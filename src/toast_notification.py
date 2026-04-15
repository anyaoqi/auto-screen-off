"""
Toast 通知模块
右下角弹出提醒窗口，支持倒计时和确认/取消操作。
使用 customtkinter 实现现代化 UI。
"""

import customtkinter as ctk
import threading
import sys
import os

# 将 project 根目录加入 path，以便导入 resources
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from resources.styles import (
    TOAST_WIDTH,
    TOAST_HEIGHT,
    TOAST_MARGIN,
    DARK_BG_COLOR,
    TEXT_WHITE,
    TEXT_LIGHT,
    BTN_CONFIRM,
    BTN_CANCEL,
    BTN_CANCEL_TEXT,
    FONT_FAMILY,
    FONT_FAMILY_NUM,
    FONT_BUTTON,
    RADIUS_TOAST,
    RADIUS_BUTTON,
    TOAST_ANIM_DURATION,
)


class ToastNotification:
    """
    Toast 提醒通知窗口。

    在屏幕右下角弹出带倒计时的通知，用户可选择：
    - 确认 → 立即息屏
    - 取消 → 取消本次息屏，重置计时器
    - 倒计时结束 → 自动息屏
    """

    def __init__(
        self, countdown: int = 30, on_confirm=None, on_cancel=None, on_timeout=None
    ):
        """
        初始化 Toast 通知。

        Args:
            countdown: 倒计时秒数
            on_confirm: 确认回调
            on_cancel: 取消回调
            on_timeout: 超时回调（倒计时结束）
        """
        self.countdown = countdown
        self.remaining = countdown
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.on_timeout = on_timeout

        self._window = None
        self._timer_id = None
        self._is_showing = False
        self._countdown_label = None
        self._message_label = None

    def show(self):
        """显示 Toast 通知"""
        if self._is_showing:
            return

        self._is_showing = True
        self.remaining = self.countdown

        # 创建顶层窗口
        self._window = ctk.CTkToplevel()
        self._window.title("")
        self._window.overrideredirect(True)  # 无边框
        self._window.attributes("-topmost", True)  # 置顶
        self._window.attributes("-alpha", 0.0)  # 初始透明（用于淡入动画）
        self._window.configure(fg_color=DARK_BG_COLOR)

        # 计算位置（右下角）
        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        x = screen_w - TOAST_WIDTH - TOAST_MARGIN
        y = screen_h - TOAST_HEIGHT - TOAST_MARGIN - 40  # 减去任务栏高度
        self._window.geometry(f"{TOAST_WIDTH}x{TOAST_HEIGHT}+{x}+{y}")

        self._build_ui()
        self._fade_in()
        self._start_countdown()

    def _build_ui(self):
        """构建 Toast UI"""
        window = self._window

        # 主容器，带圆角
        main_frame = ctk.CTkFrame(
            window,
            fg_color=DARK_BG_COLOR,
            corner_radius=RADIUS_TOAST,
        )
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)

        # -- 标题行 --
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(16, 4))

        icon_label = ctk.CTkLabel(
            title_frame,
            text="🌙",
            font=(FONT_FAMILY, 16),
            text_color=TEXT_WHITE,
        )
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(
            title_frame,
            text="即将自动息屏",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=TEXT_WHITE,
        )
        title_label.pack(side="left", padx=(8, 0))

        # -- 倒计时数字 --
        self._countdown_label = ctk.CTkLabel(
            main_frame,
            text=str(self.remaining),
            font=(FONT_FAMILY_NUM, 40, "bold"),
            text_color=TEXT_WHITE,
        )
        self._countdown_label.pack(pady=(4, 2))

        # -- 提示文字 --
        self._message_label = ctk.CTkLabel(
            main_frame,
            text="秒后自动关闭屏幕",
            font=(FONT_FAMILY, 12),
            text_color=TEXT_LIGHT,
        )
        self._message_label.pack(pady=(0, 8))

        # -- 按钮行 --
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(4, 20))

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="取消",
            width=120,
            height=36,
            font=(FONT_FAMILY, 13),
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            text_color=TEXT_LIGHT,
            corner_radius=RADIUS_BUTTON,
            command=self._on_cancel_click,
        )
        cancel_btn.pack(side="left", expand=True, padx=(0, 8))

        # 确认按钮
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="立即息屏",
            width=120,
            height=36,
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=BTN_CONFIRM,
            hover_color="#3d9ae8",
            text_color=TEXT_WHITE,
            corner_radius=RADIUS_BUTTON,
            command=self._on_confirm_click,
        )
        confirm_btn.pack(side="right", expand=True, padx=(8, 0))

    def _fade_in(self):
        """淡入动画"""
        alpha = 0.0
        step = 0.05
        interval = int(TOAST_ANIM_DURATION / (1.0 / step))  # ms per step

        def _step():
            nonlocal alpha
            if self._window is None:
                return
            alpha += step
            if alpha >= 0.95:
                self._window.attributes("-alpha", 0.95)
                return
            self._window.attributes("-alpha", alpha)
            self._window.after(interval, _step)

        _step()

    def _start_countdown(self):
        """开始倒计时"""

        def _tick():
            if not self._is_showing or self._window is None:
                return

            self.remaining -= 1

            if self.remaining <= 0:
                # 倒计时结束，自动息屏
                self._close()
                if self.on_timeout:
                    self.on_timeout()
                return

            # 更新显示
            if self._countdown_label:
                self._countdown_label.configure(text=str(self.remaining))

                # 最后 10 秒变红色
                if self.remaining <= 10:
                    self._countdown_label.configure(text_color="#f56565")

            self._timer_id = self._window.after(1000, _tick)

        self._timer_id = self._window.after(1000, _tick)

    def _on_confirm_click(self):
        """确认按钮点击"""
        self._close()
        if self.on_confirm:
            self.on_confirm()

    def _on_cancel_click(self):
        """取消按钮点击"""
        self._close()
        if self.on_cancel:
            self.on_cancel()

    def _close(self):
        """关闭 Toast"""
        self._is_showing = False
        if self._timer_id and self._window:
            try:
                self._window.after_cancel(self._timer_id)
            except Exception:
                pass
        if self._window:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None

    @property
    def is_showing(self):
        return self._is_showing

    def close(self):
        """外部调用关闭"""
        self._close()
