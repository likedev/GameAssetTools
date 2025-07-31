import requests

# 设置 SOCKS5 代理
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890",
}

# 测试请求
url = "http://www.google.com"
response = requests.get(url, proxies=proxies)

print(response.status_code)
print(response.text)
