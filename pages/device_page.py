# -*- coding: utf-8 -*-
"""
pages/device_page.py —— 设备页对象
"""
from pages.base_page import BasePage


class DevicePage(BasePage):
    # 新增设备弹窗里的名称输入框、Add 按钮
    NAME_INPUT = "mat-dialog-container input[formcontrolname=name]"
    ADD_BUTTON = "mat-dialog-container button:has-text('Add')"

    def open_add_dialog(self):
        """打开"新增设备"弹窗"""
        self.goto("/entities/devices?action=add")
        self.page.wait_for_selector("text=Add new device", timeout=20000)

    def add_device(self, name):
        """在弹窗里填名称并点 Add，完成设备创建"""
        self.open_add_dialog()
        self.page.fill(self.NAME_INPUT, name)
        self.page.click(self.ADD_BUTTON)
        # 等弹窗标题消失，说明弹窗关闭（mat-dialog-container 关掉后仍会留在 DOM，不能等它 detach）
        self.page.wait_for_selector("text=Add new device", state="detached", timeout=15000)
