from bs4 import BeautifulSoup
import crawler
import game_assets_dao
from datetime import datetime, timezone
import json


def crawl_page_list(page):
    url = "https://www.gfxcamp.com/category/footage/psd-vector/page/%s/" % page

    html = crawler.req_get(url)

    # 解析 HTML 内容
    soup = BeautifulSoup(html, 'html.parser')

    # 查找所有 class 为 'content' 的元素
    contents = soup.find_all(class_='post-inner')

    # 在这些元素中进一步查找 class 为 'post-thumbnail' 的元素，并提取 'a' 标签的 href 属性
    links = []
    for content in contents:
        for post_thumbnail in content.find_all(class_='post-thumbnail'):
            a_tag = post_thumbnail.find('a')
            if a_tag and a_tag.has_attr('href'):
                links.append(a_tag['href'])
    return links


def crawl_detail(url):
    html = crawler.req_get(url)
    soup = BeautifulSoup(html, 'html.parser')
    contents = soup.find_all(class_='content')
    if not contents:
        return None
    content = contents[0]
    h1 = content.find_next('h1', class_='post-title')
    title = h1.text.strip()
    print('title:', title)
    tt = content.find_next('time', class_='published')

    div = content.find_next('div', class_='entry-inner')

    img_urls = []
    img_htmls = div.select('p > img')
    if img_htmls:
        img_urls = [i['data-src'] for i in img_htmls]

    paras = div.find_all('p')
    texts = [i.text for i in paras]

    print(texts)
    dt = datetime.fromisoformat(tt['datetime'])

    data = {
        'title': title,
        'file_path': '',
        'web_url': url,
        'software': [],
        'file_type': [],
        'note': "\n".join(texts),
        'keywords': [],
        'meta': json.dumps({}),
        'score': 0,
        'file_extension': [],
        'src': 1,
        'price': 0,
        'license': 1,
        'pics': img_urls,
        'ctime': dt,
    }
    game_assets_dao.insert_row(data)


if __name__ == '__main__':
    for i in range(20):
        page = i + 1
        urls = crawl_page_list(i)
        print(urls)
        for url in urls:
            crawl_detail(url)
            # break
        # break
