from dotenv import load_dotenv
import pymysql
import requests
import json
import os
from termcolor import colored
import base64

os.environ['https_proxy'] = '127.0.0.1:7890'
os.environ['http_proxy'] = '127.0.0.1:7890'
load_dotenv()

def connect_to_database(database_name: str):
    assert database_name in ("data_center_dev", "ai_database_dev")
    match database_name:
        case "data_center_dev":
            host , user, password = 'rm-uf6k55f9394p93af8.rwlb.rds.aliyuncs.com', 'ai_data', '5a@12ujdaldj8s'
        case "ai_database_dev":
            host , user, password = 'rm-t4nao9vgc59g20e48.mysql.singapore.rds.aliyuncs.com', 'nlp_dev', 'nlp*12345'
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

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def gpt4o_generate(text, image_paths=[], temp=None, presence_penalty=None, is_print=False):
    if is_print:
        print(colored(text, 'green'))
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

def LLM_judge(question, ref_answer, actual_response, is_print=False):
    num = 10
    prompt = f"Question: {question}\nGround Truth: {ref_answer}\nAnswer to be checked:\n{actual_response}\n\nPlease determine if this answer is correct or not based on Ground Truth.\nIn numerical measurements such as length, a certain degree of error is permissible.\nYour output should strictly follow the format: \"Thought: [Your Thought]\nJudgement: [Yes/No]\"."
    while num > 0:
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