# -*- coding: utf-8 -*-
"""
testcases/api/test_mqtt_smoke.py —— MQTT 设备接入冒烟测试

作用：验证「设备经 MQTT 接入 → 上报遥测 → ThingsBoard 真正入库」这条完整链路。
      原 40 条用例全走 HTTP 接口，唯独没测过 MQTT 协议层，这个用例补上。

核心知识点：
  1. 复用自研的 mqtt_simulator（同一个工具，既做压测也做冒烟）；
  2. 三层断言：MQTT 连接成功 → 有成功上报(PUBACK) → 遥测能被 API 查到（端到端）；
  3. 遥测是异步写入的，所以查询要轮询等待（复用 TelemetryApi.wait_latest_value）。
"""
from mqtt_simulator.simulator import DeviceSimulator


def test_mqtt_device_telemetry_ingestion(device_api, telemetry_api, device_name):
    """用例：设备经 MQTT 上报遥测 → 轮询查询 → 断言数据入库"""
    device_id = device_api.create(device_name)
    access_token = device_api.get_credentials(device_id)

    # 用模拟器通过 MQTT 上报 8 秒（interval=2 秒 → 约上报 3~4 次）
    sim = DeviceSimulator(device_name, access_token, "localhost", 1883,
                          interval=2.0, duration=8.0)
    sim.run()

    # 第一层：MQTT 连接成功
    assert sim.connected, "MQTT 连接失败"
    # 第二层：有成功上报（broker 回了 PUBACK 确认）
    assert sim.publish_ok > 0, "MQTT 上报失败"

    # 第三层：遥测真的入库（端到端验证；温度是随机游走，只断言非空）
    temp = telemetry_api.wait_latest_value(device_id, "temperature")
    assert temp is not None, "MQTT 上报的遥测未被 ThingsBoard 入库"

    device_api.delete(device_id)
