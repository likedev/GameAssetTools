import os
import hashlib
import requests
import psycopg2
from urllib.parse import urlparse
import game_assets_dao

BASE_PATH = "F:\\data\\img_cache"


def download_image(url, local_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False


def hash_url(url):
    # 对 URL 进行 hash，以创建子目录和文件名
    hash_obj = hashlib.sha256(url.encode())
    hash_hex = hash_obj.hexdigest()
    return hash_hex[:2], hash_hex[2:4]


def get_file_extension(url):
    # 从 URL 中提取文件扩展名
    parsed_url = urlparse(url)
    _, ext = os.path.splitext(parsed_url.path)
    return ext


def update_database_image_paths(cursor, image_id, new_paths):
    cursor.execute("UPDATE game_assets SET pics_local = %s WHERE id = %s", (new_paths, image_id))


conn = psycopg2.connect(**game_assets_dao.conn_params)
cursor = conn.cursor()

cursor.execute("SELECT id, pics FROM game_assets")

for row in cursor.fetchall():
    image_id, urls = row
    new_paths = []

    for url in urls:
        subdir1, subdir2 = hash_url(url)
        file_ext = get_file_extension(url)
        local_dir = os.path.join(BASE_PATH, subdir1, subdir2)

        # 创建子目录（如果不存在）
        os.makedirs(local_dir, exist_ok=True)

        local_filename = hashlib.sha256(url.encode()).hexdigest() + file_ext
        local_path = os.path.join(local_dir, local_filename)
        rel_path = os.path.join(subdir1, subdir2, local_filename)  # 相对路径

        if download_image(url, local_path):
            new_paths.append(rel_path)

    # 更新数据库中的路径
    update_database_image_paths(cursor, image_id, new_paths)
    print("新路径", new_paths)

conn.commit()
cursor.close()
conn.close()
