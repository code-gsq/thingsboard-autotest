# -*- coding: utf-8 -*-
"""
testcases/ui/conftest.py —— UI 测试专用 fixture

作用：把浏览器界面强制设成英文，避免中文环境下定位器（如 "Add"、"Alarms"）对不上。
"""
import pytest


@pytest.fixture()
def browser_context_args(browser_context_args):
    """覆盖 pytest-playwright 的浏览器上下文参数，强制英文界面"""
    return {**browser_context_args, "locale": "en-US"}
