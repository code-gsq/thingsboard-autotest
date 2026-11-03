# -*- coding: utf-8 -*-
"""
testcases/api/test_negative.py —— 接口异常 / 负面用例

作用：验证平台对"错误密码、空名称、非法 token、删除不存在设备、
      设备重名、设备名超长"等异常场景的返回。
面试常问"你有没有测异常场景"，这部分体现测试思路的完整性——
不只测"正常流程能跑通"，还要测"非法输入被正确拒绝"。
"""
from common.api_client import ApiClient
from config.setting import TB_USERNAME


def test_login_wrong_password():
    """用例：错误密码登录 → 返回 401"""
    c = ApiClient()
    resp = c.session.post(
        f"{c.base_url}/api/auth/login",
        json={"username": TB_USERNAME, "password": "wrong_password"})
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["message"]


def test_create_device_empty_name(device_api):
    """用例：创建设备名称为空 → 返回 400"""
    resp = device_api.client.post("/api/device", json={"name": ""})
    assert resp.status_code == 400
    assert "Device name should be specified" in resp.json()["message"]


def test_report_telemetry_invalid_token(telemetry_api):
    """用例：用非法 access token 上报遥测 → 返回 401"""
    resp = telemetry_api.client.session.post(
        f"{telemetry_api.client.base_url}/api/v1/invalid_token_123/telemetry",
        json={"temperature": 25})
    assert resp.status_code == 401


def test_delete_nonexistent_device(device_api):
    """用例：删除不存在的设备 → 返回 404"""
    resp = device_api.client.delete("/api/device/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_create_device_duplicate_name(device_api, device_name):
    """用例：创建重名设备 → 返回 400"""
    device_id = device_api.create(device_name)
    # 第二次用同一个名字创建，应被拒绝
    resp = device_api.client.post("/api/device", json={"name": device_name})
    assert resp.status_code == 400
    assert "Device with such name already exists" in resp.json()["message"]
    device_api.delete(device_id)


def test_create_device_name_too_long(device_api):
    """用例：设备名超长（300 字符，超过 255 上限）→ 返回 400 校验错误"""
    resp = device_api.client.post("/api/device", json={"name": "x" * 300})
    assert resp.status_code == 400
    assert "name length must be equal or less than 255" in resp.json()["message"]
