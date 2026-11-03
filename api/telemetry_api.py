# -*- coding: utf-8 -*-
"""
api/telemetry_api.py —— 遥测数据上报与查询封装

作用：模拟"设备上报温湿度"以及"查询设备最新遥测值"。

关键点：设备上报走的是设备自己的 access token（不是平台的 JWT），
而且遥测是异步写入的——上报后要经过消息队列处理，立刻查可能拿不到值，
所以要"轮询等待"。
"""
import time
from config.setting import REQUEST_TIMEOUT, POLL_INTERVAL, POLL_TIMEOUT


class TelemetryApi:
    def __init__(self, client):
        self.client = client

    def report_http(self, access_token, data):
        """设备侧通过 HTTP 上报遥测（用 access token，不需要 JWT 认证头）"""
        url = f"{self.client.base_url}/api/v1/{access_token}/telemetry"
        resp = self.client.session.post(url, json=data, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp

    def set_server_attributes(self, device_id, attrs):
        """给设备设置服务器属性（如告警开关、阈值）"""
        return self.client.post(
            f"/api/plugins/telemetry/DEVICE/{device_id}/attributes/SERVER_SCOPE",
            json=attrs)

    def get_latest(self, device_id, keys):
        """查询设备最新遥测值，返回 {'temperature': [{'ts':.., 'value':..}], ...}"""
        resp = self.client.get(
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries",
            params={"keys": keys})
        resp.raise_for_status()
        return resp.json()

    def wait_latest_value(self, device_id, key, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
        """轮询等待某个遥测值写入完成（异步写入），返回该值；超时返回 None"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            data = self.get_latest(device_id, key)
            series = data.get(key) or []
            if series and series[0].get("value") is not None:
                return series[0]["value"]
            time.sleep(interval)
        return None

    def get_server_attributes(self, device_id, keys):
        """查询设备服务器属性（SERVER_SCOPE），返回 [{'key':.., 'value':..}, ...]"""
        resp = self.client.get(
            f"/api/plugins/telemetry/DEVICE/{device_id}/values/attributes/SERVER_SCOPE",
            params={"keys": keys})
        resp.raise_for_status()
        return resp.json()
