import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
import const

# 数据库连接参数
conn_params = {
    "dbname": "game_data",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": 5432
}


def insert_row(data):
    # 连接数据库
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    # 构建插入语句
    query = sql.SQL("""
        INSERT INTO game_assets (
            title, file_path, web_url, software, file_type, note, keywords,
            meta, score, ctime, file_extension, src, price, license,pics
        ) VALUES (
            %(title)s, %(file_path)s, %(web_url)s, %(software)s, %(file_type)s, 
            %(note)s, %(keywords)s, %(meta)s, %(score)s, %(ctime)s, 
            %(file_extension)s, %(src)s, %(price)s, %(license)s,%(pics)s
        )
    """)
    # 执行插入语句
    cursor.execute(query, data)

    # 提交事务
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()


def query(sql_str):
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor(cursor_factory=DictCursor)

    # 执行查询
    cursor.execute(sql.SQL(sql_str))

    # 获取所有行
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # 将结果转换为普通的字典列表（可选）
    rows_as_dicts = [dict(row) for row in rows]
    for t in rows_as_dicts:
        if t['pics_local']:
            t['pics_local'] = [const.IMG_CACHE_BASE_URL + t for t in t['pics_local']]
            t['preview'] = t['pics_local'][0]
    return rows_as_dicts

# if __name__ == '__main__':
#     data = query("SELECT * FROM game_assets")
#     print(data)
