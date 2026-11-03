# -*- coding: utf-8 -*-
"""
api/alarm_api.py —— 告警相关封装

作用：
  1. 创建设备配置（device profile），并挂一条告警规则："温度 > 50 触发 CRITICAL 告警"
  2. 查询、轮询设备告警

核心知识点（面试重点）：
  ThingsBoard 的告警不是"上报遥测后立刻就有"。真实链路是：
  设备上报遥测 -> 消息队列 -> 规则链在后台异步判断 -> 命中告警规则才生成告警。
  所以测试必须"轮询"告警接口直到它出现，不能上报完立刻断言"告警已存在"。
"""
import time
from config.setting import POLL_INTERVAL, POLL_TIMEOUT


class AlarmApi:
    def __init__(self, client):
        self.client = client

    def create_alarm_profile(self, name):
        """创建设备配置，带一条简单告警规则：temperature > 50 -> CRITICAL"""
        body = {
            "name": name,
            "default": False,
            "type": "DEFAULT",
            "transportType": "DEFAULT",
            "provisionType": "DISABLED",
            "profileData": {
                "configuration": {"type": "DEFAULT"},
                "transportConfiguration": {"type": "DEFAULT"},
                "alarms": [{
                    "id": "highTemp",
                    "alarmType": "High Temperature",
                    "createRules": {
                        "CRITICAL": {
                            "condition": {
                                "condition": [{
                                    "key": {"type": "TIME_SERIES", "key": "temperature"},
                                    "valueType": "NUMERIC",
                                    "value": None,
                                    "predicate": {
                                        "type": "NUMERIC", "operation": "GREATER",
                                        "value": {"defaultValue": 50.0, "userValue": None, "dynamicValue": None}
                                    }
                                }],
                                "spec": {"type": "SIMPLE"}
                            },
                            "schedule": None,
                            "alarmDetails": "Temperature too high: ${temperature}",
                            "dashboardId": None
                        }
                    },
                    "clearRule": None,
                    "propagate": False, "propagateToOwner": False, "propagateToTenant": False,
                    "propagateRelationTypes": None
                }]
            }
        }
        resp = self.client.post("/api/deviceProfile", json=body)
        resp.raise_for_status()
        return resp.json()["id"]["id"]

    def delete_profile(self, profile_id):
        """删除设备配置"""
        return self.client.delete(f"/api/deviceProfile/{profile_id}")

    def get_alarms(self, device_id):
        """查询某设备的所有告警，返回告警列表。

        注意：必须用 /api/alarm/DEVICE/{deviceId} 按实体查。
        /api/alarms?deviceId=xxx 这个参数会被忽略、返回全租户告警（踩过的坑）。
        """
        resp = self.client.get(f"/api/alarm/DEVICE/{device_id}",
                               params={"pageSize": 100, "page": 0,
                                       "sortProperty": "createdTime", "sortOrder": "DESC"})
        resp.raise_for_status()
        return resp.json().get("data", [])

    def wait_for_alarm(self, device_id, alarm_type, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL):
        """轮询等待指定类型的告警出现，返回告警对象；超时返回 None"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            for alarm in self.get_alarms(device_id):
                if alarm["type"] == alarm_type:
                    return alarm
            time.sleep(interval)
        return None

    def delete_alarm(self, alarm_id):
        """删除一条告警（清理测试产生的告警，避免积累）"""
        return self.client.delete(f"/api/alarm/{alarm_id}")
