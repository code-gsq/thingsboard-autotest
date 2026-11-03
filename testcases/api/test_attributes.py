# -*- coding: utf-8 -*-
"""
testcases/api/test_attributes.py —— 设备服务器属性测试

服务器属性（SERVER_SCOPE attributes）跟遥测不一样：
  遥测是设备上报的历史时序数据，属性是平台侧配置的"元数据"（如固件版本、阈值）。
这里验证：设置属性 -> 查询属性值一致；查询从未设置过的属性 -> 为空。
"""
import time


def test_set_and_query_server_attribute(device_api, telemetry_api, device_name):
    """用例：设置服务器属性 → 查询到一致的值"""
    device_id = device_api.create(device_name)

    resp = telemetry_api.set_server_attributes(device_id, {"firmware": "v1.2.3"})
    assert resp.status_code == 200

    time.sleep(2)  # 属性写入后稍等再查，避免时序问题
    attrs = telemetry_api.get_server_attributes(device_id, "firmware")
    assert attrs, "设置属性后查询为空"
    assert attrs[0]["key"] == "firmware"
    assert attrs[0]["value"] == "v1.2.3"

    device_api.delete(device_id)


def test_query_unset_attribute(device_api, telemetry_api, device_name):
    """用例：查询从未设置过的属性 → 返回空"""
    device_id = device_api.create(device_name)

    attrs = telemetry_api.get_server_attributes(device_id, "nonexistent_key")
    assert not attrs

    device_api.delete(device_id)
