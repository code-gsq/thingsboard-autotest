# -*- coding: utf-8 -*-
"""
pages/alarm_page.py —— 告警页对象
"""
from pages.base_page import BasePage


class AlarmPage(BasePage):
    def open_alarms(self):
        """打开告警页"""
        self.goto("/alarms")

    def assert_alarm_visible(self, alarm_type):
        """断言某个类型的告警出现在列表中"""
        self.page.wait_for_selector(f"text={alarm_type}", timeout=30000)
