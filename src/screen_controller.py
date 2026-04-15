"""
屏幕控制模块
使用 Windows API SendMessage 广播 WM_SYSCOMMAND 控制显示器电源状态。
"""

import ctypes
import time


# Windows API 常量
HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170

# 显示器电源状态
MONITOR_ON = -1  # 打开显示器
MONITOR_STANDBY = 1  # 待机
MONITOR_OFF = 2  # 关闭显示器


class ScreenController:
    """屏幕控制器"""

    def __init__(self):
        self._last_screen_off_time = None

    def turn_off_screen(self):
        """
        关闭屏幕（硬件级关闭显示器电源）。

        效果：
        - 屏幕完全黑屏，不显示登录界面或屏保
        - 不影响正在运行的程序
        - 移动鼠标或按键可立即唤醒
        - 支持多显示器（广播消息覆盖所有显示器）
        """
        self._last_screen_off_time = time.time()
        ctypes.windll.user32.SendMessageW(
            HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF
        )

    def turn_on_screen(self):
        """
        唤醒屏幕（通常用户操作即可唤醒，此方法备用）。
        """
        ctypes.windll.user32.SendMessageW(
            HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON
        )

    def get_last_screen_off_time(self):
        """获取最后一次息屏的时间戳"""
        return self._last_screen_off_time

    def was_screen_off_recently(self, seconds: float = 5.0) -> bool:
        """检查屏幕是否在最近N秒内被关闭过"""
        if self._last_screen_off_time is None:
            return False
        return (time.time() - self._last_screen_off_time) < seconds
