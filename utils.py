from dotenv import load_dotenv
import pymysql
import requests
import json
import os
from termcolor import colored
import base64

# os.environ['https_proxy'] = '127.0.0.1:7890'
# os.environ['http_proxy'] = '127.0.0.1:7890'
# load_dotenv()

def connect_to_database(database_name: str):
    assert database_name in ("data_center_dev", "ai_database_dev", "data_center_release")
    match database_name:
        case "data_center_dev":
            host , user, password = 'rm-uf6k55f9394p93af8.rwlb.rds.aliyuncs.com', 'ai_data', '5a@12ujdaldj8s'
        case "ai_database_dev":
            host , user, password = 'rm-t4nao9vgc59g20e48.mysql.singapore.rds.aliyuncs.com', 'nlp_dev', 'nlp*12345'
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


API_KEY = 'sk-proj-Rl41N05dYzhdjkHneWI2T3BlbkFJXf1SmQ7Nth4wHBCgzHjO'
API_URL = "https://api.openai.com/v1/chat/completions"

# KIMI
KIMI_API_KEY = 'sk-PlAAAH2Jwx7E3m9Rb8DCAx3tIZ2fqLutOytxlu0zy4aB6F7Y'
KIMI_API_URL = "https://api.moonshot.cn/v1"

# claude
claude_API_KEY = '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'
claude_API_URL = "https://api.aiproxy.io/v1/messages"

# QWEN
QWEN_API_KEY = 'your-kimi-api-key'
QWEN_API_URL = "https://api.qwen.com/v1/chat/completions"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
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

# TODO: 将后面所有的generate函数重构整合到一个函数中，根据llm_name选择调用哪个模型。llm_name是具体的模型名称，而不是模型种类。比如gpt-4o, 而不是gpt。下面的gpt4o_generate、kimi_generate、qwen_generate、claude_generate等之后都要删掉。
def LLM_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False, llm_name='gpt4o'):
    if llm_name == 'gpt4o':
        return gpt4o_generate(text, image_paths, temp, presence_penalty, is_print)
    elif llm_name == 'kimi':
        return kimi_generate(text, image_paths, temp, presence_penalty, is_print)
    elif llm_name == 'qwen':
        return qwen_generate(text, image_paths, temp, presence_penalty, is_print)
    elif llm_name == 'claude':
        return claude_generate(text, image_paths, temp, presence_penalty, is_print)
    else:
        return gpt4o_generate(text, image_paths, temp, presence_penalty, is_print)


def gpt4o_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
    # if is_print:
    #     print(colored(text, 'green'))
    num = 10
    res = ""
    messages = [{"role": "user", "content": text}]
    while num > 0 and len(res)==0:
        try:
            content = [{"type": "text", "text": text}]
            for image_path in image_paths:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}})
            
            data = {"model": "gpt-4o", "messages": [{"role": "user", "content": content}]}
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


def kimi_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
    if is_print:
        print(colored(text, 'green'))
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

            data = {"model": "kimi-model", "messages": [{"role": "user", "content": content}]}
            data = json.dumps(data)
            response = requests.post(KIMI_API_URL, headers=KIMI_HEADERS, data=data)
            response_json = response.json()
            res = response_json['choices'][0]['message']['content']
        except Exception as e:
            print(e)
            num -= 1
    if is_print:
        print(colored(res, 'yellow'))
    return res


def qwen_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
    if is_print:
        print(colored(text, 'green'))

    # 尝试次数
    num = 10
    res = ""
    messages = [{"role": "user", "content": text}]

    while num > 0 and len(res) == 0:
        try:
            content = text
            if image_paths:  # 如果有图片路径，则处理图片并添加到content中
                content = {"text": text, "images": []}
                for image_path in image_paths:
                    with open(image_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                    content["images"].append({"url": f"data:image/png;base64,{base64_image}"})

            data = {"model": "qwen", "messages": [content]}
            data = json.dumps(data)
            response = requests.post(QWEN_API_URL, headers=QWEN_HEADERS, data=data)
            response.raise_for_status()  # 检查请求是否成功
            response_json = response.json()
            res = response_json['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error occurred: {e}")
            num -= 1
    if is_print:
        print(colored(res, 'yellow'))
    return res

def LLM_judge(question, ref_answer, actual_response, is_print=False, llm_type='gpt4o'):
    num = 10
    prompt = f"Question: {question}\nGround Truth: {ref_answer}\nAnswer to be checked:\n{actual_response}\n\nPlease determine if this answer is correct or not based on Ground Truth.\nIn numerical measurements such as length, a certain degree of error is permissible.\nYour output should strictly follow the format: \"Thought: [Your Thought]\nJudgement: [Yes/No]\"."
    while num > 0:
        if llm_type == 'gpt4o':
            response = gpt4o_generate(prompt)
        elif llm_type == 'kimi':
            response = kimi_generate(prompt)
        elif llm_type == 'qwen':
            response = qwen_generate(prompt)
        elif llm_type == 'claude':
            response = claude_generate(prompt)
        else:
            response = gpt4o_generate(prompt)
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

def SQL_judge(ref_sql, actual_sql, connection, actual_result=None, is_print=False):
    if (not actual_sql) and (not actual_result):
        return 'no'
    num = 10
    cursor = connection.cursor()
    ref_sql,  actual_sql = ref_sql.strip(), actual_sql.strip()
    if ref_sql == actual_sql:
        if is_print:
            print(colored("same sql", 'red'))
        return 'yes'
    else:
        if is_print:
            print(colored(ref_sql, 'green'))
            print(colored(actual_sql, 'yellow'))
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



def claude_generate(text, image_paths=[], temp=None, max_tokens_to_sample=None, is_print=False):
    if is_print:
        print(colored(text, 'green'))

    # 尝试次数
    num = 10
    res = ""
    messages = [
        {"role": "human", "content": text}
    ]

    while num > 0 and len(res) == 0:
        try:
            data = {
                "prompt": "\n".join([msg["content"] for msg in messages]),
                "model": "claude-2",
                "max_tokens_to_sample": max_tokens_to_sample or 300,
                "temperature": temp or 0.7
            }

            if image_paths:  # 如果有图片路径，Claude API当前版本不支持直接发送图片，这里仅保留逻辑
                print("Warning: Claude API does not support sending images directly.")

            data = json.dumps(data)
            response = requests.post(claude_API_URL, headers=claude_HEADERS, data=data)
            response.raise_for_status()  # 检查请求是否成功
            response_json = response.json()
            res = response_json['completion']
        except Exception as e:
            print(f"Error occurred: {e}")
            num -= 1

    if is_print:
        print(colored(res, 'yellow'))

    return res

def LLM_score(question, ref_answer, actual_response, is_print=False):
    num = 10
    prompt = f"Question: {question}\nGround Truth: {ref_answer}\nAnswer to be checked:\n{actual_response}\n\nPlease score this answer from 0 to 10 based on Ground Truth. You should answer only with a number."
    while num > 0:
        result = gpt4o_generate(prompt).lower()
        if result.isdigit():
            break
        num -= 1
    else:
        result = "Scoring failed"
    if is_print:
        print(colored(prompt, 'green'))
        print(colored(result, 'red'))
    return result

# actual_answer = gpt4o_generate("Waht's OpenAI?", is_print=True)