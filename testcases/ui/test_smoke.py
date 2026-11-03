# -*- coding: utf-8 -*-
"""
testcases/ui/test_smoke.py —— UI 冒烟用例：核心页面能正常打开
"""
from pages.login_page import LoginPage
from pages.device_page import DevicePage
from pages.alarm_page import AlarmPage


def test_device_page_loads(page):
    """用例：登录后打开设备页 → URL 跳转 /devices"""
    LoginPage(page).login()
    DevicePage(page).goto("/entities/devices")
    page.wait_for_timeout(2000)
    assert "devices" in page.url


def test_alarm_page_loads(page):
    """用例：登录后打开告警页 → URL 跳转 /alarms"""
    LoginPage(page).login()
    AlarmPage(page).goto("/alarms")
    page.wait_for_timeout(2000)
    assert "/alarms" in page.url
