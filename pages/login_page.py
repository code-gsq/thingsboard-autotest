# -*- coding: utf-8 -*-
"""
pages/login_page.py —— 登录页对象
"""
from pages.base_page import BasePage
from config.setting import TB_USERNAME, TB_PASSWORD


class LoginPage(BasePage):
    # 元素定位器统一写在这里（类属性），方便集中维护
    USERNAME_INPUT = "#username-input"
    PASSWORD_INPUT = "#password-input"
    LOGIN_BUTTON = "button[type=submit]"

    def open(self):
        """打开登录页"""
        self.goto("/login")

    def login(self, username=TB_USERNAME, password=TB_PASSWORD):
        """输入账号密码并登录，登录成功后自动跳转到 /home"""
        self.open()
        self.page.fill(self.USERNAME_INPUT, username)
        self.page.fill(self.PASSWORD_INPUT, password)
        self.page.click(self.LOGIN_BUTTON)
        # 等待跳转到首页，超时则说明登录失败
        self.page.wait_for_url("**/home", timeout=30000)
