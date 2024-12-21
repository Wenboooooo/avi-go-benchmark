from dotenv import load_dotenv
import pymysql
import requests
import json
import os
from termcolor import colored
import base64
import re
import pandas as pd
import datetime

# os.environ['https_proxy'] = '127.0.0.1:7890'
# os.environ['http_proxy'] = '127.0.0.1:7890'
# load_dotenv()

def connect_to_database(database_name: str):
    assert database_name in ("data_center_dev", "ai_database_dev", "data_center_release")
    match database_name:
        case "data_center_dev":
            host , user, password = 'rm-uf6k55f9394p93af8.rwlb.rds.aliyuncs.com', 'ai_data', '5a@12ujdaldj8s'
        case "ai_database_dev":
            host , user, password = 'rm-t4n3p0r28isdqdgvx.mysql.singapore.rds.aliyuncs.com', 'nlp_dev_read', 'nlp*12345'
            # host , user, password = 'rm-t4nao9vgc59g20e48.mysql.singapore.rds.aliyuncs.com', 'nlp_dev', 'nlp*12345'
        case "data_center_release":
            host , user, password = 'rm-uf6k55f9394p93af8.rwlb.rds.aliyuncs.com', 'ai_data', '5a@12ujdaldj8s'
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database_name,  # 数据库名称
        port=3306,
        connect_timeout=300  # 设置连接超时时间为30秒
    )
    return connection


GPT4O_API_KEY = 'sk-proj-Rl41N05dYzhdjkHneWI2T3BlbkFJXf1SmQ7Nth4wHBCgzHjO'
GPT4O_API_URL = "https://api.openai.com/v1/chat/completions"

# KIMI
KIMI_API_KEY = 'sk-PlAAAH2Jwx7E3m9Rb8DCAx3tIZ2fqLutOytxlu0zy4aB6F7Y'
KIMI_API_URL = "https://api.moonshot.cn/v1"

# claude
claude_API_KEY = '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'
claude_API_URL = "https://api.aiproxy.io/v1/messages"

# QWEN
QWEN_API_KEY = 'your-kimi-api-key'
QWEN_API_URL = "https://api.qwen.com/v1/chat/completions"

GPT4O_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GPT4O_API_KEY}"
}

KIMI_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {KIMI_API_KEY}"
}

QWEN_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {QWEN_API_KEY}"
}

claude_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {claude_API_KEY}"
}

# TODO: 改成OpenAI风格的generate函数，注意历史记录
def LLM_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False, llm_name='gpt4o'):
    API_KEY = ""
    API_URL = ""
    HEADERS = {}
    selected_model = ''
    if llm_name == 'gpt4o':
        API_URL = GPT4O_API_URL
        HEADERS = GPT4O_HEADERS
        selected_model = 'gpt-4o'
    elif llm_name == 'kimi':
        API_URL = KIMI_API_URL
        HEADERS = KIMI_HEADERS
        selected_model = 'kimi'
    elif llm_name == 'qwen':
        API_URL = QWEN_API_URL
        HEADERS = QWEN_HEADERS
        selected_model = 'qwen'
    elif llm_name == 'claude':
        API_URL = claude_API_URL
        HEADERS = claude_HEADERS
        selected_model = 'claude'
    else:
        API_URL = GPT4O_API_URL
        HEADERS = GPT4O_HEADERS
        selected_model = 'gpt-4o'
    num = 10
    res = ""
    messages = [{"role": "user", "content": text}]
    while num > 0 and len(res) == 0:
        try:
            content = [{"type": "text", "text": text}]
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})

            data = {"model": selected_model, "messages": [{"role": "user", "content": content}]}
            data = json.dumps(data)
            response = requests.post(API_URL, headers=HEADERS, data=data)
            response_json = response.json()
            res = response_json['choices'][0]['message']['content']
        except Exception as e:
            print(e)
            num -= 1
    if is_print:
        print(colored(res, 'yellow'))
    return res
    # if llm_name == 'gpt4o':
    #     return gpt4o_generate(text, image_paths, temp, presence_penalty, is_print)
    # elif llm_name == 'kimi':
    #     return kimi_generate(text, image_paths, temp, presence_penalty, is_print)
    # elif llm_name == 'qwen':
    #     return qwen_generate(text, image_paths, temp, presence_penalty, is_print)
    # elif llm_name == 'claude':
    #     return claude_generate(text, image_paths, temp, presence_penalty, is_print)
    # else:
    #     return gpt4o_generate(text, image_paths, temp, presence_penalty, is_print)


# def gpt4o_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
#     # if is_print:
#     #     print(colored(text, 'green'))
#     num = 10
#     res = ""
#     messages = [{"role": "user", "content": text}]
#     while num > 0 and len(res)==0:
#         try:
#             content = [{"type": "text", "text": text}]
#             for image_path in image_paths:
#                 with open(image_path, "rb") as image_file:
#                     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
#                 content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
#
#             data = {"model": "gpt-4o", "messages": [{"role": "user", "content": content}]}
#             data = json.dumps(data)
#             response = requests.post(GPT4O_API_URL, headers=GPT4O_HEADERS, data=data)
#             response_json = response.json()
#             res = response_json['choices'][0]['message']['content']
#         except Exception as e:
#             print(e)
#             num -= 1
#     if is_print:
#         print(colored(res, 'yellow'))
#     return res
#
#
# def kimi_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
#     if is_print:
#         print(colored(text, 'green'))
#     num = 10
#     res = ""
#     messages = [{"role": "user", "content": text}]
#     while num > 0 and len(res) == 0:
#         try:
#             content = [{"type": "text", "text": text}]
#             for image_path in image_paths:
#                 with open(image_path, "rb") as image_file:
#                     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
#                 content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
#
#             data = {"model": "kimi-model", "messages": [{"role": "user", "content": content}]}
#             data = json.dumps(data)
#             response = requests.post(KIMI_API_URL, headers=KIMI_HEADERS, data=data)
#             response_json = response.json()
#             res = response_json['choices'][0]['message']['content']
#         except Exception as e:
#             print(e)
#             num -= 1
#     if is_print:
#         print(colored(res, 'yellow'))
#     return res
#
#
# def qwen_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
#     if is_print:
#         print(colored(text, 'green'))
#
#     # 尝试次数
#     num = 10
#     res = ""
#     messages = [{"role": "user", "content": text}]
#
#     while num > 0 and len(res) == 0:
#         try:
#             content = text
#             if image_paths:  # 如果有图片路径，则处理图片并添加到content中
#                 content = {"text": text, "images": []}
#                 for image_path in image_paths:
#                     with open(image_path, "rb") as image_file:
#                         base64_image = base64.b64encode(image_file.read()).decode('utf-8')
#                     content["images"].append({"url": f"data:image/png;base64,{base64_image}"})
#
#             data = {"model": "qwen", "messages": [content]}
#             data = json.dumps(data)
#             response = requests.post(QWEN_API_URL, headers=QWEN_HEADERS, data=data)
#             response.raise_for_status()  # 检查请求是否成功
#             response_json = response.json()
#             res = response_json['choices'][0]['message']['content']
#         except Exception as e:
#             print(f"Error occurred: {e}")
#             num -= 1
#     if is_print:
#         print(colored(res, 'yellow'))
#     return res

def LLM_judge(question, ref_answer, actual_response, is_print=False, llm_type='gpt4o'):
    num = 10
    prompt = f"Question: {question}\nGround Truth: {ref_answer}\nAnswer to be checked:\n{actual_response}\n\nPlease determine if this answer is correct or not based on Ground Truth.\nIn numerical measurements such as length, a certain degree of error is permissible.\nYour output should strictly follow the format: \"Thought: [Your Thought]\nJudgement: [Yes/No]\"."
    while num > 0:
        response = LLM_generate(prompt, llm_name=llm_type)
        result = response.split("Judgement: ")[-1].lower().strip()
        if result in ('yes', 'no'):
            break
        num -= 1
    else:
        result = "Judgement failed"
    if is_print:
        print(colored(prompt, 'green'))
        print(colored(response, 'yellow'))
        print(colored(result, 'red'))
    return result

def remove_whitespace_and_newlines(input_string: str) -> str:
    """
    移除字符串中所有的空格和换行符。

    参数:
        input_string (str): 输入的字符串

    返回:
        str: 处理后的紧凑字符串
    """
    clean_text = re.sub(r'\s+', ' ', input_string).lower()
    return clean_text

def SQL_judge(ref_sql, actual_sql, connection, actual_result=None, is_print=False):
    try:
        if (not actual_sql) and (not actual_result):
            return 'no'
        num = 10
        cursor = connection.cursor()
        ref_sql, actual_sql = ref_sql.strip(), actual_sql.strip()
        # ref_sql = remove_whitespace_and_newlines(ref_sql)
        # actual_sql = remove_whitespace_and_newlines(actual_sql)
        if remove_whitespace_and_newlines(ref_sql) == remove_whitespace_and_newlines(actual_sql):
            if is_print:
                print(colored("same sql", 'red'))
            return 'yes'
        else:
            if is_print:
                print(colored(ref_sql, 'green'))
                print(colored(actual_sql, 'yellow'))
            cursor.execute(ref_sql)
            ref_result = cursor.fetchall()
            if not actual_result:
                cursor.execute(actual_sql)
                actual_result = cursor.fetchall()
            if is_print:
                print(colored(ref_result, 'green'))
                print(colored(actual_result, 'yellow'))
                print(colored(ref_result == actual_result, 'red'))
            if ref_result == actual_result:
                return 'yes'
            else:
                return 'no'
                # return LLM_judge("请检查Answer中是否包含Ground Truth中的所有信息", str(ref_result), str(actual_result), is_print=is_print)
    except Exception as e:
        print(e)
        return 'no'


def LLM_score(question, ref_answer, actual_response, is_print=False):
    num = 10
    prompt = f"Question: {question}\nGround Truth: {ref_answer}\nAnswer to be checked:\n{actual_response}\n\nPlease score this answer from 0 to 10 based on Ground Truth. You should answer only with a number."
    while num > 0:
        result = LLM_generate(prompt).lower()
        if result.isdigit():
            break
        num -= 1
    else:
        result = "Scoring failed"
    if is_print:
        print(colored(prompt, 'green'))
        print(colored(result, 'red'))
    return result



def chatbi_generate(prompt):
    def get_ri_response(prompt):
        url = f'http://127.0.0.1:9000/chatbi/ir/prompt={prompt}'
        response = requests.get(url)
        data = response.text
        return data
    
    num = 5
    while num > 0:
        try:
            response = get_ri_response(prompt)
            response = json.loads(response)
            prompt = (response['prompt'])
            url = f'http://127.0.0.1:9000/chatbi/response/prompt={prompt}'
            response = requests.get(url)
            data = response.text
            print(data)
            data = json.loads(data)
            sql =  data['markdown_sql']
            sql = re.search(r'```sql\n(.*?)\n```', sql, re.DOTALL).group(1).strip()
            return sql, data['data']
        except Exception as e:
            print(e)
            num -= 1
            continue
       


import json
import requests
from termcolor import colored

def avibot_pro_generate(text, image_paths=None, temp=None, presence_penalty=None, is_print=False):
    
    
    url = 'http://47.237.119.79:8300/avi-go-chatbotpro/benchmark_test'
    
   
    if is_print:
        print(colored(text, 'green'))

   
    num = 10
    res = ""

   
    headers = {
        "Content-Type": "application/json"
    }

    # 数据
    data = {
        "question": text
    }

 
    while num > 0 and len(res) == 0:
        try:
           
            data_json = json.dumps(data)

        
            response = requests.post(url, headers=headers, data=data_json)

            # 如果请求成功
            if response.status_code == 200:
                response_json = response.json()
                res = response_json.get("result", "")
            else:
                num -= 1
        except Exception as e:
            num -= 1

    # 打印响应结果
    if is_print and res:
        print(colored(res, 'yellow'))

    # 返回响应结果
    return res

def format_result_as_markdown(result):
    def format_list(lst):
        return '\n'.join(format_item(item) for item in lst)

    def format_item(item):
        if isinstance(item, (int, float)):
            return f'- {item}'
        elif isinstance(item, str):
            return f'- {item}'
        elif isinstance(item, (list, tuple)):
            return '\n' + format_list(item)
        else:
            return 'Unsupported data type'

    markdown_text = ''
    if isinstance(result, (int, float)):
        markdown_text = f'{result}'
    elif isinstance(result, str):
        markdown_text = f'"{result}"'
    elif isinstance(result, (list, tuple)):
        markdown_text = format_list(result)
    else:
        markdown_text = 'Unsupported data type'

    return f'```\n{markdown_text}\n```'


def parse_sql_result_to_dataframe(sql, result):
    """
    解析 SQL 查询结果，将其尽可能转换为 Pandas DataFrame，并提取 SQL 查询中的表名。

    参数:
    sql (str): SQL 查询语句。
    result: 从 SQL 查询返回的结果，可以是 int、float、str、list、tuple 等任意格式。

    返回:
    tuple: (pd.DataFrame, list)，其中包含：
           - 转换后的 Pandas 数据框。
           - 从 SQL 中提取的表名列表。
    """
    # 提取表名的正则表达式
    table_name_pattern = r"FROM\s+([a-zA-Z_][a-zA-Z0-9_\.]*)|JOIN\s+([a-zA-Z_][a-zA-Z0-9_\.]*)"
    matches = re.findall(table_name_pattern, sql, re.IGNORECASE)

    # 提取表名（处理正则结果）
    table_names = [match[0] if match[0] else match[1] for match in matches]

    # 解析 result 数据为 DataFrame
    if isinstance(result, (int, float)):
        df = pd.DataFrame({"value": [result]})
    elif isinstance(result, str):
        df = pd.DataFrame({"value": [result]})
    elif isinstance(result, list):
        if all(isinstance(item, (list, tuple)) for item in result):
            df = pd.DataFrame(result)
        else:
            df = pd.DataFrame({"value": result})
    elif isinstance(result, tuple):
        df = pd.DataFrame([result])
    elif isinstance(result, dict):
        df = pd.DataFrame([result])
    else:
        try:
            df = pd.DataFrame(result)
        except Exception as e:
            raise ValueError(f"无法解析 result 数据：{e}")

    return df, table_names

# # 示例调用
if __name__ == "__main__":
    result = [1, 2.5, "text", [3, 4, "nested list", (5, 6)]]
    print(format_result_as_markdown(result))
