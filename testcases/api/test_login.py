# -*- coding: utf-8 -*-
"""
testcases/api/test_login.py —— 登录认证用例（正例 + 反例）

用等价类划分覆盖登录：
  - 有效类：正确账号密码 -> 登录成功
  - 无效类：用户名错误、空密码、空用户名、密码大小写、非邮箱格式、用户名带空格
  （密码错误已经在 test_negative.py 的 test_login_wrong_password 里，不重复写）
"""
from common.api_client import ApiClient
from config.setting import TB_USERNAME, TB_PASSWORD


def test_login_success():
    """用例：正确账号密码登录 -> 200，返回 token"""
    c = ApiClient()
    token = c.login()  # login() 内部 raise_for_status，失败会直接抛异常
    assert token is not None and len(token) > 0


def test_login_wrong_username():
    """用例：用户名错误 -> 401，提示 Invalid username or password"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": "wrong_user@thingsboard.org", "password": TB_PASSWORD})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["message"]


def test_login_empty_password():
    """用例：空密码 -> 401，提示 Authentication failed"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": TB_USERNAME, "password": ""})
    assert resp.status_code == 401
    assert resp.json()["message"] == "Authentication failed"


def test_login_empty_username():
    """用例：空用户名 -> 401，提示 Authentication failed"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": "", "password": TB_PASSWORD})
    assert resp.status_code == 401
    assert resp.json()["message"] == "Authentication failed"


def test_login_password_case_sensitive():
    """用例：密码大小写敏感 -> 大写 TENANT 登录失败 401"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": TB_USERNAME, "password": "TENANT"})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["message"]


def test_login_non_email_username():
    """用例：用户名非邮箱格式 -> 401"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": "notanemail", "password": TB_PASSWORD})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["message"]


def test_login_username_with_whitespace():
    """用例：用户名带首尾空格 -> 401（平台不自动去空格）"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": f" {TB_USERNAME} ", "password": TB_PASSWORD})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["message"]


def test_login_token_is_jwt():
    """用例：登录成功返回的 token 是 JWT（三段，用 . 分隔）"""
    c = ApiClient()
    token = c.login()
    parts = token.split(".")
    assert len(parts) == 3, f"token 不是标准 JWT 三段结构: {token[:20]}..."
