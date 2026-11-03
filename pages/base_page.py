# -*- coding: utf-8 -*-
"""
pages/base_page.py —— 页面基类（POM 的公共部分）

作用：所有页面对象都继承它，把"打开页面、等待元素"等通用操作放这里。

POM（Page Object Model，页面对象模型）：
  一个页面 = 一个类，把"页面元素定位"和"页面操作"都封装进类里。
  测试用例不直接写选择器，只调用页面对象的方法。好处：
  1. 页面改版时，只改页面对象里的定位器，测试用例不用动。
  2. 测试用例读起来像"操作步骤"，而不是一堆选择器。
"""
from config.setting import TB_BASE_URL


class BasePage:
    def __init__(self, page):
        # page 是 pytest-playwright 提供的浏览器页面对象
        self.page = page
        self.base_url = TB_BASE_URL

    def goto(self, path):
        """打开某个页面"""
        self.page.goto(f"{self.base_url}{path}")

    def wait_for_text(self, text, timeout=30000):
        """等待某段文字出现"""
        self.page.wait_for_selector(f"text={text}", timeout=timeout)
