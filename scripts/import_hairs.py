from bs4 import BeautifulSoup
import crawler
import game_assets_dao
from datetime import datetime, timezone
import json
from datetime import datetime, timedelta
import os
import pprint
from util import is_pic_by_ext


def import_12345():
    for i in range(40):
        if i < 10:
            continue
        p_i = r"E:\sucai\100种高级男女发型\448资源：40个男性插片头发系列\man-haircard %d\%d" % ((i + 1), i + 1)

        pic_dir = p_i
        pics_local = []
        preview = ''
        item0 = ''
        for item in os.listdir(pic_dir):
            img_path = os.path.join(pic_dir, item)
            pics_local.append(img_path)
            if '3D' in item:
                preview = img_path
            if not item0:
                item0 = item

        file_path = pics_local[0]
        dt = datetime.now()
        data = {
            'title': item0,
            'file_path': file_path,
            'web_url': '',
            'software': ['blender'],
            'file_type': ['obj'],
            'note': "hair," + file_path,
            'keywords': ["hair"],
            'meta': json.dumps({}),
            'score': 0,
            'file_extension': ['obj'],
            'src': 1,
            'price': 0,
            'license': 1,
            'pics': [],
            'ctime': dt.strftime("%Y-%m-%d %H:%M:%S"),
            'pics_local': pics_local,
            "preview": preview
        }
        pprint.pprint(data)
        # exit()
        game_assets_dao.insert_row(data)


import_12345()
