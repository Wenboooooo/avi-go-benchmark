import uuid
import utils
from os import path as osp
import os
from flask import Flask, request, Response, jsonify
import json
import numpy as np
import pandas as pd
import time
from utils import *
from easy_search import SQL_RAG,preprocess_passages
from sentence_transformers import SentenceTransformer
import openai

app = Flask(__name__)
# 初始化检索相关内容
data_dir = "synthetic_data_clean"
retrieval_model = SentenceTransformer('all-MiniLM-L6-v2')
Q_files = os.listdir(data_dir)
Q_files = [json.load(open(osp.join(data_dir, file)[:30], 'r')) for file in Q_files]
Q_templates = {item['Q']: item for sublist in Q_files for item in sublist}
benchmark_questions = list(Q_templates.keys())

if osp.exists('benchmark_question_embeddings.npy'):
    benchmark_question_embeddings = np.load('benchmark_question_embeddings.npy')
else:
    benchmark_question_embeddings = preprocess_passages(retrieval_model, benchmark_questions, save_path='benchmark_question_embeddings.npy')

# 初始化数据库相关内容
databases = ["ai_database_dev", "data_center_dev", "data_center_release", 'spark']
connections = {database: utils.connect_to_database(database) for database in databases}

# 字段匹配相关
convertion_file = {_[:-4] : pd.read_csv(osp.join("meta_data", _)) for _ in os.listdir("meta_data") if _.endswith(".csv")}
convertion_dict = {_ : df.set_index(df.columns[0])[df.columns[1]].to_dict() for _, df in convertion_file.items()}

match_file = {_.split('2')[0] : pd.read_csv(osp.join("meta_data", _)) for _ in os.listdir("meta_data") if _.endswith(".csv")}
match_dict = {_ : {'names': tuple(df[df.columns[0]].tolist())} for _, df in match_file.items()}

for k, v in match_dict.items():
    if osp.exists(f'{k}_embeddings.npy'):
        match_dict[k]['embeddings'] = np.load(f'{k}_embeddings.npy')
    else:
        match_dict[k]['embeddings'] = preprocess_passages(retrieval_model, v['names'], save_path=f'{k}_embeddings.npy')



async def inner_generate_BaseDO_response(prompt, model, messages):

    category_task = asyncio.create_task(get_query_category(prompt))
    llm_task = asyncio.create_task(asyn_gpt4o_generate(messages=messages))
    sql_task = asyncio.create_task(SQL_RAG(
        prompt, Q_templates, benchmark_question_embeddings, retrieval_model, 
        'gpt4o', connections, convertion_dict, match_dict, 
        only_need_sql=False, result_markdown=True, spark_query=True
    ))

    category = await category_task

    if category == 1:
        # 使用 LLM_generate 的结果
        try:
            result =  await llm_task
        except asyncio.CancelledError:
            print("LLM_generate 任务失败。")
        # 取消 SQL_RAG 任务
        sql_task.cancel()
        print("SQL_RAG 任务已取消。")
        try:
            await sql_task
        except asyncio.CancelledError:
            pass
            # print("SQL_RAG 任务已取消。")
        return result

    elif category == 0:
        # 使用 SQL_RAG 的结果
        try:
            sql, query_database, result = await sql_task
            print(sql)
        except asyncio.CancelledError:
            print("SQL_RAG 任务失败。")
            sql, query_database, result = None, None, None
        # 取消 LLM_generate 任务
        llm_task.cancel()
        print("LLM_generate 任务已取消。")
        try:
            await llm_task
        except asyncio.CancelledError:
            pass
        return result


# 模拟生成内容的函数
def generate_response(prompt, model):
    """
    根据用户输入生成响应内容（模拟 AI 返回的内容）。
    """
    res = LLM_generate(prompt)
    return res

# todo 三线程匹配
def generate_BaseDO_response(prompt, model, messages):
    result =  asyncio.run(inner_generate_BaseDO_response(prompt, model, messages))
    return result


# 流式输出生成器（改进后的实现）
@app.route('/v1/chat/completions', methods=['POST'])
def generate_stream_response():
    print(colored(request.json, 'green'))
    data = request.json
    messages = data.get("messages", [])
    model = data.get("model", "gpt-4o")
    stream = data.get("stream", True)

    if not messages:
        return jsonify({"error": "messages 参数缺失"}), 400

    # 获取用户输入内容
    prompt = messages[-1].get("content", "")

    return_obj = {
            "id": "42",
            "object": "chat.completion.chunk",
            "created": "42",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": None},
                    "finish_reason": None
                }
            ],
            "system_fingerprint": "42"
    }

    category = get_query_category(prompt)
    if category == 1:
        print(colored("Category: LLM_generate", 'red'))
        if stream:
            def generate():
                API_URL = GPT4O_API_URL
                HEADERS = GPT4O_HEADERS
                selected_model = 'gpt-4o'
                data = {"model": selected_model, "messages": messages, "stream": True}
                data = json.dumps(data)
                response = requests.post(API_URL, headers=HEADERS, data=data, stream=True)

                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line == 'data: [DONE]':  # Stream completion check
                                yield 'data: [DONE]'
                            try:
                                line_data = json.loads(decoded_line[6:])
                                # print(line_data)
                                data = line_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                if data:
                                    # print(data)
                                    return_obj['choices'][0]['delta']['content'] = data
                                    yield 'data: ' + json.dumps(return_obj) + '\n\n'
                            except Exception as e:
                                print(e)
            return Response(generate(), mimetype='text/event-stream')
    else:
        print(colored("Category: SQL_RAG", 'red'))
        sql, query_database, result = SQL_RAG(
            prompt, Q_templates, benchmark_question_embeddings, retrieval_model, 
            'gpt4o', connections, convertion_dict, match_dict, 
            only_need_sql=False, result_markdown=True, spark_query=True
        )
        print(sql)
        print(result)
        return_obj['choices'][0]['delta']['content'] = result
        return_obj['choices'][0]['finish_reason'] = "stop"
        def generate():
            yield 'data: ' + json.dumps(return_obj) + '\n\n'
            yield 'data: [DONE]'
        return Response(generate(), mimetype='text/event-stream')



# 接口 /v1/chat/completions/models
@app.route('/v1/models', methods=['GET'])
def get_models():
    """
    返回支持的模型列表。
    """
    models = [
        {"id": "gpt-4", "object": "model", "created": 1677610602, "owned_by": "openai"},
        {"id": "gpt-3.5-turbo", "object": "model", "created": 1677610703, "owned_by": "openai"}
    ]
    return jsonify({"data": models, "object": "list"})

# 启动服务
if __name__ == "__main__":
    app.run(debug=True, port=1234)