Q_templates_easy = {
    "{city_name}有哪些机场？请给出机场名称和对应的四字码。": {
        "id": "1-4",
        "Q_template": "{city_name}有哪些机场？请给出机场名称和对应的四字码。",
        "SQL_template": '''SELECT DISTINCT airport_name, icao_code FROM airport_fbo_details WHERE city_name = "{city_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    },
    "飞机注册号为{aircraft_registration}的飞机是哪一家公司的？": {
        "id": "1-5",
        "Q_template": "飞机注册号为{aircraft_registration}的飞机是哪一家公司的？",
        "SQL_template": '''SELECT sd.supplier_name FROM aircraft_details ad JOIN supplier_details sd ON ad.supplier_id = sd.supplier_id WHERE ad.registration = "{aircraft_registration}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{city_name}的航空公司有哪些？": {
        "id": "1-6",
        "Q_template": "{city_name}的航空公司有哪些？",
        "SQL_template": '''SELECT supplier_name FROM supplier_details WHERE supplier_city_name = "{city_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{aircraft_model_names}的最大载客量是多少？": {
        "id": "1-7",
        "Q_template": "{aircraft_model_names}的最大载客量是多少？",
        "SQL_template": '''SELECT max(seat_num) FROM aircraft_details WHERE aircraft_model_name = "{aircraft_model_names}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{supplier_name}航司的总部位于哪个城市？": {
        "id": "1-8",
        "Q_template": "{supplier_name}航司的总部位于哪个城市？",
        "SQL_template": '''SELECT supplier_city_name FROM supplier_details WHERE supplier_name = "{supplier_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{airport_name}的三字码是什么？": {
        "id": "1-9",
        "Q_template": "{airport_name}的四字码是什么？",
        "SQL_template": '''SELECT iata_code FROM airport_fbo_details WHERE airport_name = "{airport_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{airport_name}的四字码是什么？": {
        "id": "1-10",
        "Q_template": "{airport_name}的四字码是什么？",
        "SQL_template": '''SELECT icao_code FROM airport_fbo_details WHERE airport_name = "{airport_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "{airport_name}在哪个国家哪个城市？": {
        "id": "1-12",
        "Q_template": "{airport_name}在哪个国家哪个城市？",
        "SQL_template": '''SELECT country_name, city_name FROM airport_fbo_details WHERE airport_name = "{airport_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    "停场在{airport_name}的所有航司有哪些？": {
        "id": "1-13",
        "Q_template": "停场在{airport_name}的所有航司有哪些？",
        "SQL_template": '''SELECT  DISTINCT supplier_name FROM zts_plane_status WHERE supplier_name IS NOT NULL AND status = 0 AND pure_reg IN ( SELECT LOWER(REPLACE(REPLACE(registration, ' ', ''), '-', '')) FROM dc_aircraft WHERE delete_tag = 0 ) AND arr_icao = "{airport_icao}" COLLATE utf8mb4_general_ci;''',
        "query_database": "data_center_dev",
        "category": "easy"
    },
    "注册号为{aircraft_registration}的飞机的制造商是谁？": {
        "id": "1-14",
        "Q_template": "注册号为{aircraft_registration}的飞机的制造商是谁？",
        "SQL_template": '''SELECT brand_name FROM aircraft_details WHERE registration = "{aircraft_registration}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{supplier_name}的官网链接是什么？": {
        "id": "1-16",
        "Q_template": "{supplier_name}的官网链接是什么？",
        "SQL_template": '''SELECT supplier_website FROM supplier_details WHERE supplier_name = "{supplier_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{aircraft_model_name}机型的最大飞行距离是多少公里？": {
        "id": "1-17",
        "Q_template": "{aircraft_model_name}机型的最大飞行距离是多少公里？",
        "SQL_template": '''SELECT max_range FROM aircraft_details WHERE aircraft_model_name = "{aircraft_model_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{aircraft_model_name}机型的座位数是多少？": {
        "id": "1-18",
        "Q_template": "{aircraft_model_name}机型的座位数是多少？",
        "SQL_template": '''SELECT seat_num FROM aircraft_details WHERE aircraft_model_name = "{aircraft_model_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{aircraft_model_name}机型的机身长度是多少米？": {
        "id": "1-19",
        "Q_template": "{aircraft_model_name}机型的机身长度是多少米？",
        "SQL_template": '''SELECT aircraft_length FROM aircraft_details WHERE aircraft_model_name = "{aircraft_model_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{aircraft_model_name}机型的翼展是多少米？": {
        "id": "1-20",
        "Q_template": "{aircraft_model_name}机型的翼展是多少米？",
        "SQL_template": '''SELECT aircraft_width FROM dc_aircraft_model WHERE name = "{aircraft_model_name}" AND aircraft_width IS NOT NULL;''',
        "query_database": "data_center_dev",
        "category": "easy"
    },
    "{aircraft_model_name}机型的起飞重量是多少吨？": {
        "id": "1-21",
        "Q_template": "{aircraft_model_name}机型的起飞重量是多少吨？",
        "SQL_template": '''SELECT max_takeoff_weight FROM dc_aircraft_model WHERE name = "{aircraft_model_name}" AND max_takeoff_weight IS NOT NULL;''',
        "query_database": "data_center_dev",
        "category": "easy"
    },
    "{aircraft_registration}的制造年份是什么？": {
        "id": "1-22",
        "Q_template": "{aircraft_registration}的制造年份是什么？",
        "SQL_template": '''SELECT make_year FROM aircraft_details WHERE registration = "{aircraft_registration}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    "{aircraft_model_name}属于哪种机型类型（如远程、小飞机）？": {
        "id": "1-23",
        "Q_template": "{aircraft_model_name}属于哪种机型类型（如远程、小飞机）？",
        "SQL_template": '''SELECT aircraft_type_match.aircraft_type FROM aircraft_type_match INNER JOIN dc_aircraft_model ON aircraft_type_match.`code` = dc_aircraft_model.aircraft_type WHERE name = "{aircraft_model_name}" LIMIT 1;''',
        "query_database": "data_center_release",
        "category": "easy"
    },
    "{aircraft_model_name}机型的飞行高度范围是多少？": {
        "id": "1-24",
        "Q_template": "{aircraft_model_name}机型的飞行高度范围是多少？",
        "SQL_template": '''SELECT certified_ceiling FROM dc_aircraft_model WHERE name = "{aircraft_model_name}" AND certified_ceiling IS NOT NULL LIMIT 1;''',
        "query_database": "data_center_release",
        "category": "easy"
    },
    "Fleet information of {supplier_name}?": {
        "id": "1-25",
        "Q_template": "Fleet information of {supplier_name}?",
        "SQL_template": '''SELECT aircraft_details.aircraft_model_name FROM aircraft_details JOIN supplier_details ON aircraft_details.supplier_id = supplier_details.supplier_id WHERE supplier_details.supplier_name = "{supplier_name}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
}


Q_templates_complex = {
    "查询在{airport_name}停场的所有公务机及其注册号。": {
        "Q_template": "查询在{airport_name}停场的所有公务机及其注册号。",
        "SQL_template":  "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    "展示所有在{airport_name}起降的航司、飞机，以及其对应的航线。": {
        "Q_template": "展示所有在{airport_name}起降的航司、飞机，以及其对应的航线。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "{city_name}的所有机场及其距离最近的其他机场。": {
        "Q_template": "{city_name}的所有机场及其距离最近的其他机场。",
        "SQL_template": "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    "展示过去一年中，{supplier_name}在{airport_name}的航班数量及主要使用的飞机型号。": {
        "Q_template": "展示过去一年中，{supplier_name}在{airport_name}的航班数量及主要使用的飞机型号。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "分析在{city_name}中，哪个机场的公务机停场数量最多，并列出相关的航司。": {
        "Q_template": "分析在{city_name}中，哪个机场的公务机停场数量最多，并列出相关的航司。",
        "SQL_template": "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    "查询所有在{airport_name}起降的航班，并找出最常用的飞机型号。": {
        "Q_template": "查询所有在{airport_name}起降的航班，并找出最常用的飞机型号。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "分析{supplier_name}的飞机型号中，飞行距离最长的与座位数最多的飞机分别是什么。": {
        "Q_template": "分析{supplier_name}的飞机型号中，飞行距离最长的与座位数最多的飞机分别是什么。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "分析在{city_name}的所有机场中，哪个机场的开放时间最长。": {
        "Q_template": "分析在{city_name}的所有机场中，哪个机场的开放时间最长。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "查询{airport_name}过去1个月的进出港航班数量以及哪些航线飞行次数较多，排名前十的航线是什么？": {
        "Q_template": "查询{airport_name}过去1个月的进出港航班数量以及哪些航线飞行次数较多，排名前十的航线是什么？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "分析{city_name}中，各机场的航班量，并找出排名前三的机场。": {
        "Q_template": "分析{city_name}中，各机场的航班量，并找出排名前三的机场。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "总结过去一年中，{supplier_name}的总航班数量和飞行排名前三的区域。": {
        "Q_template": "总结过去一年中，{supplier_name}的总航班数量和飞行排名前三的区域。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "总结{aircraft_model_name}的总飞行次数及平均飞行距离。": {
        "Q_template": "总结{aircraft_model_name}的总飞行次数及平均飞行距离。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "展示在{city_name}中，主要航司及其航班数量的总和。": {
        "Q_template": "展示在{city_name}中，主要航司及其航班数量的总和。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "总结在{airport_name}的所有航班中，最常使用的前三飞机型号及其座位数（取区间）。": {
        "Q_template": "总结在{airport_name}的所有航班中，最常使用的前三飞机型号及其座位数（取区间）。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "列出在{city_name}中，使用频率最高的{top_N}公务机及其航班数。": {
        "Q_template": "列出在{city_name}中，使用频率最高的{top_N}公务机及其航班数。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "从{departure_city_name}到{arrival_city_name}，飞行距离是多少，飞行时长是多少？": {
        "Q_template": "从{departure_city_name}到{arrival_city_name}，飞行距离是多少，飞行时长是多少？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5个航司？": {
        "Q_template": "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5个航司？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5种机型？": {
        "Q_template": "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5种机型？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    "从{departure_city_name}到{arrival_city_name}，哪些机型可以直飞？": {
        "Q_template": "从{departure_city_name}到{arrival_city_name}，哪些机型可以直飞？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    }
}