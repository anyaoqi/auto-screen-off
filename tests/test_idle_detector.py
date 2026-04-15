"""
无操作检测模块测试
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.idle_detector import IdleDetector


class TestIdleDetector:
    """测试无操作检测器"""

    def setup_method(self):
        self.detector = IdleDetector()

    def test_get_idle_seconds_returns_float(self):
        """测试返回浮点数类型"""
        result = self.detector.get_idle_seconds()
        assert isinstance(result, float)

    def test_get_idle_seconds_non_negative(self):
        """测试返回非负值"""
        result = self.detector.get_idle_seconds()
        assert result >= 0

    def test_get_idle_minutes_returns_float(self):
        """测试分钟返回浮点数"""
        result = self.detector.get_idle_minutes()
        assert isinstance(result, float)

    def test_get_idle_minutes_non_negative(self):
        """测试分钟返回非负值"""
        result = self.detector.get_idle_minutes()
        assert result >= 0

    def test_idle_minutes_less_than_seconds(self):
        """测试分钟值应该小于等于秒值"""
        seconds = self.detector.get_idle_seconds()
        minutes = self.detector.get_idle_minutes()
        # 允许有微小的时间差
        assert minutes <= seconds

    def test_is_idle_false_for_large_timeout(self):
        """测试超大超时值时应返回 False（刚运行测试时不可能空闲1000分钟）"""
        result = self.detector.is_idle(1000)
        assert result is False

    def test_is_idle_returns_bool(self):
        """测试返回布尔类型"""
        result = self.detector.is_idle(10)
        assert isinstance(result, bool)

    def test_multiple_calls_consistent(self):
        """测试多次调用结果一致性（短时间内差异应该很小）"""
        s1 = self.detector.get_idle_seconds()
        s2 = self.detector.get_idle_seconds()
        # 两次调用之间差异不超过2秒
        assert abs(s2 - s1) < 2
