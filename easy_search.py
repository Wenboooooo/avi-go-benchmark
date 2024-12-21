import numpy as np
import os
from tabulate import tabulate

# os.environ['https_proxy'] = 'http://127.0.0.1:7890'
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from utils import *
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from Q_templates import *
import re


def preprocess_passages(model, passages, save_path=''):
    embeddings = model.encode(passages, convert_to_numpy=True)
    if save_path != '':
        np.save(save_path, embeddings)
    return embeddings


def find_topk_similar(model, query, passages, passage_embeddings, k=1):
    query_embedding = model.encode([query], convert_to_numpy=True)
    similarities = cosine_similarity(query_embedding, passage_embeddings)[0]
    topk_indices = np.argsort(similarities)[::-1][:k]
    return [passages[idx] for idx in topk_indices]


def generate_prompt(query, few_shot_data):
    prompt = "以下是一些示例问题及其对应的SQL查询：\n"

    for example in few_shot_data:
        # prompt += f"Q_template: {example['Q_template']}\nSQL_template: {example['SQL_template']}\n\n"
        prompt += f"Q: {example['Q']}\nDB: {example['DB']}\nSQL: ```sql\n{example['SQL']}\n```\n\n"

    prompt += f"Q: {query}\n"
    prompt += '''你应该严格遵守以下的输出格式:"DB: [The database you used in your SQL query]\nSQL: ```sql\nYour SQL query here]\n```"'''

    return prompt


def query_revise(retrieval_model, query, convertion_dict, macth_dict):
    slots = "aircraft_model_name: {}\naircraft_registration: {}\nairport_name: {}\ncity_name: {}"
    slot_filling_prompt = f'''Given the following text, please fill in the slots with the correct values:\n\nText: {query}\n\nSlots:\n{slots}\n\nYour should output a json with slot as key and value as value. For example:\n```json\n{{\n    "aircraft_model_name": "Boeing 737",\n    "aircraft_registration": "",\n    "airport_name": "",\n    "city_name": ""\n}}\n```\nIf you don't know the answer, please leave the value empty.\nDo not modify the table names and statement structure in the example SQL statements you provide.\n'''


    response = LLM_generate(slot_filling_prompt, is_print=True)
    json_str = re.search(r'```json\n(.*?)\n```', response, re.DOTALL).group(1)
    json_obj = json.loads(json_str)
    append_strs = []

    for k, v in list(json_obj.items()):
        if not v:
            json_obj.pop(k)
            continue
        if 'registration' in k:
            continue
        revise_v =  find_topk_similar(retrieval_model, v, macth_dict[k]['names'], macth_dict[k]['embeddings'], k=1)[0]
        print(f'{k}: {v} --> {revise_v}')
        json_obj[k] = revise_v
        identifier = 'id' if k != 'airport_name' else 'icao'
        match_value = convertion_dict[k + f'2{identifier}'][revise_v]
        json_obj[k.replace('_name', f'_{identifier}')] = match_value
        query.replace(v, revise_v)
        tmp = f'''{revise_v}对应的的{k.replace('_name', f'_{identifier}')}为"{match_value}"'''
        append_strs.append(tmp)
        # print(colored(tmp, 'red'))
        # query += '\n' + tmp

    # print(colored(query, 'red'))

    return query


def SQL_RAG(query, Q_templates, benchmark_question_embeddings, retrieval_model, llm_name, connections, convertion_dict, macth_dict, only_need_sql=False, result_markdown=False):
    num = 5
    while num > 0:
        try:
            benchmark_questions = list(Q_templates.keys())
            topk_similar_questions = find_topk_similar(retrieval_model, query, benchmark_questions, benchmark_question_embeddings, k=3)
            few_shot_data = [Q_templates[question] for question in topk_similar_questions]
            # query_database = few_shot_data[0]["query_database"]
            query = query_revise(retrieval_model, query, convertion_dict, macth_dict)

            prompt = generate_prompt(query, few_shot_data)
            # print(prompt)
            response = LLM_generate(prompt, llm_name=llm_name, is_print=False)
            # print(response)
            sql = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL).group(1).strip()
            # if not sql.startswith('SELECT'):
            #     raise Exception("Not a SELECT query")
            query_database = re.search(r'DB: (.*?)\n', response).group(1).strip()
                
            # print(query_database)
            # print(colored(sql, 'yellow'))

            # todo 需要去写一个Spark的版本
            if not only_need_sql:
                connection = connections[query_database]
                cursor = connection.cursor()
                cursor.execute(sql)
                if not result_markdown:
                    result = cursor.fetchall()
                else:
                    rows = cursor.fetchall()
                    cols = [desc[0] for desc in cursor.description]
                    result = tabulate(tabular_data=rows, headers=cols, tablefmt='pipe')
            return sql, query_database, result if not only_need_sql else None
        except Exception as e:
            print(e)
            num -= 1
            if num > 0:
                continue
            return None, None, None


# 测试代码
if __name__ == '__main__':
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    Q_templates = Q_templates_easy | Q_templates_complex
    benchmark_questions = list(Q_templates.keys())
    benchmark_question_embeddings = preprocess_passages(model, benchmark_questions)
    databases = ["ai_database_dev", "data_center_dev", "data_center_release"]
    connections = {database: connect_to_database(database) for database in databases}


    query = "Los Angeles的航空公司有哪些？"
    ref_sql = '''SELECT supplier_name FROM supplier_details WHERE supplier_city_name = \"Los Angeles\";'''
    print("Query:", query)

    
    sql, query_database, result = SQL_RAG(query, Q_templates, benchmark_question_embeddings, model, "gpt4o", connections, only_need_sql=True)
    print(sql)
    print(result)
    # is_correct = SQL_judge(ref_sql, sql, connections[query_database], True)
    # print(is_correct)



    # topk_similar_questions = find_topk_similar(model, query, benchmark_questions, benchmark_question_embeddings, k=1)
    # few_shot_data = [Q_templates[question] for question in topk_similar_questions]
    # database_to_use = few_shot_data[0]["query_database"]

    # prompt = generate_prompt(query, few_shot_data)
    # print(prompt)
    # sql = utils.gpt4o_generate(prompt, is_print=True)
    # # print(sql)
    # connection = utils.connect_to_database(database_to_use)
    # # cursor = connection.cursor()
    # # cursor.execute(sql)
    # # print(cursor.fetchall())
    # is_correct = utils.SQL_judge(ref_sql, sql, connection, True)
    # print(is_correct)

