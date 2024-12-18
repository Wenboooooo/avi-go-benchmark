import requests
import json
import datetime


def get_ri_response(prompt):
    # 目标URL
    url = f'http://47.237.119.79:9000/chatbi/ir/prompt={prompt}'

    # 发送GET请求
    response = requests.get(url)
    data = response.text
    return data


def get_chatbi_response(prompt):
    # 目标URL
    url = f'http://47.237.119.79:9000/chatbi/response/prompt={prompt}'

    # 发送GET请求
    response = requests.get(url)
    data = response.text
    return data


if __name__ == '__main__':
    with open('synthetic_data/3-3.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    print(json_data)
    # prompt = 'Zurich的航空公司有哪些？'
    # # 意图识别
    # start_query = datetime.datetime.now()
    # start_query_format = start_query.strftime("%Y-%m-%d %H:%M:%S")
    # response = get_ri_response(prompt)
    # response = json.loads(response)
    # end_query = datetime.datetime.now()
    # end_query_format = end_query.strftime("%Y-%m-%d %H:%M:%S")
    # query_time = (end_query - start_query).total_seconds()
    #
    # print("ri done!")
    # # 数据查询
    # start_data = datetime.datetime.now()
    # start_data_format = start_data.strftime("%Y-%m-%d %H:%M:%S")
    # final_response = get_chatbi_response(response['prompt'])
    # final_response = json.loads(final_response)
    # end_data = datetime.datetime.now()
    # # 格式化输出当前时间
    # end_data_format = end_data.strftime("%Y-%m-%d %H:%M:%S")
    # data_time = (end_data - start_data).total_seconds()
    # print(final_response)
