import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor

# 数据库连接参数
conn_params = {
    "dbname": "game_data",
    "user": "postgres",
    "password": "root",
    "host": "localhost",
    "port": 5432
}


def insert_tag(name, icon):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO fm_tags (name, icon) VALUES (%s, %s)",
                (name, icon)
            )


def insert_file(path, alias, tags):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO fm_files (path, alias, tags) VALUES (%s, %s, %s)",
                (path, alias, tags)
            )


def delete_fm_file(id):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "delete from fm_files where id = " + str(id))


def delete_fm_tag(id):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "delete from fm_tags where id = " + str(id))


def get_tags():
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql.SQL("SELECT * FROM fm_tags"))
            rows = cursor.fetchall()
            rows_as_dicts = [dict(row) for row in rows]
            return rows_as_dicts


def get_files():
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT * FROM fm_files")
            rows = cursor.fetchall()
            rows_as_dicts = [dict(row) for row in rows]
            return rows_as_dicts


def update_tag_db(tag_id, name, icon):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE fm_tags SET name = %s, icon = %s WHERE id = %s",
                (name, icon, tag_id)
            )


def update_file_db(file_id, path, alias, tags):
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE fm_files SET path = %s, alias = %s, tags = %s WHERE id = %s",
                (path, alias, tags, file_id)
            )
