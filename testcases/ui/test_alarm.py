# -*- coding: utf-8 -*-
"""
testcases/ui/test_alarm.py —— UI 用例：验证告警（端到端）

流程：API 准备好"带告警规则的设备 + 上报高温触发告警"，
      再用 UI 登录打开告警页，确认告警显示在页面上。
这是"接口 + UI"结合的端到端测试。
"""
import uuid
from pages.login_page import LoginPage
from pages.alarm_page import AlarmPage


def test_verify_alarm(page, device_api, telemetry_api, alarm_api, device_name):
    # 1. API 准备：建带告警规则的配置 + 设备，上报高温触发告警
    profile_name = f"autotest_profile_{uuid.uuid4().hex[:8]}"
    profile_id = alarm_api.create_alarm_profile(profile_name)
    device_id = device_api.create(device_name, profile_id=profile_id)
    access_token = device_api.get_credentials(device_id)
    telemetry_api.report_http(access_token, {"temperature": 80})

    # 等告警在后台异步生成
    alarm = alarm_api.wait_for_alarm(device_id, "High Temperature")
    assert alarm is not None, "API 准备阶段：上报高温后告警未触发"

    # 2. UI 登录并打开告警页
    LoginPage(page).login()
    alarm_page = AlarmPage(page)
    alarm_page.open_alarms()

    # 3. 断言：告警显示在 UI 列表中
    alarm_page.assert_alarm_visible("High Temperature")

    # 清理：删告警、设备、设备配置
    alarm_api.delete_alarm(alarm["id"]["id"])
    device_api.delete(device_id)
    alarm_api.delete_profile(profile_id)
