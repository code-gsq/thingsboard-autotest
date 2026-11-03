# -*- coding: utf-8 -*-
"""
testcases/conftest.py —— pytest 公共 fixture（测试的前置准备）

作用：用 fixture 把"登录 + 创建各 API 对象"准备好，
      测试用例函数直接写在参数里就能拿到，不用自己写登录代码。
"""
import uuid
import pytest
from common.api_client import ApiClient
from api.device_api import DeviceApi
from api.telemetry_api import TelemetryApi
from api.alarm_api import AlarmApi
from config.setting import DEVICE_NAME_PREFIX


@pytest.fixture(scope="session")
def client():
    """会话级 fixture：整个测试只登录一次，复用同一个 token（省时间）"""
    c = ApiClient()
    c.login()
    return c


@pytest.fixture()
def device_api(client):
    """设备接口封装对象"""
    return DeviceApi(client)


@pytest.fixture()
def telemetry_api(client):
    """遥测接口封装对象"""
    return TelemetryApi(client)


@pytest.fixture()
def alarm_api(client):
    """告警接口封装对象"""
    return AlarmApi(client)


@pytest.fixture()
def device_name():
    """生成一个唯一的设备名（前缀 + 8 位随机串），避免重复"""
    return f"{DEVICE_NAME_PREFIX}{uuid.uuid4().hex[:8]}"
