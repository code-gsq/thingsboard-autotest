# -*- coding: utf-8 -*-
"""
pages/dashboard_page.py —— 仪表盘页对象
"""
from pages.base_page import BasePage


class DashboardPage(BasePage):
    def open_dashboards(self):
        """打开仪表盘列表页"""
        self.goto("/dashboards")
