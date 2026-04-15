"""
工作时间调度器模块
判断当前是否在工作时间内，控制息屏功能的启用/禁用。
"""

from datetime import datetime


class Scheduler:
    """工作时间调度器"""

    def __init__(self, on_work_time: str = "09:00", off_work_time: str = "18:30"):
        """
        初始化调度器。
        
        Args:
            on_work_time: 上班时间，格式 "HH:MM"
            off_work_time: 下班时间，格式 "HH:MM"
        """
        self._on_work_time = on_work_time
        self._off_work_time = off_work_time

    @property
    def on_work_time(self) -> str:
        return self._on_work_time

    @on_work_time.setter
    def on_work_time(self, value: str):
        self._on_work_time = value

    @property
    def off_work_time(self) -> str:
        return self._off_work_time

    @off_work_time.setter
    def off_work_time(self, value: str):
        self._off_work_time = value

    def is_work_time(self) -> bool:
        """
        判断当前是否在工作时间内。
        
        工作时间内：功能禁用，不检测无操作
        非工作时间：功能启用，正常检测
        
        支持跨午夜的情况，比如上班时间22:00，下班时间06:00
        
        Returns:
            bool: 是否在工作时间内
        """
        now = datetime.now().time()

        try:
            on_time = datetime.strptime(self._on_work_time, "%H:%M").time()
            off_time = datetime.strptime(self._off_work_time, "%H:%M").time()
        except ValueError:
            # 时间格式错误，默认为非工作时间（启用检测）
            return False

        if on_time <= off_time:
            # 正常情况：上班时间早于下班时间（如 09:00 ~ 18:30）
            return on_time <= now <= off_time
        else:
            # 跨午夜：上班时间晚于下班时间（如 22:00 ~ 06:00）
            return now >= on_time or now <= off_time

    def should_detect(self) -> bool:
        """
        判断当前是否应该启用无操作检测。
        工作时间内不检测，非工作时间检测。
        
        Returns:
            bool: 是否应该启用检测
        """
        return not self.is_work_time()

    def get_status_text(self) -> str:
        """
        获取当前状态文字描述。
        
        Returns:
            str: 状态描述
        """
        if self.is_work_time():
            return f"工作中 ({self._on_work_time} - {self._off_work_time})"
        else:
            return "下班时间 - 监控中"
