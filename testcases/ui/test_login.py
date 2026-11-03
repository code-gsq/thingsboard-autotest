# -*- coding: utf-8 -*-
"""
testcases/ui/test_login.py —— UI 用例：登录平台（正例 + 反例）
"""
from pages.login_page import LoginPage
from config.setting import TB_USERNAME, TB_PASSWORD


def test_login(page):
    """用例：登录平台 → 断言跳转到首页"""
    LoginPage(page).login()
    assert "home" in page.url


def test_login_wrong_password(page):
    """用例：错误密码 → 停留在登录页，不跳转首页"""
    LoginPage(page).open()
    page.fill(LoginPage.USERNAME_INPUT, TB_USERNAME)
    page.fill(LoginPage.PASSWORD_INPUT, "wrong_password")
    page.click(LoginPage.LOGIN_BUTTON)
    page.wait_for_timeout(3000)
    assert "/home" not in page.url


def test_login_wrong_username(page):
    """用例：错误用户名 → 停留在登录页，不跳转首页"""
    LoginPage(page).open()
    page.fill(LoginPage.USERNAME_INPUT, "wrong_user@thingsboard.org")
    page.fill(LoginPage.PASSWORD_INPUT, TB_PASSWORD)
    page.click(LoginPage.LOGIN_BUTTON)
    page.wait_for_timeout(3000)
    assert "/home" not in page.url
