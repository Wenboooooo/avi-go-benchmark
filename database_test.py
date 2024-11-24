import pymysql

# 设置环境：'dev' 或 'pro' 或 'avigo'
environment = 'ai'  # 可以切换为 'pro'

# 数据库配置，根据不同环境和内外网地址选择相应配置
if environment == 'dev':
    user = 'nlp_dev'
    password = 'nlp*12345'
    host = 'rm-t4nao9vgc59g20e48.mysql.singapore.rds.aliyuncs.com'  # dev 内网地址

# 添加新的外网连接
elif environment == 'data_center':
    user = 'ai_data'
    password = '5a@12ujdaldj8s'
    host = 'rm-uf6k55f9394p93af8.rwlb.rds.aliyuncs.com'  # 数据中心内网地址


try:
    print('start')
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database='ai_database_dev',  # 数据库名称
        port=3306,
        connect_timeout=300  # 设置连接超时时间为30秒
    )
    print("Connection successful!")

    # 执行SQL查询，检查用户权限
    with connection.cursor() as cursor:
        # cursor.execute(f"SHOW GRANTS FOR '{user}'@'%';")
        cursor.execute(f"SELECT * FROM ai_database_dev.aircraft_details;")
        # cursor.execute(f"SELECT DISTINCT avg_speed FROM zts_trip_plane_model;;")
        

        result = cursor.fetchall()
        for row in result:
            print(row)

except pymysql.MySQLError as e:
    print(f"Error: {e}")
finally:
    # 检查 'connection' 是否存在并关闭连接
    if 'connection' in locals() and connection:
        connection.close()
        print("Connection closed.")

