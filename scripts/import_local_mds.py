from bs4 import BeautifulSoup
import crawler
import game_assets_dao
from datetime import datetime, timezone
import json
from datetime import datetime, timedelta
import os

from util import is_pic_by_ext


# //导入本地的md 文件


def import_md_files(directory):
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        p1, ext = os.path.splitext(path)

        if not is_pic_by_ext(ext):
            continue

        dt = datetime.now()
        zpac_file = p1 + ".zpac"
        ext = "zpac"
        if not os.path.exists(zpac_file):
            zpac_file = p1 + ".zprj"
            ext = "zprj"
        data = {
            'title': item,
            'file_path': zpac_file,
            'web_url': '',
            'software': ['md'],
            'file_type': ['md'],
            'note': "md," + zpac_file,
            'keywords': ["md"],
            'meta': json.dumps({}),
            'score': 0,
            'file_extension': [ext],
            'src': 1,
            'price': 0,
            'license': 1,
            'pics': [],
            'ctime': dt.strftime("%Y-%m-%d %H:%M:%S"),
            'pics_local': [],
            "preview": path
        }
        print(data)
        game_assets_dao.insert_row(data)


def import_12345():
    for i in range(5):
        p_i = r"E:\md\md萝莉连衣裙汉服夹克暗黑哥特服礼服运动服3d模型服装打版文件\%d\预览图" % (i + 1)
        for item in os.listdir(p_i):
            img_path = os.path.join(p_i, item)
            p_name, _ = os.path.splitext(item)

            file_path = r"E:\md\md萝莉连衣裙汉服夹克暗黑哥特服礼服运动服3d模型服装打版文件\%d\%s.rar" % (i + 1, p_name)
            dt = datetime.now()
            data = {
                'title': item,
                'file_path': file_path,
                'web_url': '',
                'software': ['md'],
                'file_type': ['md'],
                'note': "md," + file_path,
                'keywords': ["md"],
                'meta': json.dumps({}),
                'score': 0,
                'file_extension': ['zprj'],
                'src': 1,
                'price': 0,
                'license': 1,
                'pics': [],
                'ctime': dt.strftime("%Y-%m-%d %H:%M:%S"),
                'pics_local': [img_path],
                "preview": img_path
            }
            print(data)
            # exit()
            game_assets_dao.insert_row(data)


def find_thumbnail(file_path):
    directory, file_name = os.path.split(file_path)
    base_name, _ = os.path.splitext(file_name)
    image_extensions = ['.jpg', '.jpeg', '.png']

    # Step 1: Search for same-name image in the same directory
    for ext in image_extensions:
        thumbnail_path = os.path.join(directory, base_name + ext)
        if os.path.isfile(thumbnail_path):
            return thumbnail_path

    # Step 2: Search for any image in the same directory
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            return os.path.join(directory, file)

    # Step 3: Search in parent directories
    parent_directory = os.path.dirname(directory)
    while parent_directory:
        for file in os.listdir(parent_directory):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                return os.path.join(parent_directory, file)
        parent_directory = os.path.dirname(parent_directory)

    return None


def search_zprj_or_zpac_files(directory):
    '''
    对于每个子目录，搜索 其下的 .zprj 或者 .zpac 文件，
    对于每个 目标文件，同样也要找到 对应的一个缩略图，搜索缩略图的算法：
    1. 优先查找 同级目录的同名 图片文件， 比如 skirt.zprj 对应于 skirt.jpg 或者 skirt.jpeg 或者 skirt.png 等等
    2. 如果没找到，从同级目录下找到一个图片文件，作为缩略图
    3. 如果仍然没找到，从上级目录以同样的逻辑寻找，找到即可，如果还没找到就从 上上级目录同样逻辑查找
    '''
    result = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.zprj', '.zpac')):
                file_path = os.path.join(root, file)
                thumbnail = find_thumbnail(file_path)
                result[file_path] = thumbnail
    return result


# E:\md\MD现代都市男女服装
def import_2():
    path = r'E:\md\MD现代都市男女服装'
    for item in os.listdir(path):
        if '配套' in item or '教程' in item:
            continue
        small_dir = os.path.join(path, item)
        # import_md_files(small_dir)


def import_gufeng():
    directory_path = r'E:\md\【精选】52套古风服装'
    files_with_thumbnails = search_zprj_or_zpac_files(directory_path)
    for file, thumbnail in files_with_thumbnails.items():
        print(f"File: {file}, Thumbnail: {thumbnail}")

        dt = datetime.now()
        data = {
            'title': file,
            'file_path': file,
            'web_url': '',
            'software': ['md'],
            'file_type': ['md'],
            'note': "md," + file,
            'keywords': ["md"],
            'meta': json.dumps({}),
            'score': 0,
            'file_extension': ['zprj'],
            'src': 1,
            'price': 0,
            'license': 1,
            'pics': [],
            'ctime': dt.strftime("%Y-%m-%d %H:%M:%S"),
            'pics_local': [thumbnail],
            "preview": thumbnail
        }
        print(data)
        # exit()
        game_assets_dao.insert_row(data)


import_gufeng()

# import_md_files(r"E:\md\MD8预设")
# import_md_files(r"E:\md\MD精品服装工程文件")

# import_md_files(r"E:\md\MD男性服装基础套件")
# import_md_files(r"E:\md\MD女性服装基础套件")

# import_md_files(r"E:\md\汉服萝莉服")
# import_md_files(r"E:\md\军事主题")
