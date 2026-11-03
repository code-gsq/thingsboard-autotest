# -*- coding: utf-8 -*-
"""
testcases/api/test_telemetry.py —— 设备遥测上报与查询测试

核心知识点：ThingsBoard 遥测是异步写入的——设备上报后要经过消息队列处理，
立刻查询可能拿不到值，所以测试要"轮询等待"，而不是上报完立刻断言。
"""


def test_report_and_query_telemetry(device_api, telemetry_api, device_name):
    """用例：设备上报温湿度 → 轮询查询 → 断言值一致"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 25, "humidity": 60})

    temp = telemetry_api.wait_latest_value(device_id, "temperature")
    humi = telemetry_api.wait_latest_value(device_id, "humidity")

    assert temp is not None, "温度遥测值未查询到"
    assert humi is not None, "湿度遥测值未查询到"
    assert float(temp) == 25.0
    assert float(humi) == 60.0

    device_api.delete(device_id)


def test_report_multiple_keys(device_api, telemetry_api, device_name):
    """用例：一次上报 3 个键（温度/湿度/电量）→ 逐个轮询校验"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 30, "humidity": 55, "battery": 88})

    temp = telemetry_api.wait_latest_value(device_id, "temperature")
    humi = telemetry_api.wait_latest_value(device_id, "humidity")
    batt = telemetry_api.wait_latest_value(device_id, "battery")

    assert float(temp) == 30.0
    assert float(humi) == 55.0
    assert float(batt) == 88.0

    device_api.delete(device_id)


def test_query_multiple_keys_at_once(device_api, telemetry_api, device_name):
    """用例：一次查询多个键（keys 逗号分隔）→ 返回里同时含多个键"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"temperature": 40, "humidity": 70})
    telemetry_api.wait_latest_value(device_id, "temperature")  # 等写入完成

    data = telemetry_api.get_latest(device_id, "temperature,humidity")
    assert "temperature" in data
    assert "humidity" in data

    device_api.delete(device_id)


def test_query_empty_device(device_api, telemetry_api, device_name):
    """用例：从未上报过的设备 → 查不到有效遥测值（值为 None）"""
    device_id = device_api.create(device_name)

    data = telemetry_api.get_latest(device_id, "temperature")
    series = data.get("temperature") or []
    # 从未上报过的 key：要么没有序列，要么值全为 None（没有真实数据）
    assert all(v.get("value") is None for v in series)

    device_api.delete(device_id)


def test_report_string_value(device_api, telemetry_api, device_name):
    """用例：上报字符串类型遥测 → 轮询查到字符串值"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"status": "online"})
    status = telemetry_api.wait_latest_value(device_id, "status")

    assert status == "online"

    device_api.delete(device_id)


def test_report_boolean_value(device_api, telemetry_api, device_name):
    """用例：上报布尔类型遥测 → 轮询查到布尔值"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    telemetry_api.report_http(access_token, {"enabled": True})
    enabled = telemetry_api.wait_latest_value(device_id, "enabled")

    # ThingsBoard 把布尔遥测存成字符串 "true"
    assert enabled in (True, "true")

    device_api.delete(device_id)
