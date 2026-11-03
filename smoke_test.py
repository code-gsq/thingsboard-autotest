# -*- coding: utf-8 -*-
# smoke_test.py —— 冒烟测试：验证 Python 能连通 ThingsBoard 并登录
import requests

url = "http://localhost:8080/api/auth/login"          # 登录接口
body = {"username": "tenant@thingsboard.org", "password": "tenant"}  # 账号密码
resp = requests.post(url, json=body, timeout=10)      # 发 POST 请求

print("HTTP 状态码:", resp.status_code)
data = resp.json()                                    # 返回的 JSON 转成字典
if data.get("token"):
    print("登录成功！拿到 token，长度", len(data["token"]))
else:
    print("登录失败：", data)
