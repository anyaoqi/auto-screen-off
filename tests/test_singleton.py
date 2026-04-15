"""测试单例检测功能"""

import pytest
import sys
import os

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_mutex_import_available():
    """测试 win32event 和 win32api 可以导入"""
    try:
        import win32event
        import win32api

        assert win32event is not None
        assert win32api is not None
    except ImportError:
        pytest.skip("pywin32 not installed")


def test_is_already_running_function_exists():
    """测试 is_already_running 函数存在于 main.py"""
    from src.main import is_already_running

    assert callable(is_already_running)


def test_is_already_running_returns_false_first_time():
    """测试第一次运行时返回 False"""
    try:
        from src.main import is_already_running

        # 第一次调用应该返回 False（没有已运行的实例）
        result = is_already_running()
        assert result == False
    except ImportError:
        pytest.skip("pywin32 not installed")
