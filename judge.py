import os
import json
import random
import numpy as np
from os import path as osp
from concurrent.futures import ThreadPoolExecutor, as_completed
import utils
from utils import gpt4o_generate, LLM_judge, SQL_judge, kimi_generate, qwen_generate, claude_generate
import easy_search
from sentence_transformers import SentenceTransformer
from Q_templates import *
import re
import pandas as pd

random_seed = 44
sample_size = 50
random.seed(random_seed)

data_dir = "synthetic_data"
output_dir = "SQL_RAG_judge_result"

test_files = os.listdir(data_dir)
test_files = ["1-13.json"]
# test_files = ["1-8.json", "1-9.json", "1-14.json", "1-20.json", "1-22.json", "1-25.json"]
# test_files = ['1-10.json', '1-17.json', '1-4.json', '1-8.json', '1-21.json', '1-20.json']
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
        for line in sampled_data:
            actual_answer = gpt4o_generate(line['Q'], is_print=False)
            # actual_answer = kimi_generate(line['Q'], is_print=False)
            is_correct = LLM_judge(line['Q'], line['A'], actual_answer, is_print=True, llm_type='gpt4o')
            line['actual_answer'] = actual_answer
            line['is_correct(LLM_judge)'] = is_correct
            if is_correct == 'yes':
                correct_count += 1
        
        sampled_data.append({
            'correct_rate': round((correct_count / sample_size) * 100, 2),
            'sample_size': sample_size,
            'correct_count': correct_count,
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
        for line in sampled_data:
            print(line['Q'])
            sql, query_database, result = easy_search.SQL_RAG(line['Q'], Q_templates, benchmark_question_embeddings, retrieval_model, llm_name, connections, convertion_dict, macth_dict, only_need_sql=True)
            is_correct = SQL_judge(line['SQL'], sql, connections[line['DB']], actual_result=result, is_print=True)
            line['actual_SQL'] = sql
            line['actual_answer'] = result
            line['is_correct(SQL_judge)'] = is_correct
            if is_correct == 'yes':
                correct_count += 1

        sampled_data.append({
            'correct_rate': round((correct_count / sample_size) * 100, 2),
            'sample_size': sample_size,
            'correct_count': correct_count,
        })
        with open(osp.join(output_dir, file), 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)

        print(f"Processed file: {file}")
    except Exception as e:
        print(f"Error processing file {file}: {e}")

os.makedirs(output_dir, exist_ok=True)

with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = [executor.submit(process_file_by_SQL_RAG, file) for file in test_files]
    
    for future in as_completed(futures):
        future.result()
