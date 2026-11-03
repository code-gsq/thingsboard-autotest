# -*- coding: utf-8 -*-
"""
testcases/api/test_alarm.py —— 异步告警触发与轮询校验（项目核心亮点）

核心知识点：
  ThingsBoard 的告警不是"上报遥测后立刻就有"，真实链路是：
  设备上报遥测 -> 消息队列 -> 规则链后台异步判断 -> 命中告警规则才生成告警。
  所以测试必须"轮询"告警接口直到它出现，不能上报完立刻断言"告警已存在"。

边界值：告警规则是 temperature > 50（严格大于），所以 50 本身不触发。
"""
import uuid


def test_async_alarm_trigger(device_api, telemetry_api, alarm_api, device_name):
    """用例：上报高温 -> 异步触发 CRITICAL 告警 -> 轮询校验"""
    profile_name = f"autotest_profile_{uuid.uuid4().hex[:8]}"
    profile_id = alarm_api.create_alarm_profile(profile_name)

    device_id = device_api.create(device_name, profile_id=profile_id)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 80})

    alarm = alarm_api.wait_for_alarm(device_id, "High Temperature")

    assert alarm is not None, "上报高温后未触发 High Temperature 告警"
    assert alarm["severity"] == "CRITICAL"
    assert alarm["status"] == "ACTIVE_UNACK"

    # 清理：删告警、设备、设备配置
    alarm_api.delete_alarm(alarm["id"]["id"])
    device_api.delete(device_id)
    alarm_api.delete_profile(profile_id)


def test_alarm_below_threshold(device_api, telemetry_api, alarm_api, device_name):
    """用例：温度低于阈值（30 < 50）→ 不触发告警"""
    profile_name = f"autotest_profile_{uuid.uuid4().hex[:8]}"
    profile_id = alarm_api.create_alarm_profile(profile_name)

    device_id = device_api.create(device_name, profile_id=profile_id)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 30})

    # 阈值规则是 temperature > 50，30 不该触发；轮询 15 秒确认没有告警
    alarm = alarm_api.wait_for_alarm(device_id, "High Temperature", timeout=15)
    assert alarm is None, "温度低于阈值却触发了告警"

    device_api.delete(device_id)
    alarm_api.delete_profile(profile_id)


def test_alarm_threshold_boundary(device_api, telemetry_api, alarm_api, device_name):
    """用例：温度恰等于阈值 50 → 不触发（规则是 > 50 而非 >=）"""
    profile_name = f"autotest_profile_{uuid.uuid4().hex[:8]}"
    profile_id = alarm_api.create_alarm_profile(profile_name)

    device_id = device_api.create(device_name, profile_id=profile_id)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 50})

    alarm = alarm_api.wait_for_alarm(device_id, "High Temperature", timeout=15)
    assert alarm is None, "温度等于 50 不应触发（规则是严格大于）"

    device_api.delete(device_id)
    alarm_api.delete_profile(profile_id)


def test_get_alarms_empty(device_api, alarm_api, device_name):
    """用例：默认配置的设备（无告警规则）→ 告警列表为空"""
    device_id = device_api.create(device_name)

    alarms = alarm_api.get_alarms(device_id)
    assert alarms == []

    device_api.delete(device_id)
