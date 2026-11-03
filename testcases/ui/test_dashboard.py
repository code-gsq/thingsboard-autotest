# -*- coding: utf-8 -*-
"""
testcases/ui/test_dashboard.py —— UI 用例：查看仪表盘
"""
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage


def test_view_dashboard(page):
    """用例：登录后打开仪表盘页 → 断言页面加载成功"""
    LoginPage(page).login()
    DashboardPage(page).open_dashboards()
    # 断言：跳转到仪表盘页
    assert "/dashboards" in page.url
