# ThingsBoard IoT 平台自动化测试

基于 **Docker 本地部署**的 ThingsBoard 社区版，用 Python + pytest 搭建的 **接口 + UI** 自动化测试框架。

覆盖：设备增删、遥测上报、异步告警触发与校验、异常/负面场景（接口层），以及登录、设备管理、仪表盘、告警展示（UI 层）。

## 技术栈

| 分类 | 技术 |
|------|------|
| 语言 | Python 3.11 |
| 测试框架 | pytest |
| 接口请求 | requests |
| UI 自动化 | pytest-playwright |
| 测试报告 | allure-pytest |
| 被测系统 | ThingsBoard 4.x（Docker 部署） |

## 目录结构

```
thingsboard-autotest/
├── config/
│   └── setting.py          # 全局配置：地址、账号、轮询参数等
├── common/
│   └── api_client.py       # 登录 + 统一发请求（X-Authorization 认证）
├── api/                    # 接口业务层
│   ├── device_api.py       # 设备增删查
│   ├── telemetry_api.py    # 遥测上报 / 查询
│   └── alarm_api.py        # 告警规则 + 告警查询轮询
├── pages/                  # UI 页面对象（POM）
│   ├── base_page.py        # 页面基类
│   ├── login_page.py       # 登录页
│   ├── device_page.py      # 设备页
│   ├── dashboard_page.py   # 仪表盘页
│   └── alarm_page.py       # 告警页
├── testcases/
│   ├── conftest.py         # 公共 fixture（登录、各 API 对象）
│   ├── api/                # 接口用例（32 条，含负面/边界/等价类用例）
│   └── ui/                 # UI 用例（8 条）
├── data/                   # 测试数据（预留，可做 YAML 数据驱动）
├── reports/                # Allure 报告输出
└── pytest.ini
```

## 环境准备

1. **启动 ThingsBoard**（Docker）：
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```
   默认账号：`tenant@thingsboard.org` / `tenant`（网页地址 http://localhost:8080）

2. **安装依赖**：
   ```bash
   python -m pip install requests pytest pytest-playwright allure-pytest
   python -m playwright install chromium
   ```

## 运行测试

```bash
# 接口测试（32 条，含负面/边界用例）
python -m pytest testcases/api -v

# UI 测试（8 条）
python -m pytest testcases/ui -v

# 全部测试（40 条）
python -m pytest -v

# 生成 Allure 报告
python -m pytest --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

> Windows 可直接双击根目录 `run_allure.bat`，一键跑完测试并打开报告。
> 想看浏览器运行过程，UI 测试加 `--headed`。

## 项目亮点

1. **异步告警 + 轮询校验**：IoT 平台告警由规则链异步触发（设备上报遥测 → 后台判断 → 生成告警），测试用"轮询"等告警出现，而不是上报后立刻断言。
2. **分层架构**：config（配置）→ common（通用）→ api/pages（业务）→ testcases（用例），职责清晰、易维护。
3. **POM 模式**：UI 用页面对象模型，页面改版只改定位器，用例可读性强。
4. **ThingsBoard 特有认证**：请求头用 `X-Authorization: Bearer <token>`（非标准 `Authorization`）。
5. **UI + API 交叉验证**：规避虚拟滚动列表 DOM 断言不稳的问题。
