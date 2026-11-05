# -*- coding: utf-8 -*-
"""
mqtt_simulator/simulator.py —— MQTT 设备模拟器（第 3 步：并发多设备 + 统计）

相比第 2 步的升级：
  1. 支持一次模拟 N 台设备（每台设备一个线程，真正并发上报）；
  2. 不再逐台打印，而是在回调里统计「连接成功 / 上报成功 / 上报失败」，最后汇总成功率。

用法（在项目根目录运行）：
    先批量建设备拿到 token：
        python -m mqtt_simulator.create_device --count 5
    再并发跑：
        python -m mqtt_simulator.simulator --devices 5 --duration 20 --interval 1
"""
import argparse
import json
import random
import sys
import threading
import time
from pathlib import Path

# Windows 控制台默认 GBK 编码，打印 ✅ 等字符会报错，这里强制转 UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import paho.mqtt.client as mqtt

TELEMETRY_TOPIC = "v1/devices/me/telemetry"   # ThingsBoard 固定遥测主题
TOKENS_FILE = Path(__file__).resolve().parent / "tokens.json"


class DeviceSimulator:
    """模拟一台设备。run() 连接并上报，结果写回自身属性，供最后汇总"""

    def __init__(self, name, token, host, port, interval, duration):
        self.name = name
        self.token = token
        self.host = host
        self.port = port
        self.interval = interval          # 上报间隔（秒）
        self.duration = duration          # 运行时长（秒）
        self.temperature = 25.0           # 随机游走起点

        self.connected = False            # 是否连上 broker
        self.publish_ok = 0               # 上报成功次数
        self.publish_fail = 0             # 上报失败次数

        # paho-mqtt 2.x 用 V2 回调 API（V1 已弃用）
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(token)   # access token 当用户名
        self.client.on_connect = self._on_connect
        self.client.on_publish = self._on_publish

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self.connected = not reason_code.is_failure

    def _on_publish(self, client, userdata, mid, reason_code, properties):
        # 并发场景下不在回调里打印（会刷屏），改成记数，最后统一汇总
        if reason_code.is_failure:
            self.publish_fail += 1
        else:
            self.publish_ok += 1

    def make_telemetry(self):
        """随机游走生成温度 + 随机湿度"""
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(15.0, min(40.0, self.temperature))
        return {
            "temperature": round(self.temperature, 2),
            "humidity": round(random.uniform(30.0, 90.0), 2),
        }

    def run(self):
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()       # 后台线程维持长连接

            end = time.time() + self.duration
            while time.time() < end:
                payload = self.make_telemetry()
                self.client.publish(TELEMETRY_TOPIC, json.dumps(payload), qos=1)
                time.sleep(self.interval)

            time.sleep(1)                  # 等一下，让最后几条 qos=1 的确认回调走完
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            self.publish_fail += 1
            print(f"❌ {self.name} 异常：{e}")


def load_tokens(count):
    """从 tokens.json 读 count 个 token，不足会提示先建设备"""
    if not TOKENS_FILE.exists():
        raise SystemExit(f"找不到 {TOKENS_FILE.name}，请先运行：python -m mqtt_simulator.create_device --count {count}")
    tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    if len(tokens) < count:
        raise SystemExit(f"{TOKENS_FILE.name} 里只有 {len(tokens)} 个 token，不够 {count} 台，请先运行 create_device.py --count {count}")
    return tokens[:count]


def parse_args():
    p = argparse.ArgumentParser(description="ThingsBoard MQTT 设备模拟器（并发版）")
    p.add_argument("--host", default="localhost", help="ThingsBoard 地址")
    p.add_argument("--port", type=int, default=1883, help="MQTT 端口")
    p.add_argument("--devices", type=int, default=1, help="并发模拟多少台设备")
    p.add_argument("--interval", type=float, default=2.0, help="上报间隔（秒）")
    p.add_argument("--duration", type=float, default=10.0, help="运行时长（秒）")
    return p.parse_args()


def main():
    args = parse_args()
    tokens = load_tokens(args.devices)

    # 一台设备一个 DeviceSimulator 实例
    sims = [
        DeviceSimulator(t["name"], t["token"], args.host, args.port, args.interval, args.duration)
        for t in tokens
    ]

    print(f"启动 {len(sims)} 台设备，并发上报 {args.duration} 秒...")

    # 每台设备一个线程，实现真正并发
    threads = [threading.Thread(target=s.run, daemon=True) for s in sims]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    # 汇总统计
    connected = sum(1 for s in sims if s.connected)
    total_ok = sum(s.publish_ok for s in sims)
    total_fail = sum(s.publish_fail for s in sims)
    total = total_ok + total_fail

    print("\n===== 汇总统计 =====")
    print(f"设备总数：{len(sims)}")
    print(f"连接成功：{connected} / {len(sims)}")
    print(f"上报成功：{total_ok}")
    print(f"上报失败：{total_fail}")
    if total:
        print(f"上报成功率：{total_ok / total * 100:.1f}%")


if __name__ == "__main__":
    main()
