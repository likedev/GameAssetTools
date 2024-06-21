import requests


def req_get(url):
    # 发送 HTTP 请求获取 HTML 内容
    response = requests.get(url)
    response.raise_for_status()  # 确保请求成功
    return response.text
