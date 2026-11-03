"""
 全局配置：把测试要用到的地址、账号、密码等信息集中放这里。
 """
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# ThingsBoard 平台地址和登录账号（本地 Docker 部署；CI 里通过环境变量覆盖）
TB_BASE_URL = os.getenv("TB_BASE_URL", "http://localhost:8080")
TB_USERNAME = os.getenv("TB_USERNAME", "tenant@thingsboard.org")
TB_PASSWORD = os.getenv("TB_PASSWORD", "tenant")

# 请求超时 & 轮询校验时间参数
REQUEST_TIMEOUT = 30  # 单次请求超时（秒）
POLL_INTERVAL = 2  # 轮询间隔（秒）
POLL_TIMEOUT = 60  # 轮询最长等待（秒）

# 测试设备名前缀
DEVICE_NAME_PREFIX = "autotest_device_"