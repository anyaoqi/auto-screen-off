"""
小黑 - 自动息屏助手
程序入口，整合所有模块。

核心流程：
1. 加载配置
2. 创建系统托盘
3. 启动主循环
   - 每分钟检查工作时间
   - 每秒检测无操作时间
   - 达到阈值弹出 Toast 通知
   - 倒计时结束自动息屏
"""

import sys
import os
import threading
import time

# 添加 Windows 单例支持
try:
    import win32event
    import win32api

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import customtkinter as ctk

from src.config import ConfigManager
from src.idle_detector import IdleDetector
from src.screen_controller import ScreenController
from src.scheduler import Scheduler
from src.autostart import AutoStart
from src.tray_icon import TrayIcon
from src.toast_notification import ToastNotification
from src.settings_window import SettingsWindow

# 互斥量名称
MUTEX_NAME = "AutoScreenOffAppMutex"
ERROR_ALREADY_EXISTS = 183
_global_mutex = None


def is_already_running():
    """
    检查程序是否已在运行。
    使用 Windows 互斥量实现单例模式。

    Returns:
        bool: 如果程序已在运行返回 True，否则返回 False
    """
    global _global_mutex

    if not HAS_WIN32:
        # 如果没有 pywin32，跳过单例检查
        print("[Main] 警告:pywin32 未安装，无法进行单例检测")
        return False

    try:
        _global_mutex = win32event.CreateMutex(None, True, MUTEX_NAME)
        last_error = win32api.GetLastError()

        if last_error == ERROR_ALREADY_EXISTS:
            print("[Main] 检测到程序已在运行")
            win32api.CloseHandle(_global_mutex)
            _global_mutex = None
            return True

        return False
    except Exception as e:
        print(f"[Main] 单例检测异常: {e}")
        return True


class AutoScreenOffApp:
    """
    自动息屏助手主应用。
    整合所有模块，管理主循环和状态。
    """

    def __init__(self, autostart=False):
        # 核心模块
        self.config = ConfigManager()
        self.idle_detector = IdleDetector()
        self.screen_controller = ScreenController()
        self.scheduler = Scheduler(
            on_work_time=self.config.get("on_work_time", "09:00"),
            off_work_time=self.config.get("off_work_time", "18:30"),
        )

        # 状态
        self._running = True
        self._paused = False
        self._toast_showing = False
        self._toast = None
        self._settings_window = None
        self._autostart = autostart  # 是否开机自启动

        # customtkinter 根窗口（隐藏，仅作为事件循环载体）
        self._root = None

        # 系统托盘
        self.tray = TrayIcon(
            on_settings=self._open_settings,
            on_screen_off=self._immediate_screen_off,
            on_pause=self._pause_detection,
            on_resume=self._resume_detection,
            on_quit=self._quit_app,
        )

    def run(self):
        """启动应用"""
        # 创建隐藏的 ctk 根窗口
        self._root = ctk.CTk()
        self._root.withdraw()  # 隐藏主窗口
        self._root.title("小黑 - 自动息屏助手")

        # 设置 customtkinter 主题
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 同步开机自启状态
        auto_start = self.config.get("auto_start", False)
        AutoStart.set_enabled(auto_start)

        # 在子线程启动系统托盘
        tray_thread = threading.Thread(target=self.tray.start, daemon=True)
        tray_thread.start()

        # 在子线程启动检测主循环
        detect_thread = threading.Thread(target=self._detection_loop, daemon=True)
        detect_thread.start()

        # 更新托盘状态
        self._update_tray_status()

        # 如果不是开机自启动，延迟 500ms 打开设置窗口
        if not self._autostart:
            self._root.after(500, self._open_settings)

        # 运行 tkinter 事件循环
        self._root.mainloop()

    def _detection_loop(self):
        """
        核心检测循环。
        每秒执行一次，检测无操作时间。
        """
        last_work_check = 0
        last_screen_off_time = None  # 记录最后一次息屏时间
        waiting_for_activity = False  # 是否在等待用户活动

        while self._running:
            try:
                now = time.time()

                # 每 30 秒检查一次工作时间
                if now - last_work_check >= 30:
                    last_work_check = now
                    self._update_tray_status()

                # 如果暂停了，或者在工作时间内，不检测
                if self._paused or self.scheduler.is_work_time():
                    waiting_for_activity = False
                    last_screen_off_time = None
                    time.sleep(1)
                    continue

                # 如果正在显示 Toast，不重复检测
                if self._toast_showing:
                    time.sleep(1)
                    continue

                # 检查是否有新的息屏记录
                current_off_time = self.screen_controller.get_last_screen_off_time()
                if (
                    current_off_time is not None
                    and current_off_time != last_screen_off_time
                ):
                    # 屏幕刚被关闭过，进入等待活动状态
                    last_screen_off_time = current_off_time
                    waiting_for_activity = True
                    time.sleep(1)
                    continue

                # 如果处于等待用户活动状态
                if waiting_for_activity:
                    idle_seconds = self.idle_detector.get_idle_seconds()
                    time_since_off = now - last_screen_off_time

                    # 如果 idle 时间 < 息屏后的时间，说明用户有新操作
                    if idle_seconds < time_since_off:
                        waiting_for_activity = False  # 退出等待，开始正常检测
                    else:
                        # 用户还没有新操作，跳过检测
                        time.sleep(1)
                        continue

                # 获取无操作时间
                idle_timeout = self.config.get("idle_timeout", 10)
                idle_seconds = self.idle_detector.get_idle_seconds()
                idle_minutes = idle_seconds / 60.0

                if idle_minutes >= idle_timeout:
                    # 达到阈值，弹出 Toast 通知
                    self._show_toast()

                time.sleep(1)

            except Exception as e:
                print(f"[Main] 检测循环异常: {e}")
                time.sleep(5)

    def _show_toast(self):
        """弹出 Toast 通知（在主线程执行）"""
        if self._toast_showing:
            return

        self._toast_showing = True

        def _create_toast():
            countdown = self.config.get("toast_countdown", 30)
            self._toast = ToastNotification(
                countdown=countdown,
                on_confirm=self._on_toast_confirm,
                on_cancel=self._on_toast_cancel,
                on_timeout=self._on_toast_timeout,
            )
            self._toast.show()

        # 在主线程中创建 Toast
        if self._root:
            self._root.after(0, _create_toast)

    def _on_toast_confirm(self):
        """Toast 确认回调 → 立即息屏"""
        self._toast_showing = False
        self._toast = None
        self.screen_controller.turn_off_screen()

    def _on_toast_cancel(self):
        """Toast 取消回调 → 重置计时器"""
        self._toast_showing = False
        self._toast = None
        # 取消后不需要特殊处理，idle_detector 会在用户操作后自动重置

    def _on_toast_timeout(self):
        """Toast 超时回调 → 自动息屏"""
        self._toast_showing = False
        self._toast = None
        self.screen_controller.turn_off_screen()

    def _immediate_screen_off(self):
        """一键息屏"""
        # 如果有 Toast 正在显示，先关闭
        if self._toast and self._toast.is_showing:
            if self._root:
                self._root.after(0, self._toast.close)
        self._toast_showing = False
        self._toast = None
        self.screen_controller.turn_off_screen()

    def _open_settings(self):
        """打开设置窗口"""

        def _create_or_restore():
            # 如果窗口存在，检查是否有效
            if self._settings_window:
                try:
                    # 检查窗口是否存在且未销毁
                    if (
                        self._settings_window.is_showing
                        and self._settings_window._window
                    ):
                        # 检查窗口是否最小化
                        if self._settings_window._window.state() == "iconic":
                            self._settings_window.restore()
                            return
                        # 窗口正常显示，置顶
                        self._settings_window._window.lift()
                        self._settings_window._window.focus_force()
                        return
                except Exception:
                    # 窗口已销毁，重置引用
                    self._settings_window = None

            # 窗口不存在或已销毁，创建新窗口
            self._settings_window = SettingsWindow(
                config_manager=self.config,
                on_save=self._on_settings_save,
            )
            self._settings_window.show()

        if self._root:
            self._root.after(0, _create_or_restore)

    def _on_settings_save(self, updates: dict):
        """设置保存回调"""
        # 更新调度器时间
        if "on_work_time" in updates:
            self.scheduler.on_work_time = updates["on_work_time"]
        if "off_work_time" in updates:
            self.scheduler.off_work_time = updates["off_work_time"]

        # 更新托盘状态
        self._update_tray_status()

    def _pause_detection(self):
        """暂停检测"""
        self._paused = True
        self.tray.update_status("已暂停")

        # 如果有 Toast 正在显示，关闭它
        if self._toast and self._toast.is_showing:
            if self._root:
                self._root.after(0, self._toast.close)
            self._toast_showing = False
            self._toast = None

    def _resume_detection(self):
        """恢复检测"""
        self._paused = False
        self._update_tray_status()

    def _update_tray_status(self):
        """更新托盘状态文字"""
        if self._paused:
            self.tray.update_status("已暂停")
        elif self.scheduler.is_work_time():
            on_time = self.config.get("on_work_time", "09:00")
            off_time = self.config.get("off_work_time", "18:30")
            self.tray.update_status(f"工作中 ({on_time}-{off_time})")
        else:
            idle_timeout = self.config.get("idle_timeout", 10)
            self.tray.update_status(f"监控中 ({idle_timeout}分钟后息屏)")

    def _quit_app(self):
        """退出应用"""
        self._running = False

        # 关闭 Toast
        if self._toast and self._toast.is_showing:
            try:
                self._toast.close()
            except Exception:
                pass

        # 关闭设置窗口
        if self._settings_window and self._settings_window.is_showing:
            try:
                self._settings_window._on_close()
            except Exception:
                pass

        # 关闭 tkinter 主循环
        if self._root:
            try:
                self._root.after(0, self._root.destroy)
            except Exception:
                pass

        # 强制退出
        os._exit(0)


def main():
    """程序入口"""
    # 检查是否已有实例在运行
    if is_already_running():
        print("[Main] 程序已在运行，退出当前实例")
        sys.exit(0)

    # 检测是否通过开机自启动方式启动
    autostart = "--autostart" in sys.argv

    print(f"[Main] 启动新的应用实例 (autostart={autostart})")
    app = AutoScreenOffApp(autostart=autostart)
    app.run()


if __name__ == "__main__":
    main()
