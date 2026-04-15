"""
无操作检测模块
使用 Windows API GetLastInputInfo 检测用户最后输入时间，计算无操作时长。
"""

import ctypes
import ctypes.wintypes


class LASTINPUTINFO(ctypes.Structure):
    """Windows LASTINPUTINFO 结构体"""
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_ulong),
    ]


class IdleDetector:
    """无操作检测器"""

    def get_idle_seconds(self) -> float:
        """
        获取用户无操作时间（秒）。
        通过 Windows API GetLastInputInfo 获取最后一次输入时间，
        然后与当前系统运行时间比较，计算出无操作的持续时间。
        
        Returns:
            float: 无操作时间（秒）
        """
        last_input = LASTINPUTINFO()
        last_input.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input))

        # GetTickCount 返回系统启动以来的毫秒数
        tick_count = ctypes.windll.kernel32.GetTickCount()
        idle_ms = tick_count - last_input.dwTime
        return idle_ms / 1000.0

    def get_idle_minutes(self) -> float:
        """
        获取用户无操作时间（分钟）。
        
        Returns:
            float: 无操作时间（分钟）
        """
        return self.get_idle_seconds() / 60.0

    def is_idle(self, timeout_minutes: int) -> bool:
        """
        判断无操作时间是否已超过指定阈值。
        
        Args:
            timeout_minutes: 无操作阈值（分钟）
        
        Returns:
            bool: 是否超时
        """
        return self.get_idle_minutes() >= timeout_minutes
