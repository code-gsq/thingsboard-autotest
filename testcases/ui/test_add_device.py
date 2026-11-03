# -*- coding: utf-8 -*-
"""
testcases/ui/test_add_device.py —— UI 用例：新增设备
"""
from pages.login_page import LoginPage
from pages.device_page import DevicePage


def test_add_device(page, device_api, device_name):
    """用例：UI 新增设备 → API 交叉验证设备确实创建成功"""
    # 1. 登录
    LoginPage(page).login()

    # 2. 通过 UI 弹窗新增设备
    DevicePage(page).add_device(device_name)

    # 3. API 交叉验证：设备确实创建成功
    #    注：UI 设备列表用虚拟滚动，DOM 断言不可靠，所以用 API 做二次确认
    device_id = device_api.get_by_name(device_name)
    assert device_id is not None, "UI 新增设备后，API 查不到该设备"

    # 清理
    device_api.delete(device_id)
