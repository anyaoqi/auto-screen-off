"""
工作时间调度器测试
"""

import os
import sys
import pytest
from unittest.mock import patch
from datetime import datetime, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.scheduler import Scheduler


class TestScheduler:
    """测试工作时间调度器"""

    def test_default_init(self):
        """测试默认初始化"""
        s = Scheduler()
        assert s.on_work_time == "09:00"
        assert s.off_work_time == "18:30"

    def test_custom_init(self):
        """测试自定义初始化"""
        s = Scheduler("08:00", "17:00")
        assert s.on_work_time == "08:00"
        assert s.off_work_time == "17:00"

    def test_work_time_setter(self):
        """测试属性设置"""
        s = Scheduler()
        s.on_work_time = "10:00"
        s.off_work_time = "20:00"
        assert s.on_work_time == "10:00"
        assert s.off_work_time == "20:00"

    @patch("src.scheduler.datetime")
    def test_is_work_time_during_work(self, mock_dt):
        """测试工作时间内"""
        mock_dt.now.return_value.time.return_value = time(12, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.is_work_time() is True

    @patch("src.scheduler.datetime")
    def test_is_work_time_before_work(self, mock_dt):
        """测试上班前"""
        mock_dt.now.return_value.time.return_value = time(7, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.is_work_time() is False

    @patch("src.scheduler.datetime")
    def test_is_work_time_after_work(self, mock_dt):
        """测试下班后"""
        mock_dt.now.return_value.time.return_value = time(20, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.is_work_time() is False

    @patch("src.scheduler.datetime")
    def test_is_work_time_at_start(self, mock_dt):
        """测试刚好上班时间"""
        mock_dt.now.return_value.time.return_value = time(9, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.is_work_time() is True

    @patch("src.scheduler.datetime")
    def test_is_work_time_at_end(self, mock_dt):
        """测试刚好下班时间"""
        mock_dt.now.return_value.time.return_value = time(18, 30)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.is_work_time() is True

    @patch("src.scheduler.datetime")
    def test_should_detect_after_work(self, mock_dt):
        """测试下班后应启用检测"""
        mock_dt.now.return_value.time.return_value = time(20, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.should_detect() is True

    @patch("src.scheduler.datetime")
    def test_should_detect_during_work(self, mock_dt):
        """测试工作时间内不检测"""
        mock_dt.now.return_value.time.return_value = time(12, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("09:00", "18:30")
        assert s.should_detect() is False

    @patch("src.scheduler.datetime")
    def test_cross_midnight_during_work(self, mock_dt):
        """测试跨午夜：工作时间内（夜班 22:00 ~ 06:00）"""
        mock_dt.now.return_value.time.return_value = time(23, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("22:00", "06:00")
        assert s.is_work_time() is True

    @patch("src.scheduler.datetime")
    def test_cross_midnight_outside_work(self, mock_dt):
        """测试跨午夜：非工作时间"""
        mock_dt.now.return_value.time.return_value = time(12, 0)
        mock_dt.strptime = datetime.strptime
        s = Scheduler("22:00", "06:00")
        assert s.is_work_time() is False

    def test_invalid_time_format(self):
        """测试无效时间格式不崩溃"""
        s = Scheduler("invalid", "bad")
        # 无效格式应返回 False（非工作时间）
        assert s.is_work_time() is False

    def test_get_status_text(self):
        """测试状态文字"""
        s = Scheduler()
        text = s.get_status_text()
        assert isinstance(text, str)
        assert len(text) > 0
