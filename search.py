import game_assets_dao
import time

'''
修改以下函数，使得扩展功能，使用的是 postgresql
输入的 | ，相当于或的条件，比如 "木 贴图" 则代表  note 任意一个包含 木 或者贴图的都返回
输入的 &, 相当于 and 的条件，比如 "水&贴图"，则代表  note 既包含"水"，又包含 "贴图"
还要支持 括号，括号的优先级是最高的，
 (水|木头)&贴图 ： 一定包含"贴图" 并且 "水" 和  "木头" 至少包含一个
 水&木头&贴图 ： 三个关键词都要包含
 (Substance&PhotoShop) | Blender : 包含blender，或者同时包含  Substance 和 PhotoShop
 
'''
import re


def search_game_assets_any_match_title_note(param):
    query = param['text']
    query = query.replace("（", "(")
    query = query.replace("）", ")")
    tokens = re.split(r'[\|\&\(\)]', query)

    if query:
        tokens = [token.strip() for token in tokens if token.strip() != '']
        print(tokens)
        query = query.replace('(', " ( ")
        query = query.replace(')', " ) ")
        query = query.replace('|', " or ")
        query = query.replace("&", " and ")
        for token in tokens:
            query = query.replace(token, f'( title ILIKE \'%{token}%\' OR note ILIKE \'%{token}%\' )')

        sql_query = f"SELECT * FROM game_assets WHERE {query} ORDER BY score DESC, ctime DESC LIMIT 1000"
    else:
        sql_query = f"SELECT * FROM game_assets ORDER BY score DESC, ctime DESC LIMIT 1000"
    print(sql_query)
    data = game_assets_dao.query(sql_query)
    return data

# (木|泥土)&墙面
