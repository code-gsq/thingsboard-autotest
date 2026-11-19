# ThingsBoard IoT 平台自动化测试

[![CI](https://github.com/code-gsq/thingsboard-autotest/actions/workflows/ci.yml/badge.svg)](https://github.com/code-gsq/thingsboard-autotest/actions)
[![Allure Report](https://img.shields.io/badge/Allure%20Report-online-brightgreen)](https://code-gsq.github.io/thingsboard-autotest/)

基于 **Docker 本地部署**的 ThingsBoard 社区版（物联网平台），用 Python + pytest 搭建的 **接口 + UI + MQTT** 自动化测试项目，包含 **CI/CD 持续回归**与**自研 MQTT 设备模拟器 + 并发压测**。

一句话概括：从「功能正确性」和「性能容量」两个维度，对物联网平台做了完整的自动化测试与性能瓶颈定位。

---

## 量化结果一览

| 维度 | 成果 |
|------|------|
| 功能自动化 | **41 条**用例（接口 32 + UI 8 + MQTT 冒烟 1），全量回归约 **90 秒** |
| CI/CD | GitHub Actions 每次 push 自动触发，Allure 报告自动发布到 GitHub Pages |
| 并发压测 | 自研模拟器，**500 台**并发成功率 **100%** |
| 瓶颈定位 | 平均 CPU 8.2% → **112.7%**（峰值 559.7% ≈ 5.6 核），内存仅增 **68MB** → 瓶颈在 **CPU 而非内存** |

---

## 技术栈

| 分类 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 测试框架 | pytest + allure-pytest |
| 接口请求 | requests |
| UI 自动化 | pytest-playwright（POM 模式） |
| MQTT / 压测 | paho-mqtt + 多线程（自研模拟器） |
| CI/CD | GitHub Actions → Allure → GitHub Pages |
| 被测系统 | ThingsBoard 3.9.1（Docker 部署，锁版本） |

---

## 目录结构

```
thingsboard-autotest/
├── .github/workflows/ci.yml   # CI/CD 流水线（push 自动跑 + 发报告）
├── config/setting.py           # 全局配置：地址、账号、轮询参数
├── common/api_client.py        # 登录 + 统一发请求（X-Authorization 认证）
├── api/                        # 接口业务层
│   ├── device_api.py           #   设备增删查
│   ├── telemetry_api.py        #   遥测上报 / 查询
│   └── alarm_api.py            #   告警规则 + 告警查询轮询
├── pages/                      # UI 页面对象（POM）
├── testcases/
│   ├── conftest.py             # 公共 fixture（登录、各 API 对象）
│   ├── api/                    # 接口用例（32 条）+ MQTT 冒烟用例（1 条）
│   └── ui/                     # UI 用例（8 条）
├── mqtt_simulator/             # 自研 MQTT 设备模拟器 + 压测
│   ├── create_device.py        #   批量创建设备 + 导出 access token
│   ├── simulator.py            #   设备模拟器（随机游走 + 多线程并发）
│   └── stress_test.py          #   10→500 台逐档压测 + docker stats 采样
├── docker/docker-compose.yml   # ThingsBoard 本地部署配置
└── requirements.txt
```

---

## 自研 MQTT 模拟器与并发压测

ThingsBoard 的核心能力是海量设备接入，但并发接入的性能上限缺少量化验证。为此自研了 MQTT 设备模拟器：

- **认证**：设备接入令牌（access token）作为 MQTT 用户名；
- **数据建模**：用随机游走算法生成温湿度，还原真实传感器"缓慢漂移"特征；
- **并发**：多线程实现多设备并发上报，回调统计连接与上报成功率；
- **压测**：对 10/50/100/200/500 台逐档加压（每档 20 秒），同步采样容器 CPU/内存。

### 压测结果（固定环境）

| 设备数 | 连接成功率 | 上报成功率 | 平均 CPU | 峰值 CPU | 平均内存(MB) |
|--------|-----------|-----------|---------|---------|-------------|
| 10     | 100%      | 100%      | 8.2%    | 11.7%   | 1515.5      |
| 50     | 100%      | 100%      | 14.5%   | 17.5%   | 1516.5      |
| 100    | 100%      | 100%      | 36.2%   | 145.3%  | 1536.6      |
| 200    | 100%      | 100%      | 49.8%   | 222.5%  | 1552.2      |
| 500    | 100%      | 100%      | 112.7%  | 559.7%  | 1583.1      |

**结论**：设备数 10 → 500 台，内存仅增约 68MB，而 CPU 明显增长（平均 8.2%→112.7%、峰值 559.7%，约 5.6 核满载），说明**瓶颈在 CPU 而非内存**。压测脚本输出 CSV 报告（`mqtt_simulator/stress_report.csv`）。

---

## CI/CD 闭环

GitHub Actions 流水线（`.github/workflows/ci.yml`）：

```
push / PR → 拉起 ThingsBoard 服务容器 → 轮询就绪 → 跑 41 条用例 → 生成 Allure 报告 → 发布到 GitHub Pages
```

每次提交都会自动跑全量回归，报告在线可查：**https://code-gsq.github.io/thingsboard-autotest/**

---

## 环境准备

1. **启动 ThingsBoard**（Docker）：
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
   默认账号：`tenant@thingsboard.org` / `tenant`（网页 http://localhost:8080，MQTT 端口 1883）

2. **安装依赖**：
   ```bash
   python -m pip install -r requirements.txt
   python -m playwright install chromium
   ```

## 运行测试

```bash
# 全部测试（41 条）
python -m pytest -v

# 生成并打开 Allure 报告
python -m pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

> Windows 可直接双击根目录 `run_allure.bat` 一键跑完并打开报告。

## 压测用法

```bash
# 1. 批量创建设备（拿到 access token）
python -m mqtt_simulator.create_device --count 500

# 2. 并发压测（10→500 台逐档加压）
python -m mqtt_simulator.stress_test --max 500 --duration 20 --interval 1
```

---

## 项目亮点

1. **异步数据校验**：IoT 平台的遥测/告警由规则链异步处理，测试用"轮询 + 超时上界"（2 秒轮询、60 秒上限）等数据写入，而非上报后立刻断言。
2. **分层架构**：config（配置）→ common（通用）→ api/pages（业务）→ testcases（用例），职责清晰、易维护。
3. **POM 模式 + UI/API 交叉验证**：页面对象模型降低维护成本；用"UI 操作 + API 查询"规避虚拟滚动列表 DOM 断言不稳的问题。
4. **ThingsBoard 特有认证**：请求头用 `X-Authorization: Bearer <token>`（非标准 `Authorization`）。
5. **自研测试工具**：MQTT 设备模拟器既做并发压测、又作为 CI 冒烟用例复用（`testcases/api/test_mqtt_smoke.py`），验证"设备接入 → 遥测入库"端到端链路。
