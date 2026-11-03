# -*- coding: utf-8 -*-
"""
testcases/api/test_device_crud.py —— 设备"增/删/查"接口测试

用例：
  1. 创建设备后能按名字查到
  2. 删除设备后查不到
  3. 查询不存在的设备名 -> None
  4. 批量创建多台设备
  5. 删除后重建同名设备
  6. 用指定设备配置创建设备
"""
import uuid


def test_create_device(device_api, device_name):
    """用例1：创建设备 → 断言能按名字查到它"""
    device_id = device_api.create(device_name)
    assert device_id, "创建设备失败，没有返回 id"

    found_id = device_api.get_by_name(device_name)
    assert found_id == device_id, f"设备 {device_name} 创建后查不到"

    device_api.delete(device_id)


def test_delete_device(device_api, device_name):
    """用例2：删除设备 → 断言删完后查不到"""
    device_id = device_api.create(device_name)
    device_api.delete(device_id)

    assert device_api.get_by_name(device_name) is None, "设备删除后还能查到，删除失败"


def test_get_nonexistent_device(device_api, device_name):
    """用例3：按名字查询不存在的设备 → 返回 None（底层 404）"""
    assert device_api.get_by_name(device_name) is None


def test_create_multiple_devices(device_api):
    """用例4：批量创建 3 台设备，都能查到，然后清理"""
    names = [f"autotest_batch_{uuid.uuid4().hex[:6]}" for _ in range(3)]
    ids = []
    for n in names:
        ids.append(device_api.create(n))

    for n in names:
        assert device_api.get_by_name(n) is not None, f"批量创建后查不到 {n}"

    for did in ids:
        device_api.delete(did)


def test_delete_then_recreate(device_api, device_name):
    """用例5：删除设备后，用同一个名字能重新创建成功"""
    device_id = device_api.create(device_name)
    device_api.delete(device_id)

    # 删除后重名不再冲突，能再次创建
    new_id = device_api.create(device_name)
    assert device_api.get_by_name(device_name) == new_id
    device_api.delete(new_id)


def test_create_device_with_profile(device_api, alarm_api, device_name):
    """用例6：用指定设备配置（带告警规则）创建设备 → 能查到"""
    profile_name = f"autotest_profile_{uuid.uuid4().hex[:8]}"
    profile_id = alarm_api.create_alarm_profile(profile_name)

    device_id = device_api.create(device_name, profile_id=profile_id)
    assert device_api.get_by_name(device_name) == device_id

    device_api.delete(device_id)
    alarm_api.delete_profile(profile_id)
