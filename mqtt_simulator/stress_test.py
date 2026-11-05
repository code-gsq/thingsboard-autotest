# -*- coding: utf-8 -*-
"""
mqtt_simulator/stress_test.py —— 第 4 步：并发压测 ThingsBoard，找性能瓶颈

思路：把设备数从低到高逐步加压（默认 10 → 50 → 100 → 200 → 500），每一档：
  1. 并发跑 N 台设备、固定时长；
  2. 同时采样 ThingsBoard 容器的 CPU / 内存（docker stats）；
  3. 记录连接成功率、上报成功率；
最后输出一张汇总表 + 存 CSV，看"到多少台时 ThingsBoard 开始撑不住、瓶颈在哪"。

用法（在项目根目录运行）：
    先一次性建够设备（建到你要测的最大台数）：
        python -m mqtt_simulator.create_device --count 500
    再压测：
        python -m mqtt_simulator.stress_test --max 500 --duration 20 --interval 1
"""
import argparse
import csv
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

# Windows 控制台默认 GBK 编码，打印 ✅ 等字符会报错，这里强制转 UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from mqtt_simulator.simulator import DeviceSimulator, load_tokens

DEFAULT_STEPS = [10, 50, 100, 200, 500]   # 默认加压档位


def parse_mem_mb(s):
    """把 docker stats 的 '123.4MiB / 1.5GiB' 解析成已用多少 MB"""
    used = s.split("/")[0].strip()
    if used.endswith("GiB"):
        return float(used[:-3]) * 1024
    if used.endswith("MiB"):
        return float(used[:-3])
    if used.endswith("KiB"):
        return float(used[:-3]) / 1024
    return 0.0


def sample_docker_stats(container, seconds, out):
    """后台采样容器 CPU/内存，结果 (cpu%, mem_mb) 追加进 out 列表"""
    end = time.time() + seconds
    while time.time() < end:
        try:
            r = subprocess.run(
                ["docker", "stats", "--no-stream", "--format",
                 "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}", container],
                capture_output=True, text=True, timeout=10,
            )
            line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
            m = re.match(r"([^|]+)\|([\d.]+)%\|([^|]+)", line)
            if m:
                out.append((float(m.group(2)), parse_mem_mb(m.group(3))))
        except Exception:
            pass
        time.sleep(2)


def run_round(tokens, host, port, interval, duration, container):
    """跑一档：N 台设备并发，返回各项指标"""
    sims = [
        DeviceSimulator(t["name"], t["token"], host, port, interval, duration)
        for t in tokens
    ]

    # 起后台线程采样 ThingsBoard 资源占用
    stats = []
    sampler = threading.Thread(target=sample_docker_stats, args=(container, duration, stats), daemon=True)
    sampler.start()

    # 每台设备一个线程，并发
    threads = [threading.Thread(target=s.run, daemon=True) for s in sims]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    sampler.join()

    connected = sum(1 for s in sims if s.connected)
    total_ok = sum(s.publish_ok for s in sims)
    total_fail = sum(s.publish_fail for s in sims)
    total = total_ok + total_fail

    conn_rate = connected / len(sims) * 100 if sims else 0.0
    pub_rate = total_ok / total * 100 if total else 0.0

    cpus = [x[0] for x in stats]
    mems = [x[1] for x in stats]
    avg_cpu = sum(cpus) / len(cpus) if cpus else 0.0
    max_cpu = max(cpus) if cpus else 0.0
    avg_mem = sum(mems) / len(mems) if mems else 0.0
    max_mem = max(mems) if mems else 0.0

    return conn_rate, pub_rate, avg_cpu, max_cpu, avg_mem, max_mem


def main():
    p = argparse.ArgumentParser(description="ThingsBoard MQTT 并发压测")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--max", type=int, default=200, help="最大设备数（需预先 create_device --count 建好）")
    p.add_argument("--duration", type=float, default=20.0, help="每一档运行秒数")
    p.add_argument("--interval", type=float, default=1.0, help="上报间隔（秒）")
    p.add_argument("--container", default="docker-mytb-1", help="ThingsBoard 容器名（docker ps 看 NAMES）")
    p.add_argument("--steps", default=",".join(map(str, DEFAULT_STEPS)), help="加压档位，逗号分隔")
    args = p.parse_args()

    steps = [int(x) for x in args.steps.split(",") if x.strip()]
    steps = [s for s in steps if s <= args.max] or [args.max]

    all_tokens = load_tokens(args.max)   # 需要预先备够 max 台设备的 token

    rows = []
    print(f"开始压测，档位：{steps}，每档 {args.duration} 秒\n")
    print(f"{'设备数':>6} {'连接成功率':>10} {'上报成功率':>10} {'平均CPU%':>8} {'峰值CPU%':>8} {'平均内存MB':>10} {'峰值内存MB':>10}")
    for n in steps:
        conn_rate, pub_rate, avg_cpu, max_cpu, avg_mem, max_mem = run_round(
            all_tokens[:n], args.host, args.port, args.interval, args.duration, args.container
        )
        rows.append([n, round(conn_rate, 1), round(pub_rate, 1),
                     round(avg_cpu, 1), round(max_cpu, 1), round(avg_mem, 1), round(max_mem, 1)])
        print(f"{n:>6} {conn_rate:>9.1f}% {pub_rate:>9.1f}% "
              f"{avg_cpu:>7.1f} {max_cpu:>7.1f} {avg_mem:>9.1f} {max_mem:>9.1f}")

    # 存 CSV（utf-8-sig 方便 Excel 直接打开不乱码）
    report = Path(__file__).resolve().parent / "stress_report.csv"
    with open(report, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["设备数", "连接成功率%", "上报成功率%", "平均CPU%", "峰值CPU%", "平均内存MB", "峰值内存MB"])
        w.writerows(rows)
    print(f"\n报告已保存：{report}")


if __name__ == "__main__":
    main()
