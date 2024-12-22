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
from pyspark.sql import SparkSession
import asyncio
import httpx


# os.environ['https_proxy'] = '127.0.0.1:7890'
# os.environ['http_proxy'] = '127.0.0.1:7890'
# load_dotenv()

def connect_to_database(database_name: str):
    assert database_name in ("data_center_dev", "ai_database_dev", "data_center_release", 'spark')
    
    if database_name == 'spark':
        connection = SparkSession.builder.appName("SQL Join on Multiple Tables").getOrCreate()
        for file in ("aircraft_details.csv", "airport_fbo_details.csv", "supplier_details.csv", "zts_plane_flight.csv", "zts_plane_flight_1.csv", "zts_plane_flight_2.csv", "ai_target_jet.csv", "dc_airport.csv", "zts_plane_status.csv", "dc_aircraft.csv", "dc_aircraft_model.csv"):
                view_name = file.rsplit('.', 1)[0]
                df = connection.read.format("csv").option("header", "true").option("inferSchema", "true").load(f"database/{file}")
                df.createOrReplaceTempView(view_name)
        return connection
    
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


async def asyn_gpt4o_generate(prompt='', messages=None):
    API_URL = GPT4O_API_URL
    HEADERS = GPT4O_HEADERS
    selected_model = 'gpt-4o'
    data = {"model": selected_model, "messages": [{"role": "user", "content": prompt}]}
    if messages:
        data['messages'] = messages
    data = json.dumps(data)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, headers=HEADERS, data=data)
            response.raise_for_status()  # 检查响应状态码
            response_json = response.json()
            res = response_json['choices'][0]['message']['content']
            return res
    except Exception as e:
        print(e)
        return None


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

async def get_query_category(query):
    know_sql_queries = [
        '列出2023年每月飞行次数最多的前10个机场，以及每个机场的起降航班数量。',
        '28 De Noviembre机场在2024年各月的飞行量（起降一起），并提供2024年每个月环比上一个月的增长率。（2024年1月环比2023年12月）',
        '展示所有在17th Of September起降的航司、飞机，以及其对应的航线。',
        '总结在17th Of September的所有航班中，最常使用的前三飞机型号及其座位数（取区间）。',
        '列出在Jamestown中，使用频率最高的前5公务机及其航班数。',
        'Aalborg Airport机场的四字码是什么？',
        '查询在16 L Ranch停场的所有公务机及其注册号',
        '24/7 Jet Inc.在2024年哪个月份的飞行量最大？该月的总航班数量是多少？',
        '请提供注册号为n829dl的飞机在2024年每个月的飞行量是多少？按月份排序。',
        '比较24/7 Jet Inc.在2024年在第1季度与第2季度的总飞行量及变化百分比。',
        '从Jamestown到Niue Island，哪些机型可以直飞？',
        '24/7 Jet Inc.在2024年每个月的飞行量是多少？按从大到小排列。',
        '24/7 Jet Inc.在2024年运营的航线中，前五条最繁忙的航线及其飞行次数是多少？',
        '展示2023-2024年中，Aircraft Services Group Inc.在St.Louis Lambert International Airport的航班数量及主要使用的飞机型号。',
        'Embraer Phenom 300机型的最大飞行距离是多少？',
        'A Coruna有哪些机场？请给出机场名称和对应的四字码。',
        '2024年247 Aviation Ltd在Europe地区的每月总飞行量是多少？提供环比变化。',
        '24/7 Jet Inc.航司的总部位于哪个城市？',
        'Embraer Phenom 300的起飞重量是多少？',
        '列出2024年各月使用最多的前五个飞机型号，并提供环比变化。',
        '提供2024年每月各个国家的飞行量及其环比增长或下降百分比。',
        'Embraer Phenom 300的翼展是多少？',
        'Aalborg Airport机场的三字码是什么？',
        '列出2023年每月飞行次数最多的前10个的国家，并提供环比变化。',
        '飞机注册号为5N-CAB的飞机是哪一家公司的？',
        '24/7 Jet Inc.航司的官网链接是什么？',
        '列出注册号为9hxoa的飞机在2024年所有航班的详细信息。',
        'Los Angeles的航空公司有哪些？',
        '24/7 Jet Inc.的航班总量在2024年每个月的变化趋势如何？',
        '查询所有在17th Of September起降的航班，并找出最常用的飞机型号。',
        '在2024年24/7 Jet Inc.的前五大目的地国家（按航班量排序）有哪些？',
        '提供2024年每月24/7 Jet Inc.的各机型平均飞行小时数。',
        'Embraer Phenom 300机型的机身长度是多少？',
        'Embraer Phenom 300机型的座位数是多少？',
        '注册号为5N-CAB的飞机的制造年份是什么？',
        '列出2024年01月到07月的飞行量增幅最大？提供增幅百分比。',
        '24/7 Jet Inc.最繁忙的前10架飞机在2024年每个月的飞行量分别是多少？按注册号排序。',
        '24/7 Jet Inc.在2024年每个月飞往United States的航班数量是怎样的？请按环比变化排序。',
        '5N-CAB的制造商是谁？',
        '哪些地区的飞行量在2024年的01月到06月显著增长？',
        'Embraer Phenom 300的最大载客量是多少？',
        '分析Jamestown中，各机场的航班量，并找出排名前三的机场。',
        'Embraer Phenom 300机型在2024年每个月的飞行量变化如何？',
        'Fleet information of 24/7 Jet Inc.？',
        '列出Acadiana Regl在2024年每个月的起降航班数量，并提供环比增幅。',
        '列出2023年各月飞行量增幅最大的地区，并提供环比增幅。',
        '停场在Abraham Lincoln Capital Airport的所有航司有哪些？',
        'Aalborg Airport机场在哪个国家哪个城市？请按照先国家后城市的顺序输出。',
        '24/7 Jet Inc.在2024年每个月各机型的平均飞行小时数分别是多少？',
        '24/7 Jet Inc.在过去的2024年飞行量变化趋势如何？是否有显著的增减？',
        'Embraer Phenom 300的飞行高度范围是多少？',
        '从Xinjiang到Ili，按照飞行次数推荐排名最靠前的航司？',
        '列出2024年飞行量最多的机型及每月变化情况。'
    ]
    
    prompt = f'''请判断以下问题是哪个种类的查询，你需要在“SQL查询问题”和“开放性问题”中选择一个。如果是“SQL”查询问题，请输出“0”，如果是“开放性问题”，请输出“1”。\n\n现在已知的SQL查询问题有：\n{"\n".join(know_sql_queries)}\n\n问题：空腿调机是什么？\n种类：1\n\n问题：展示2023-2024年中，Aircraft Services Group Inc.在St.Louis Lambert International Airport的航班数量及主要使用的飞机型号。\n种类：0\n\n问题：Los Angeles的航空公司有哪些？\n种类：0\nAalborg Airport机场的四字码是什么？\n种类：0\n\n问题：除冰费是什么？在什么情况下会产生此费用？\n种类：1\n\n问题：{query}\n种类：'''
    # print(prompt)
    res = LLM_generate(prompt).strip()
    print(res)
    if '0' == res[0] or '0' == res[-1]:
        return 0
    else:
        return 1


import asyncio
from typing import AsyncGenerator

async def LLM_stream_generate(prompt: str) -> AsyncGenerator[str, None]:
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def sync_stream():
        try:
            API_URL = GPT4O_API_URL
            HEADERS = GPT4O_HEADERS
            selected_model = 'gpt-4o'
            # 发起 ChatCompletion 请求，启用流式响应
            data = {"model": selected_model, "messages": [{"role": "user", "content": prompt}], "stream": True}
            data = json.dumps(data)
            response = requests.post(API_URL, headers=HEADERS, data=data)
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        # 将内容片段放入队列
                        asyncio.run_coroutine_threadsafe(queue.put(delta['content']), loop)
        except Exception as e:
            # 将异常放入队列以便在异步生成器中处理
            asyncio.run_coroutine_threadsafe(queue.put(e), loop)
        finally:
            # 在流结束后，向队列中放入一个标记以终止异步生成器
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    # 在默认线程池中运行同步的流式生成器
    asyncio.create_task(loop.run_in_executor(None, sync_stream))

    while True:
        piece = await queue.get()
        if piece is None:
            break  # 流式输出结束
        if isinstance(piece, Exception):
            raise piece  # 重新抛出异常
        yield piece


# # 示例调用
if __name__ == "__main__":
    result = [1, 2.5, "text", [3, 4, "nested list", (5, 6)]]
    print(format_result_as_markdown(result))
