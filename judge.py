import os
import json
import random
import numpy as np
from os import path as osp
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import gpt4o_generate, LLM_judge, kimi_generate, qwen_generate, claude_generate
import easy_search

random_seed = 44
sample_size = 25
random.seed(random_seed)

data_dir = "synthetic_data"
output_dir = "easyRAG_judge_result"

test_files = os.listdir(data_dir)


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


def process_file_by_easyRAG(file):
    passages, origin_data = easy_search.get_easy_question_passages()
    passage_embeddings = np.load('passage_embeddings.npy')
    try:
        data = json.load(open(osp.join(data_dir, file), 'r', encoding='utf-8'))

        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        for line in sampled_data:
            # actual_answer = gpt4o_generate(line['Q'], is_print=False)
            # actual_answer = kimi_generate(line['Q'], is_print=False)
            actual_answer = easy_search.easy_RAG_LLM(line['Q'], passages, passage_embeddings, origin_data)
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


os.makedirs(output_dir, exist_ok=True)

with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = [executor.submit(process_file_by_easyRAG, file) for file in test_files]
    
    for future in as_completed(futures):
        future.result()
