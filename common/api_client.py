# -*- coding: utf-8 -*-
"""
common/api_client.py —— 接口客户端封装（最底层的"发请求"工具）

作用：把"登录拿 token"和"带 token 发请求"这两件事封装成一个类，
      后面所有接口（设备、遥测、告警）都复用它，不用重复写登录代码。
"""
import requests
from config.setting import TB_BASE_URL, TB_USERNAME, TB_PASSWORD, REQUEST_TIMEOUT


class ApiClient:
    """ThingsBoard 的 HTTP 客户端"""

    def __init__(self):
        # 初始化：记住平台地址，token 先留空
        self.base_url = TB_BASE_URL
        self.token = None
        # requests.Session() 会自动复用 TCP 连接、保存 cookie，比每次 new 快
        self.session = requests.Session()

    def login(self):
        """登录平台，拿到 token 存起来"""
        url = f"{self.base_url}/api/auth/login"
        body = {"username": TB_USERNAME, "password": TB_PASSWORD}
        resp = self.session.post(url, json=body, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()          # 如果不是 2xx（成功），直接抛异常，方便定位
        self.token = resp.json()["token"]
        return self.token

    def auth_headers(self):
        """拼出带 token 的请求头。

        注意：ThingsBoard 用的是 X-Authorization，不是标准的 Authorization，
        这是它特有的，面试时是个亮点。
        """
        return {"X-Authorization": f"Bearer {self.token}"}

    def post(self, path, json=None):
        """发 POST 请求"""
        return self.session.post(f"{self.base_url}{path}", json=json,
                                 headers=self.auth_headers(), timeout=REQUEST_TIMEOUT)

    def get(self, path, params=None):
        """发 GET 请求"""
        return self.session.get(f"{self.base_url}{path}", params=params,
                                headers=self.auth_headers(), timeout=REQUEST_TIMEOUT)

    def delete(self, path):
        """发 DELETE 请求"""
        return self.session.delete(f"{self.base_url}{path}",
                                   headers=self.auth_headers(), timeout=REQUEST_TIMEOUT)
