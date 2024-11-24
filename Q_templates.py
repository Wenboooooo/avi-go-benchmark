Q_templates = [
    {
        "Q_template": "{city_name}有哪些机场？",
        "SQL_template": '''SELECT DISTINCT airport_name FROM airport_fbo_details WHERE city_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    },
    {
        "template": "飞机注册号为{aircraft_registration}的飞机是哪一家公司的？",
        "SQL_template": '''SELECT sd.supplier_name\nFROM aircraft_details ad\nJOIN supplier_details sd ON ad.supplier_id = sd.supplier_id\nWHERE ad.registration = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{city_name}的航空公司有哪些？",
        "SQL_template": '''SELECT supplier_name FROM supplier_details WHERE supplier_city_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{supplier_name}的总部位于哪个城市？",
        "SQL_template": '''SELECT supplier_city_name FROM supplier_details WHERE supplier_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{airport_name}的三字码是什么？",
        "SQL_template": '''SELECT iata_code FROM airport_fbo_details WHERE airport_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{airport_name}的四字码是什么？",
        "SQL_template": '''SELECT icao_code FROM airport_fbo_details WHERE airport_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{airport_name}的跑道数量是多少？",
        "SQL_template": '''SELECT runway_num FROM airport_fbo_details WHERE airport_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{airport_name}在哪个国家哪个城市？",
        "SQL_template": '''SELECT country_name, city_name FROM airport_fbo_details WHERE airport_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy",
    }, 
    {
        "template": "{supplier_name}的官网链接是什么？",
        "SQL_template": '''SELECT supplier_website FROM supplier_details WHERE supplier_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    {
        "template": "{aircraft_model_name}的最大飞行距离是多少？",
        "SQL_template": '''SELECT max_range FROM aircraft_details WHERE aircraft_model_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    {
        "template": "{aircraft_model_name}的座位数是多少？",
        "SQL_template": '''SELECT seat_num FROM aircraft_details WHERE aircraft_model_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    {
        "template": "{aircraft_model_name}的机身长度是多少？",
        "SQL_template": '''SELECT aircraft_length FROM aircraft_details WHERE aircraft_model_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    {
        "template": "{aircraft_registration}的制造年份是什么？",
        "SQL_template": '''SELECT make_year FROM aircraft_details WHERE registration = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    },
    {
        "template": "{aircraft_model_name}属于哪种机型类型（如远程、小飞机）？",
        "SQL_template": '''SELECT aircraft_type FROM aircraft_details WHERE aircraft_model_name = "{}";''',
        "query_database": "ai_database_dev",
        "category": "easy"
    }
]


Q_templates = [
    {
        "template": "查询在{airport_name}停场的所有公务机及其注册号。",
        "SQL_template":  "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    {
        "template": "展示所有在{airport_name}起降的航司、飞机，以及其对应的航线。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "{city_name}的所有机场及其距离最近的其他机场。",
        "SQL_template": "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    {
        "template": "展示过去一年中，{supplier_name}在{airport_name}的航班数量及主要使用的飞机型号。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "分析在{city_name}中，哪个机场的公务机停场数量最多，并列出相关的航司。",
        "SQL_template": "",
        "query_database": "data_center_dev",
        "category": "complex"
    },
    {
        "template": "查询所有在{airport_name}起降的航班，并找出最常用的飞机型号。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "分析{supplier_name}的飞机型号中，飞行距离最长的与座位数最多的飞机分别是什么。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "分析在{city_name}的所有机场中，哪个机场的开放时间最长。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "查询{airport_name}过去1个月的进出港航班数量以及哪些航线飞行次数较多，排名前十的航线是什么？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "分析{city_name}中，各机场的航班量，并找出排名前三的机场。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "总结过去一年中，{supplier_name}的总航班数量和飞行排名前三的区域。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "总结{aircraft_model_name}的总飞行次数及平均飞行距离。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "展示在{city_name}中，主要航司及其航班数量的总和。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "总结在{airport_name}的所有航班中，最常使用的前三飞机型号及其座位数（取区间）。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "列出在{city_name}中，使用频率最高的{top_N}公务机及其航班数。",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "从{departure_city_name}到{arrival_city_name}，飞行距离是多少，飞行时长是多少？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5个航司？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "从{departure_city_name}到{arrival_city_name}，按照飞行次数推荐排名最靠前的前5种机型？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    },
    {
        "template": "从{departure_city_name}到{arrival_city_name}，哪些机型可以直飞？",
        "SQL_template": "",
        "query_database": "ai_database_dev",
        "category": "complex"
    }
]