import json
import os
import utils
from tqdm import tqdm
from collections import Counter
from multiprocessing import Pool

def find_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                json_files.append(full_path)
    return json_files

def unique_list(input_list):
    unique_list = []  # 初始化一个空列表来存储唯一的元素
    for item in input_list:
        # 检查元素是否已经在unique_list中
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


def sort_unique_dict_list_by_frequency(dict_list):
    """
    按照字典元素的重复次数由多到少对字典列表进行排序，并去掉重复的字典。

    :param dict_list: 输入的字典列表
    :return: 去重并排序后的字典列表
    """
    # 将字典列表中的每个字典转为不可变形式（元组）以进行统计
    dict_tuples = [tuple(sorted(d.items())) for d in dict_list]
    # 统计每个元组的出现次数
    frequency = Counter(dict_tuples)
    # 按照出现次数从高到低排序
    sorted_tuples = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
    # 将排序结果转回原始字典形式，保留唯一字典
    sorted_unique_dict_list = [dict(dict_tuple[0]) for dict_tuple in sorted_tuples]
    return sorted_unique_dict_list


def fetch_all_as_dict(table_name, cursor, needs=['*'], limit='', is_UNIQUE=False):
    # Query to fetch all columns of a table
    if is_UNIQUE:
        if limit == '':
            query = "SELECT UNIQUE "
            for need in needs:
                query += need + ", "
            query = query[:-2]
            query += f" FROM {table_name}"
        else:
            query = "SELECT UNIQUE "
            for need in needs:
                query += need + ", "
                query = query[:-2]
            query += f" FROM {table_name} WHERE {limit}"
    else:
        if limit == '':
            query = "SELECT "
            for need in needs:
                query += need + ", "
                query = query[:-2]
            query += f" FROM {table_name}"
        else:
            query = "SELECT "
            for need in needs:
                query += need + ", "
                query = query[:-2]
            query += f" FROM {table_name} WHERE {limit}"
    # print(query)
    # Execute the query
    cursor.execute(query)
    # Fetch all the rows
    rows = cursor.fetchall()

    # Get the column names
    columns = [column[0] for column in cursor.description]

    # Create a list of dictionaries
    result = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        result.append(row_dict)

    return result

def db2text(json_file, type='AirCraft_Detail'):
    if type == 'AirCraft_Detail':
        amenity_type = {"pets":"pet transportation, ", "smoking":"smoking, ", "wifi":"high-speed WIFI, ", "toilet":"independent bathrooms, ", "attendant":"attendant, ", "bed":"beds, "}
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
            templates = content['templates']
        f.close()
        connection = utils.connect_to_database("ai_database_dev")
        cursor = connection.cursor()
        results = fetch_all_as_dict('aircraft_details', cursor)
        out_text = []
        index = 0
        for result in tqdm(results):
            supplier_results = fetch_all_as_dict('supplier_details', cursor,
                                                 limit='supplier_id = ' + result['supplier_id'])
            # zts_plane_results = []
            zts_plane_results = fetch_all_as_dict('zts_plane_flight', cursor,
                                                  limit="pure_reg = '" + result['pure_reg'] + "'")
            for supplier_result in supplier_results:
                for key, value in supplier_result.items():
                    result[key] = value
            result['flight_count'] = len(zts_plane_results)
            support = ''
            s = "The cabin is equipped with all necessary facilities, including "
            try:
                support_list = result['aircraft_amenity_type'].split(',')
                support = s
                if len(support_list) > 0:
                    for s in support_list:
                        support += amenity_type[s]
                    support = support[:-2]
            except:
                print(support)
            for template in templates[:1]:
                for key, value in result.items():
                    template = template.replace('{' + key + '}', str(value))
                template = template.replace('{support}', support)
                out_text.append(template)
            if index % 100 == 0:
                out = {type: out_text}
                with open('db_Text/AirCraft_Detail_out.json', 'w', encoding='utf-8') as f:
                    json.dump(out, f, ensure_ascii=False)
                f.close()
            index += 1
        out = {type:out_text}
        with open('db_Text/AirCraft_Detail_out.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False)
        f.close()
    if type == 'Airport_Detail':
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
            templates = content['templates']
        f.close()
        connection = utils.connect_to_database("ai_database_dev")
        cursor = connection.cursor()
        results = fetch_all_as_dict('airport_fbo_details', cursor)
        out_text = []
        index = 0
        for result in tqdm(results):
            zts_plane_results = fetch_all_as_dict('zts_plane_flight', cursor, needs=['pure_reg'],
                                                  limit="dep_icao = '" + result['icao_code'] + "'" +
                                                  "OR arr_icao = '" + result['icao_code'] + "'")
            result['annual_flight_count'] = len(zts_plane_results)
            zts_plane_results = sort_unique_dict_list_by_frequency(zts_plane_results)
            result['unique_plane_count'] = len(zts_plane_results)
            welcome_aircraft = ''
            if len(zts_plane_results) > 0:
                zts_plane_results = zts_plane_results[:min(3, len(zts_plane_results)-1)]
                for zts_plane_result in zts_plane_results:
                    amns = fetch_all_as_dict('aircraft_details', cursor, needs=['aircraft_model_name'],
                                      limit="pure_reg = '" + zts_plane_result["pure_reg"] + "'")
                    if len(amns) > 0:
                        for amn in amns:
                            welcome_aircraft += amn["aircraft_model_name"] + ', '
                welcome_aircraft = welcome_aircraft[:-2]
            for template in templates[:1]:
                for key, value in result.items():
                    template = template.replace('{' + key + '}', str(value))
                template = template.replace('{welcome_aircraft}', welcome_aircraft)
                out_text.append(template)
            if index % 20 == 0:
                out = {type: out_text}
                with open('db_Text/Airports_Detail_out.json', 'w', encoding='utf-8') as f:
                    json.dump(out, f, ensure_ascii=False)
                f.close()
            index += 1
        out = {type:out_text}
        with open('db_Text/Airports_Detail_out.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False)
    if type == 'Supplier_Detail':
        with open(json_file, 'r', encoding='utf-8') as f:
            content = json.load(f)
            templates = content['templates']
        f.close()
        connection = utils.connect_to_database("ai_database_dev")
        cursor = connection.cursor()
        results = fetch_all_as_dict('supplier_details', cursor)
        out_text = []
        index = 0
        for result in tqdm(results):
            # zts_plane_results = fetch_all_as_dict('zts_plane_flight', cursor, needs=['pure_reg'],
            #                                       limit="dep_icao = '" + result['icao_code'] + "'" +
            #                                       "OR arr_icao = '" + result['icao_code'] + "'")
            # result['annual_flight_count'] = len(zts_plane_results)
            # zts_plane_results = sort_unique_dict_list_by_frequency(zts_plane_results)
            # result['unique_plane_count'] = len(zts_plane_results)
            # welcome_aircraft = ''
            # if len(zts_plane_results) > 0:
            #     zts_plane_results = zts_plane_results[:min(3, len(zts_plane_results)-1)]
            #     for zts_plane_result in zts_plane_results:
            #         amns = fetch_all_as_dict('aircraft_details', cursor, needs=['aircraft_model_name'],
            #                           limit="pure_reg = '" + zts_plane_result["pure_reg"] + "'")
            #         if len(amns) > 0:
            #             for amn in amns:
            #                 welcome_aircraft += amn["aircraft_model_name"] + ', '
            #     welcome_aircraft = welcome_aircraft[:-2]
            for template in templates:
                for key, value in result.items():
                    template = template.replace('{' + key + '}', str(value))
                out_text.append(template)
            if index % 20 == 0:
                out = {type: out_text}
                with open('db_Text/Supplier_Detail_out.json', 'w', encoding='utf-8') as f:
                    json.dump(out, f, ensure_ascii=False)
                f.close()
            index += 1
        out = {type:out_text}
        with open('db_Text/Supplier_Detail_out.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False)

if __name__ == '__main__':
    db2text("db_Text/Supplier_Detail.json", type='Supplier_Detail')
