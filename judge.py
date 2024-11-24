import os
import json
import random
from os import path as osp
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import gpt4o_generate, LLM_judge

random_seed = 44
sample_size = 300
random.seed(random_seed)

data_dir = "synthetic_data"
output_dir = "judge_result"

test_files = os.listdir(data_dir)


def process_file(file):
    try:
        data = json.load(open(osp.join(data_dir, file)))
        
        sampled_data = random.sample(data, min(sample_size, len(data)))
        correct_count = 0
        for line in sampled_data:
            actual_answer = gpt4o_generate(line['Q'], is_print=False)
            is_correct = LLM_judge(line['Q'], line['A'], actual_answer, is_print=True)
            line['actual_answer'] = actual_answer
            line['is_correct(LLM_judge)'] = is_correct
            if is_correct=='yes':
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
    futures = [executor.submit(process_file, file) for file in test_files]
    
    for future in as_completed(futures):
        future.result()
