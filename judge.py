import os
import json
import random
import numpy as np
from os import path as osp
from concurrent.futures import ThreadPoolExecutor, as_completed
import utils
from utils import *
import easy_search
from sentence_transformers import SentenceTransformer
from Q_templates import *
import re
import pandas as pd
import time

random_seed = 44
sample_size = 50
random.seed(random_seed)

data_dir = "synthetic_data"
# data_dir = "ChatBI推荐问题"
# output_dir = "SQL_RAG_judge_result"
output_dir = "Test_SQL_RAG_judge_result"
output_dir = "debug"
# output_dir = "chatBI_judge_result"
# output_dir = "gpt4o_judge_result"
# output_dir = "Avibotpro_judge_result"



test_files = os.listdir(data_dir)
test_files = [file for file in test_files if not file.startswith("1")]
# test_files = ["1-5.json"]
# test_files = ["1-8.json", "1-9.json", "1-14.json", "1-20.json", "1-22.json", "1-25.json"]
# test_files = ['1-10.json', '1-17.json', '1-4.json', '1-8.json', '1-21.json', '1-20.json']
# test_files = ['1-4.json', '1-5.json', '1-6.json', '1-7.json', '1-8.json', '1-9.json', '1-10.json', '1-12.json', '1-14.json', '1-16.json', '1-17.json', '1-18.json', '1-19.json', '1-22.json', '1-25.json']
print(test_files)


llm_name = 'gpt4o'
retrieval_model = SentenceTransformer('all-MiniLM-L6-v2')
Q_files = os.listdir(data_dir)
Q_files = [json.load(open(osp.join(data_dir, file)[:30], 'r')) for file in Q_files]
Q_templates = {item['Q']: item for sublist in Q_files for item in sublist}

# Q_templates = Q_templates_easy | Q_templates_complex
# benchmark_questions = [re.sub(r'\{[^}]*\}', '', _) for _ in list(Q_templates.keys())]
benchmark_questions = list(Q_templates.keys())
if osp.exists('benchmark_question_embeddings.npy'):
    benchmark_question_embeddings = np.load('benchmark_question_embeddings.npy')
else:
    benchmark_question_embeddings = easy_search.preprocess_passages(retrieval_model, benchmark_questions, save_path='benchmark_question_embeddings.npy')
databases = ["ai_database_dev", "data_center_dev", "data_center_release"]
connections = {database: utils.connect_to_database(database) for database in databases}

convertion_file = {_[:-4] : pd.read_csv(osp.join("meta_data", _)) for _ in os.listdir("meta_data") if _.endswith(".csv")}
convertion_dict = {_ : df.set_index(df.columns[0])[df.columns[1]].to_dict() for _, df in convertion_file.items()}

macth_file = {_.split('2')[0] : pd.read_csv(osp.join("meta_data", _)) for _ in os.listdir("meta_data") if _.endswith(".csv")}
macth_dict = {_ : {'names': tuple(df[df.columns[0]].tolist())} for _, df in macth_file.items()}

for k, v in macth_dict.items():
    if osp.exists(f'{k}_embeddings.npy'):
        macth_dict[k]['embeddings'] = np.load(f'{k}_embeddings.npy')
    else:
        macth_dict[k]['embeddings'] = easy_search.preprocess_passages(retrieval_model, v['names'], save_path=f'{k}_embeddings.npy')


def process_file(file):
    try:
        data = json.load(open(osp.join(data_dir, file), 'r', encoding='utf-8'))
        
        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        time_total = 0
        for line in sampled_data:
            start_time = time.time()
            actual_answer = LLM_generate(line['Q'], llm_name='gpt-4o',is_print=False)
            end_time = time.time()
            # actual_answer = kimi_generate(line['Q'], is_print=False)
            is_correct = LLM_judge(line['Q'], line['A'], actual_answer, is_print=True, llm_type='gpt4o')
            line['actual_answer'] = actual_answer
            line['is_correct(LLM_judge)'] = is_correct
            line['time_cost'] = round(end_time - start_time, 2)
            time_total += line['time_cost']
            if is_correct == 'yes':
                correct_count += 1
        
        sampled_data.append({
            'correct_rate': round((correct_count / sample_size) * 100, 2),
            'sample_size': sample_size,
            'correct_count': correct_count,
            'average_time': round(time_total / sample_size, 2),
        })
        with open(osp.join(output_dir, file), 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)
        
        print(f"Processed file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")


def process_file_by_Avibot(file):
    try:
        data = json.load(open(osp.join(data_dir, file), 'r', encoding='utf-8'))
        
        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        time_total = 0
        for line in sampled_data:
            start_time = time.time()
            actual_answer = avibot_pro_generate(line['Q'], is_print=False)
            end_time = time.time()
            # actual_answer = kimi_generate(line['Q'], is_print=False)
            is_correct = LLM_judge(line['Q'], line['A'], actual_answer, is_print=True, llm_type='gpt4o')
            line['actual_answer'] = actual_answer
            line['is_correct(LLM_judge)'] = is_correct
            line['time_cost'] = round(end_time - start_time, 2)
            time_total += line['time_cost']
            if is_correct == 'yes':
                correct_count += 1
        
        sampled_data.append({
            'correct_rate': round((correct_count / sample_size) * 100, 2),
            'sample_size': sample_size,
            'correct_count': correct_count,
            'average_time': round(time_total / sample_size, 2),
        })
        with open(osp.join(output_dir, file), 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)
        
        print(f"Processed file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")


def process_file_by_SQL_RAG(file):
    connections = {database: utils.connect_to_database(database) for database in databases}
    try:
        data = json.load(open(osp.join(data_dir, file), 'r', encoding='utf-8'))

        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        time_total = 0
        for line in sampled_data:
            print(line['Q'])
            start_time = time.time()
            sql, query_database, result = easy_search.SQL_RAG(line['Q'], Q_templates, benchmark_question_embeddings, retrieval_model, llm_name, connections, convertion_dict, macth_dict, only_need_sql=True)
            end_time = time.time()
            is_correct = SQL_judge(line['SQL'], sql, connections[line['DB']], actual_result=result, is_print=True)
            line['actual_SQL'] = sql
            line['actual_answer'] = result
            line['is_correct(SQL_judge)'] = is_correct
            line['time_cost'] = round(end_time - start_time, 2)
            time_total += line['time_cost']
            if is_correct == 'yes':
                correct_count += 1
        sampled_data.append({
            'correct_rate': round((correct_count / len(sampled_data)) * 100, 2),
            'sample_size': len(sampled_data),
            'correct_count': correct_count,
            'average_time': round(time_total / sample_size, 2),
        })
        with open(osp.join(output_dir, file), 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)

        print(f"Processed file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")

def process_file_by_chatBI(file):
    try:
        data = json.load(open(osp.join(data_dir, file), 'r', encoding='utf-8'))
        
        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        time_total = 0
        for line in sampled_data:
            start_time = time.time()
            sql, result, = chatbi_generate(line['Q'])
            end_time = time.time()
            is_correct = SQL_judge(line['SQL'], sql, connections[line['DB']], actual_result=None, is_print=True)
            line['actual_SQL'] = sql
            line['actual_answer'] = result
            line['is_correct(SQL_judge)'] = is_correct
            line['time_cost'] = round(end_time - start_time, 2)
            time_total += line['time_cost']
            if is_correct == 'yes':
                correct_count += 1

        sampled_data.append({
            'correct_rate': round((correct_count / sample_size) * 100, 2),
            'sample_size': sample_size,
            'correct_count': correct_count,
            'average_time': round(time_total / sample_size, 2),
        })
        with open(osp.join(output_dir, file), 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)
        
        print(f"Processed file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")

os.makedirs(output_dir, exist_ok=True)

# with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
#     # futures = [executor.submit(process_file, file) for file in test_files]
#     # futures = [executor.submit(process_file_by_Avibot, file) for file in test_files]
#     futures = [executor.submit(process_file_by_SQL_RAG, file) for file in test_files]
#     # futures = [executor.submit(process_file_by_chatBI, file) for file in test_files]

    
#     for future in as_completed(futures):
#         future.result()

# process_file_by_chatBI("1-4.json")
process_file_by_SQL_RAG("3-12.json")

# for file in test_files:
#     # process_file_by_Avibot(file)
#     # process_file_by_chatBI(file)
#     process_file_by_SQL_RAG(file)