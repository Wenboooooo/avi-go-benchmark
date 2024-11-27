import numpy as np
import os

# os.environ['https_proxy'] = 'http://127.0.0.1:7890'
# os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import utils
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from Q_templates import *


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
        prompt += f"Q_template: {example['Q_template']}\nSQL_template: {example['SQL_template']}\n\n"

    prompt += "请根据以上示例的格式，为以下问题生成SQL查询(直接输出语句本身，不需要任何其他内容)：\n"
    prompt += f"Q: {query}\nSQL:"

    return prompt


def SQL_RAG(query, Q_templates, benchmark_question_embeddings, retrieval_model, llm_name, connections, only_need_sql=False):
    benchmark_questions = list(Q_templates.keys())
    topk_similar_questions = find_topk_similar(retrieval_model, query, benchmark_questions, benchmark_question_embeddings, k=1)
    few_shot_data = [Q_templates[question] for question in topk_similar_questions]
    query_database = few_shot_data[0]["query_database"]
    
    prompt = generate_prompt(query, few_shot_data)
    sql = utils.LLM_generate(prompt, llm_name=llm_name, is_print=True)
    
    if not only_need_sql:
        connection = connections[query_database]
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
    
    return sql, query_database, result if not only_need_sql else None


# 测试代码
if __name__ == '__main__':
    
    model = SentenceTransformer('all-MiniLM-L6-v2')

    Q_templates = Q_templates_easy | Q_templates_complex
    benchmark_questions = list(Q_templates.keys())
    benchmark_question_embeddings = preprocess_passages(model, benchmark_questions)
    databases = ["ai_database_dev", "data_center_dev", "data_center_release"]
    connections = {database: utils.connect_to_database(database) for database in databases}


    query = "Los Angeles的航空公司有哪些？"
    ref_sql = '''SELECT supplier_name FROM supplier_details WHERE supplier_city_name = \"Los Angeles\";'''
    print("Query:", query)

    
    sql, query_database, result = SQL_RAG(query, Q_templates, benchmark_question_embeddings, model, "gpt4o", connections, only_need_sql=True)
    
    is_correct = utils.SQL_judge(ref_sql, sql, connections[query_database], True)
    print(is_correct)



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

