"""
开机自启管理模块测试
注意：涉及注册表操作，在 CI 环境中跳过。
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.autostart import AutoStart, APP_NAME


# 检测是否在 CI 环境中
IS_CI = (
    os.environ.get("CI", "").lower() == "true"
    or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
)


@pytest.mark.skipif(
    IS_CI,
    reason="CI 环境中无法正确写入注册表（Python 路径非标准安装路径）",
)
class TestAutoStart:
    """测试开机自启管理器"""

    def teardown_method(self):
        """测试后确保清理注册表"""
        try:
            AutoStart.disable()
        except Exception:
            pass

    def test_import(self):
        """测试模块可正常导入"""
        assert AutoStart is not None

    def test_is_enabled_returns_bool(self):
        """测试返回布尔值"""
        result = AutoStart.is_enabled()
        assert isinstance(result, bool)

    def test_enable_and_check(self):
        """测试启用后状态检查"""
        AutoStart.enable()
        assert AutoStart.is_enabled() is True

    def test_disable_and_check(self):
        """测试禁用后状态检查"""
        AutoStart.enable()
        AutoStart.disable()
        assert AutoStart.is_enabled() is False

    def test_set_enabled_true(self):
        """测试 set_enabled(True)"""
        AutoStart.set_enabled(True)
        assert AutoStart.is_enabled() is True

    def test_set_enabled_false(self):
        """测试 set_enabled(False)"""
        AutoStart.set_enabled(True)
        AutoStart.set_enabled(False)
        assert AutoStart.is_enabled() is False

    def test_disable_when_not_enabled(self):
        """测试未启用时禁用不报错"""
        AutoStart.disable()
        AutoStart.disable()  # 再次禁用也不应报错

    def test_app_name(self):
        """测试应用名称"""
        assert APP_NAME == "AutoScreenOff"
