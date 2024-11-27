import numpy as np
import os
import json
import time
import utils
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# 初始化嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')  # 选择一个轻量级的预训练模型


def find_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                json_files.append(full_path)
    return json_files

# 预处理所有段落并存储嵌入
def preprocess_passages(passages, save_path=''):
    """
    将所有段落转为嵌入并存储
    :param passages: List[str], 段落列表
    :return: np.ndarray, 段落嵌入
    """
    embeddings = model.encode(passages, convert_to_numpy=True)
    if save_path != '':
        np.save(save_path, embeddings)
    return embeddings

# 查询处理函数
# def find_most_similar(query, passages, passage_embeddings):
#     """
#     根据查询找到最匹配的段落
#     :param query: str, 查询内容
#     :param passages: List[str], 段落列表
#     :param passage_embeddings: np.ndarray, 已存储的段落嵌入
#     :return: str, 最匹配的段落
#     """
#     query_embedding = model.encode([query], convert_to_numpy=True)
#     similarities = cosine_similarity(query_embedding, passage_embeddings)[0]
#     most_similar_idx = np.argmax(similarities)
#     return passages[most_similar_idx]

def find_most_similar(query, passages, passage_embeddings, origin_data, n=5, ret_type='Q'):
    """
    根据查询找到最匹配的n个段落
    :param query: str, 查询内容
    :param passages: List[str], 段落列表
    :param passage_embeddings: np.ndarray, 已存储的段落嵌入
    :param n: int, 返回最相似的n个段落
    :return: List[str], 最匹配的n个段落
    """
    # 假设model是一个预训练的模型，用于将文本编码为嵌入
    query_embedding = model.encode([query], convert_to_numpy=True)
    similarities = cosine_similarity(query_embedding, passage_embeddings)[0]

    # 获取相似度分数的前n个最相似的索引
    most_similar_indices = np.argsort(similarities)[::-1][:n]

    # 根据索引获取最相似的段落
    most_similar_passages = [passages[idx] for idx in most_similar_indices]
    ret = []
    if ret_type == 'Q':
        return most_similar_passages
    elif ret_type == 'SQL':
        for sp in most_similar_passages:
            ret.append(find_sql_by_Q(origin_data, sp))
        return ret
    elif ret_type == 'dict':
        for sp in most_similar_passages:
            ret.append(find_dict_by_Q(origin_data, sp))
        return ret
    else:
        return most_similar_passages

def get_easy_question_passages():
    origin_data = []
    passages = []
    json_files = find_json_files('synthetic_data')
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for datum in data:
                origin_data.append(datum)
                passages.append(datum['Q'])
    return passages, origin_data

def find_sql_by_Q(origin_data, Q):
    for datum in origin_data:
        if datum['Q'] == Q:
            return datum['SQL']

def find_dict_by_Q(origin_data, Q):
    for datum in origin_data:
        if datum['Q'] == Q:
            return datum

def generate_prompt(query, few_shot_data):
    prompt = "以下是一些示例问题及其对应的SQL查询：\n\n"

    # 遍历few-shot示例数据，添加到Prompt中
    for example in few_shot_data:
        prompt += f"Q: {example['Q']}\nSQL: {example['SQL']}\n\n"

    # 添加用户的查询
    prompt += "请根据以上示例的格式，为以下问题生成SQL查询(直接输出语句本身，不需要任何其他内容)：\n\n"
    prompt += f"Q: {query}\nSQL:"

    return prompt

def easy_RAG_LLM(query, passages, passage_embeddings, origin_data, llm_type='gpt4o'):
    connection = utils.connect_to_database("ai_database_dev")
    cursor = connection.cursor()
    connection1 = utils.connect_to_database("data_center_dev")
    cursor1 = connection1.cursor()
    connection2 = utils.connect_to_database("data_center_release")
    cursor2 = connection2.cursor()
    few_shot_data = find_most_similar(query, passages, passage_embeddings, origin_data, n=3, ret_type='dict')
    prompt = generate_prompt(query, few_shot_data)
    A = ''
    if llm_type == 'gpt4o':
        sql = utils.gpt4o_generate(prompt, is_print=False)
        try:
            cursor.execute(sql)
            A = cursor.fetchall()
            print(cursor.fetchall())
        except:
            try:
                cursor1.execute(sql)
                A = cursor1.fetchall()
            except:
                try:
                    cursor2.execute(sql)
                    A = cursor2.fetchall()
                except:
                    return ''
        return A
    elif llm_type == 'kimi':
        sql = utils.kimi_generate(prompt, is_print=False)
        try:
            cursor.execute(sql)
            A = cursor.fetchall()
            print(cursor.fetchall())
        except:
            try:
                cursor1.execute(sql)
                A = cursor1.fetchall()
            except:
                try:
                    cursor2.execute(sql)
                    A = cursor2.fetchall()
                except:
                    return ''
        return A
    elif llm_type == 'qwen':
        sql = utils.qwen_generate(prompt, is_print=False)
        try:
            cursor.execute(sql)
            A = cursor.fetchall()
            print(cursor.fetchall())
        except:
            try:
                cursor1.execute(sql)
                A = cursor1.fetchall()
            except:
                try:
                    cursor2.execute(sql)
                    A = cursor2.fetchall()
                except:
                    return ''
        return A
    else:
        return A



# 示例段落列表
# passages, origin_data = get_easy_question_passages()
# passages = passages

# 预处理段落并存储嵌入
# passage_embeddings = preprocess_passages(passages, save_path='passage_embeddings.npy')
# passage_embeddings = np.load('passage_embeddings.npy')
#
# # 查询
# query = "查询在上海虹桥停场的所有公务机及其注册号"
# print("Query:", query)
#
# # 找到最匹配的段落
# few_shot_data = find_most_similar(query, passages, passage_embeddings, origin_data, n=3, ret_type='dict')
#
# prompt = generate_prompt(query, few_shot_data)
# print(prompt)
# sql = utils.gpt4o_generate(prompt, is_print=True)
# connection = utils.connect_to_database("ai_database_dev")
# cursor = connection.cursor()
# cursor.execute(sql)
# print(cursor.fetchall())