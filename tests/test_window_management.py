"""测试窗口管理功能"""

import pytest
import sys
import os

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_settings_window_has_restore_method():
    """测试 SettingsWindow 有 restore 方法"""
    from src.settings_window import SettingsWindow

    # 检查方法存在
    assert hasattr(SettingsWindow, "restore")
    assert callable(getattr(SettingsWindow, "restore"))


def test_restore_method_signature():
    """测试 restore 方法签名正确"""
    from src.settings_window import SettingsWindow
    import inspect

    # 检查方法参数
    sig = inspect.signature(SettingsWindow.restore)
    params = list(sig.parameters.keys())
    assert "self" in params
