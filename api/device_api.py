# -*- coding: utf-8 -*-
"""
api/device_api.py —— 设备相关接口封装（业务层）

作用：把"创建设备、查设备、删设备、拿凭据"这些具体业务操作封装成方法。
      测试用例里只调用这些方法，不直接碰底层 URL 和请求，代码更清晰。
"""


class DeviceApi:
    def __init__(self, client):
        # 复用一个 ApiClient（已经登录过、带着 token）
        self.client = client

    def create(self, name, profile_id=None):
        """创建设备，返回设备 id（uuid 字符串）。

        profile_id：可选，指定设备配置（不传则用默认配置）。
        """
        body = {"name": name}
        if profile_id:
            # ThingsBoard 里设备配置引用是嵌套对象 {"entityType", "id"}
            body["deviceProfileId"] = {"entityType": "DEVICE_PROFILE", "id": profile_id}
        resp = self.client.post("/api/device", json=body)
        resp.raise_for_status()
        # ThingsBoard 返回的 id 是嵌套对象 {"entityType": "DEVICE", "id": "uuid"}
        return resp.json()["id"]["id"]

    def get_by_name(self, name):
        """按名字查设备，返回设备 id；查不到返回 None。

        注意：ThingsBoard 这个接口很特殊——设备存在返回 200（单个设备对象），
        不存在直接返回 404（不是 200 + 空列表）。所以要先单独处理 404。
        """
        resp = self.client.get("/api/tenant/devices", params={"deviceName": name})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()["id"]["id"]

    def delete(self, device_id):
        """删除设备"""
        return self.client.delete(f"/api/device/{device_id}")

    def get_credentials(self, device_id):
        """获取设备凭据中的 access token（设备上报数据时用）"""
        resp = self.client.get(f"/api/device/{device_id}/credentials")
        resp.raise_for_status()
        return resp.json()["credentialsId"]
