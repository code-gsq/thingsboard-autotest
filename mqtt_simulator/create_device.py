# -*- coding: utf-8 -*-
"""
mqtt_simulator/create_device.py —— 批量创建设备并导出 access token

作用：MQTT 设备接入 ThingsBoard 不用账号密码，而是用「设备接入令牌(access token)」。
      这个脚本复用项目里已有的登录/创建设备代码，批量创建 N 台设备，把 token
      存进 tokens.json，供 simulator.py 读取（一台设备一个 token）。

用法（在项目根目录运行）：
    python -m mqtt_simulator.create_device             # 创建 1 台（默认）
    python -m mqtt_simulator.create_device --count 10  # 创建 10 台
"""
import argparse
import json
import sys
from pathlib import Path

# Windows 控制台默认 GBK 编码，打印 ✅ 等字符会报错，这里强制转 UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# 把项目根目录加进 sys.path，才能 import 到 config / common / api
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.api_client import ApiClient
from api.device_api import DeviceApi

TOKENS_FILE = Path(__file__).resolve().parent / "tokens.json"


def get_or_create_token(device_api, name):
    """已存在就复用，不存在就新建；返回该设备的 access token"""
    device_id = device_api.get_by_name(name)
    if device_id is None:
        device_id = device_api.create(name)
    return device_api.get_credentials(device_id)


def main():
    p = argparse.ArgumentParser(description="批量创建 ThingsBoard 设备并导出 token")
    p.add_argument("--count", type=int, default=1, help="创建多少台设备")
    args = p.parse_args()

    client = ApiClient()
    client.login()               # 登录平台拿 token（X-Authorization）
    device_api = DeviceApi(client)

    tokens = []
    for i in range(1, args.count + 1):
        name = f"mqtt_sim_device_{i:03d}"   # 001、002、003……
        token = get_or_create_token(device_api, name)
        tokens.append({"name": name, "token": token})
        print(f"✅ {name}  token={token}")

    # 存成 JSON，simulator.py 从这读（设备名 + token 一一对应）
    TOKENS_FILE.write_text(json.dumps(tokens, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已把 {len(tokens)} 个 token 写入 {TOKENS_FILE.name}")


if __name__ == "__main__":
    main()
