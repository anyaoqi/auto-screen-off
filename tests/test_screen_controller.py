"""
屏幕控制模块测试
注意：实际息屏测试需要在真实 Windows 环境中手动验证。
这里主要测试模块可以正常导入和调用。
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.screen_controller import ScreenController


class TestScreenController:
    """测试屏幕控制器"""

    def test_import(self):
        """测试模块可以正常导入"""
        assert ScreenController is not None

    def test_has_turn_off_method(self):
        """测试有 turn_off_screen 方法"""
        assert hasattr(ScreenController, "turn_off_screen")
        assert callable(ScreenController.turn_off_screen)

    def test_has_turn_on_method(self):
        """测试有 turn_on_screen 方法"""
        assert hasattr(ScreenController, "turn_on_screen")
        assert callable(ScreenController.turn_on_screen)

    def test_static_methods(self):
        """测试方法是静态方法"""
        controller = ScreenController()
        # 实例和类调用都应该可以
        assert hasattr(controller, "turn_off_screen")
        assert hasattr(controller, "turn_on_screen")

    # 注意：不在自动化测试中实际关闭屏幕
    # def test_turn_off_screen(self):
    #     ScreenController.turn_off_screen()
