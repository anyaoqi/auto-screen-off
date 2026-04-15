"""
设置窗口模块
提供精致的参数配置界面，现代化卡片式布局。
使用 customtkinter 实现。
"""

import os
import sys

import customtkinter as ctk

# 将 project 根目录加入 path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from resources.styles import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_ORANGE,
    ACCENT_PURPLE,
    BG_COLOR,
    BTN_CANCEL,
    BTN_CANCEL_TEXT,
    CARD_BG_COLOR,
    COUNTDOWN_MAX,
    COUNTDOWN_MIN,
    FONT_FAMILY,
    FONT_FAMILY_NUM,
    RADIUS_BUTTON,
    RADIUS_CARD,
    SETTINGS_HEIGHT,
    SETTINGS_WIDTH,
    TEXT_PRIMARY,
    TEXT_WHITE,
    IDLE_TIMEOUT_MAX,
    IDLE_TIMEOUT_MIN,
)


class SettingsWindow:
    """
    设置窗口。
    使用统一卡片骨架和更清晰的信息层级，优化间距、对齐和操作区布局。
    """

    def __init__(self, config_manager, on_save=None):
        self.config = config_manager
        self.on_save = on_save
        self._window = None
        self._is_showing = False

    def show(self):
        """显示设置窗口"""
        if self._is_showing and self._window:
            self._window.lift()
            self._window.focus_force()
            return

        self._is_showing = True

        self._window = ctk.CTkToplevel()
        self._window.title("小黑 - 设置")
        self._window.geometry(f"{SETTINGS_WIDTH}x{SETTINGS_HEIGHT}")
        self._window.resizable(False, False)
        self._window.configure(fg_color=BG_COLOR)
        self._window.protocol("WM_DELETE_WINDOW", self._on_close)

        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "resources", "icon.png"
        )
        if os.path.exists(icon_path):
            try:
                self._window.iconbitmap(default="")
            except Exception:
                pass

        self._window.update_idletasks()
        screen_w = self._window.winfo_screenwidth()
        screen_h = self._window.winfo_screenheight()
        x = (screen_w - SETTINGS_WIDTH) // 2
        y = (screen_h - SETTINGS_HEIGHT) // 2
        self._window.geometry(f"+{x}+{y}")

        self._build_ui()
        self._window.attributes("-topmost", True)

    def restore(self):
        """
        恢复最小化的窗口。
        如果窗口存在但被最小化，则恢复并置顶显示。
        """
        if self._window and self._is_showing:
            try:
                # 检测窗口是否最小化
                if self._window.state() == "iconic":
                    self._window.deiconify()  # 恢复窗口

                # 置顶并获取焦点
                self._window.lift()
                self._window.focus_force()
                self._window.attributes("-topmost", True)
            except Exception as e:
                print(f"[SettingsWindow] 恢复窗口失败: {e}")

    def _build_ui(self):
        """构建设置界面"""
        window = self._window
        config = self.config.get_all()

        # 头部区域
        header = ctk.CTkFrame(window, fg_color="#5b6ee1", height=80, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=24, pady=(16, 14))

        header_top = ctk.CTkFrame(header_inner, fg_color="transparent")
        header_top.pack(fill="x")

        title_label = ctk.CTkLabel(
            header_top,
            text="⚙️  自动息屏设置",
            font=(FONT_FAMILY, 18, "bold"),
            text_color=TEXT_WHITE,
            anchor="w",
        )
        title_label.pack(side="left")

        header_badge = ctk.CTkLabel(
            header_top,
            text="桌面助手配置",
            height=26,
            corner_radius=13,
            fg_color="#7c8df0",
            text_color=TEXT_WHITE,
            font=(FONT_FAMILY, 11, "bold"),
            padx=12,
        )
        header_badge.pack(side="right", padx=(0, 4))

        subtitle_label = ctk.CTkLabel(
            header_inner,
            text="调整检测阈值、工作时间和启动方式，保存后立即生效。",
            font=(FONT_FAMILY, 11),
            text_color="#dbe3ff",
            anchor="w",
            justify="left",
        )
        subtitle_label.pack(fill="x", pady=(6, 0))

        # 内容滚动区
        content = ctk.CTkScrollableFrame(
            window,
            fg_color=BG_COLOR,
            scrollbar_button_color="#cbd5e0",
            scrollbar_button_hover_color="#a0aec0",
            corner_radius=0,
        )
        # 延迟 pack content，以确保底部操作区能够正确吸底

        # 提示卡片
        summary = ctk.CTkFrame(
            content,
            fg_color="#eef2ff",
            corner_radius=12,
            border_width=1,
            border_color="#dbe4ff",
        )
        summary.pack(fill="x", pady=(0, 10))

        summary_label = ctk.CTkLabel(
            summary,
            text="建议保留工作时间限制，避免上班期间误触发自动息屏。",
            font=(FONT_FAMILY, 11),
            text_color="#3730a3",
            anchor="w",
            justify="left",
        )
        summary_label.pack(fill="x", padx=16, pady=10)

        card1 = self._create_card(
            content,
            "⏱️  无操作息屏时间",
            ACCENT_BLUE,
            "离开电脑超过此时间后自动息屏",
        )
        slider_row1 = self._create_value_row(card1)
        slider_row1.pack(pady=(0, 6))
        self._create_inline_hint(slider_row1, "自动息屏阈值", ACCENT_BLUE).pack(
            side="left", padx=(0, 12)
        )
        self._idle_value_label = self._create_value_badge(
            slider_row1,
            f"{config.get('idle_timeout', 10):2d} 分钟",
            ACCENT_BLUE,
            "#edf6ff",
        )
        self._idle_value_label.pack(side="right")

        self._idle_slider = ctk.CTkSlider(
            card1,
            from_=IDLE_TIMEOUT_MIN,
            to=IDLE_TIMEOUT_MAX,
            number_of_steps=IDLE_TIMEOUT_MAX - IDLE_TIMEOUT_MIN,
            height=18,
            button_color=ACCENT_BLUE,
            button_hover_color="#3d9ae8",
            progress_color=ACCENT_BLUE,
            fg_color="#e2e8f0",
            command=self._on_idle_change,
        )
        self._idle_slider.set(config.get("idle_timeout", 10))
        self._idle_slider.pack(fill="x", pady=(8, 6))

        ctk.CTkLabel(
            card1,
            text=f"最短 {IDLE_TIMEOUT_MIN} 分钟，最长 {IDLE_TIMEOUT_MAX} 分钟",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        card2 = self._create_card(
            content,
            "🕐  工作时间设置",
            ACCENT_PURPLE,
            "工作时间内不启用息屏，非工作时间自动监控",
        )
        time_frame = ctk.CTkFrame(card2, fg_color="transparent")
        time_frame.pack(fill="x", pady=(4, 0))
        time_frame.grid_columnconfigure(0, weight=1)
        time_frame.grid_columnconfigure(1, weight=1)
        time_frame.grid_rowconfigure(0, weight=1)

        on_panel = self._create_time_input_panel(
            time_frame, "上班时间", "开始限制息屏", ACCENT_PURPLE
        )
        on_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._on_work_entry = self._create_time_entry(on_panel)
        self._on_work_entry.insert(0, config.get("on_work_time", "09:00"))
        self._on_work_entry.pack(fill="x", padx=12, pady=(0, 4))
        ctk.CTkLabel(
            on_panel,
            text="示例 09:00",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
            height=14,
        ).pack(fill="x", padx=12, pady=(0, 10))

        off_panel = self._create_time_input_panel(
            time_frame, "下班时间", "恢复自动监控", "#8b5cf6"
        )
        off_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._off_work_entry = self._create_time_entry(off_panel)
        self._off_work_entry.insert(0, config.get("off_work_time", "18:30"))
        self._off_work_entry.pack(fill="x", padx=12, pady=(0, 4))
        ctk.CTkLabel(
            off_panel,
            text="示例 18:30",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
            height=14,
        ).pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(
            card2,
            text="支持 24 小时制，建议将上下班时间设置为你的日常工作时段。",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(12, 0))

        card3 = self._create_card(
            content,
            "⏰  提醒倒计时",
            ACCENT_ORANGE,
            "倒计时结束后自动息屏，期间可随时取消",
        )
        slider_row3 = self._create_value_row(card3)
        slider_row3.pack(pady=(0, 6))
        self._create_inline_hint(slider_row3, "提醒停留时长", ACCENT_ORANGE).pack(
            side="left", padx=(0, 12)
        )
        self._countdown_value_label = self._create_value_badge(
            slider_row3,
            f"{config.get('toast_countdown', 30):2d} 秒",
            ACCENT_ORANGE,
            "#fff3e8",
        )
        self._countdown_value_label.pack(side="right")

        self._countdown_slider = ctk.CTkSlider(
            card3,
            from_=COUNTDOWN_MIN,
            to=COUNTDOWN_MAX,
            number_of_steps=COUNTDOWN_MAX - COUNTDOWN_MIN,
            height=18,
            button_color=ACCENT_ORANGE,
            button_hover_color="#dd6b20",
            progress_color=ACCENT_ORANGE,
            fg_color="#e2e8f0",
            command=self._on_countdown_change,
        )
        self._countdown_slider.set(config.get("toast_countdown", 30))
        self._countdown_slider.pack(fill="x", pady=(8, 6))

        ctk.CTkLabel(
            card3,
            text=f"最短 {COUNTDOWN_MIN} 秒，最长 {COUNTDOWN_MAX} 秒",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        card4 = self._create_card(
            content,
            "🚀  开机自启动",
            ACCENT_GREEN,
            "开机后自动在后台运行",
        )
        auto_frame = ctk.CTkFrame(
            card4,
            fg_color="#f7fbf8",
            corner_radius=12,
            border_width=1,
            border_color="#d9efe2",
        )
        auto_frame.pack(fill="x", pady=(4, 0))

        auto_text_frame = ctk.CTkFrame(auto_frame, fg_color="transparent")
        auto_text_frame.pack(side="left", fill="x", expand=True, padx=14, pady=12)

        ctk.CTkLabel(
            auto_text_frame,
            text="随系统启动",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            auto_text_frame,
            text="开启后将在系统启动时自动加载，无需手动运行。",
            font=(FONT_FAMILY, 10),
            text_color="#64748b",
            anchor="w",
            justify="left",
        ).pack(fill="x", pady=(6, 0))

        self._auto_start_status_label = ctk.CTkLabel(
            auto_frame,
            text="已关闭",
            height=26,
            corner_radius=13,
            fg_color="#eef2f7",
            text_color="#64748b",
            font=(FONT_FAMILY, 11, "bold"),
            padx=10,
        )
        self._auto_start_status_label.pack(side="right", padx=(10, 12), pady=12)

        self._auto_start_switch = ctk.CTkSwitch(
            auto_frame,
            text="",
            width=44,
            button_color=ACCENT_GREEN,
            button_hover_color="#38a169",
            progress_color=ACCENT_GREEN,
            fg_color="#e2e8f0",
            command=self._update_auto_start_status,
        )
        if config.get("auto_start", False):
            self._auto_start_switch.select()
        self._auto_start_switch.pack(side="right", padx=(0, 10), pady=12)
        self._update_auto_start_status()

        # 底部操作区
        bottom = ctk.CTkFrame(
            window,
            fg_color=BG_COLOR,
            height=70,
            border_width=1,
            border_color="#e6ebf5",
        )
        bottom.pack(side="bottom", fill="x", padx=24, pady=(12, 12))
        bottom.pack_propagate(False)

        btn_container = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_container.pack(expand=True, fill="both", padx=6)

        ctk.CTkLabel(
            btn_container,
            text="修改配置后将立即应用到后台监控逻辑。",
            font=(FONT_FAMILY, 10),
            text_color="#475569",
            anchor="w",
        ).pack(side="left", fill="x", expand=True, padx=(16, 0), pady=(0, 4))

        close_btn = ctk.CTkButton(
            btn_container,
            text="关闭",
            width=88,
            height=36,
            font=(FONT_FAMILY, 13),
            fg_color=BTN_CANCEL,
            hover_color="#cbd5e0",
            text_color=BTN_CANCEL_TEXT,
            corner_radius=RADIUS_BUTTON,
            command=self._on_close,
        )
        close_btn.pack(side="right", padx=(12, 12), pady=16)

        save_btn = ctk.CTkButton(
            btn_container,
            text="💾  保存设置",
            width=140,
            height=36,
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=ACCENT_PURPLE,
            hover_color="#5a67d8",
            text_color=TEXT_WHITE,
            corner_radius=RADIUS_BUTTON,
            command=self._on_save,
        )
        save_btn.pack(side="right", pady=16)

        # 最后 pack content 填充剩余所有空间，保证不与 bottom 重叠
        content.pack(side="top", fill="both", expand=True, padx=24, pady=(12, 0))

    def _create_card(
        self, parent, title: str, accent_color: str, description: str = ""
    ):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG_COLOR,
            corner_radius=RADIUS_CARD,
            border_width=1,
            border_color="#e7ebf3",
        )
        card.pack(fill="x", pady=(0, 10))

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(14, 10))

        title_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_row.pack(fill="x")

        # 计算竖线高度：如果有描述，竖线需要更长
        bar_height = 36 if description else 18

        color_bar = ctk.CTkFrame(
            title_row,
            fg_color=accent_color,
            width=4,
            height=bar_height,
            corner_radius=2,
        )
        color_bar.pack(side="left", padx=(0, 10), anchor="n")

        # 标题和描述的容器
        text_container = ctk.CTkFrame(title_row, fg_color="transparent")
        text_container.pack(side="left", fill="x", expand=True)

        title_label = ctk.CTkLabel(
            text_container,
            text=title,
            font=(FONT_FAMILY, 14, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            height=20,
        )
        title_label.pack(fill="x")

        if description:
            desc_label = ctk.CTkLabel(
                text_container,
                text=description,
                font=(FONT_FAMILY, 11),
                text_color="#64748b",
                anchor="w",
                justify="left",
                height=16,
            )
            desc_label.pack(fill="x", pady=(2, 0))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(0, 10))
        return body

    def _create_value_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        return row

    def _create_inline_hint(self, parent, text: str, accent_color: str):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=accent_color,
            anchor="w",
        )

    def _create_value_badge(self, parent, text: str, text_color: str, bg_color: str):
        return ctk.CTkLabel(
            parent,
            text=text,
            height=30,
            corner_radius=15,
            fg_color=bg_color,
            text_color=text_color,
            font=(FONT_FAMILY_NUM, 13, "bold"),
            padx=14,
        )

    def _create_time_input_panel(
        self, parent, title: str, description: str, accent_color: str
    ):
        panel = ctk.CTkFrame(
            parent,
            fg_color="#f8fafc",
            corner_radius=10,
            border_width=1,
            border_color="#e6ebf5",
        )
        title_label = ctk.CTkLabel(
            panel,
            text=title,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
            height=18,
        )
        title_label.pack(fill="x", padx=12, pady=(10, 2))

        desc_label = ctk.CTkLabel(
            panel,
            text=description,
            font=(FONT_FAMILY, 10),
            text_color="#5b21b6",
            anchor="w",
            height=14,
        )
        desc_label.pack(fill="x", padx=12, pady=(0, 6))
        return panel

    def _create_time_entry(self, parent):
        """创建带验证的时间输入框"""
        # 注册验证函数
        vcmd = (
            self._window.register(self._validate_time_input),
            "%P",  # 允许后的值
        )
        return ctk.CTkEntry(
            parent,
            height=36,
            font=(FONT_FAMILY_NUM, 15, "bold"),
            justify="center",
            fg_color="#ffffff",
            border_color="#d7deeb",
            border_width=1,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            validate="key",
            validatecommand=vcmd,
        )

    def _validate_time_input(self, new_value):
        """验证时间输入：只允许数字和冒号，最大长度 5"""
        if new_value == "":
            return True
        # 只允许数字和冒号
        if not all(c.isdigit() or c == ":" for c in new_value):
            return False
        # 限制长度为 5 (HH:MM)
        if len(new_value) > 5:
            return False
        return True

    def _update_auto_start_status(self):
        enabled = self._auto_start_switch.get() == 1
        self._auto_start_status_label.configure(
            text="已开启" if enabled else "已关闭",
            fg_color="#dcfce7" if enabled else "#eef2f7",
            text_color="#2f855a" if enabled else "#64748b",
        )

    def _on_idle_change(self, value):
        """无操作时间滑块变化"""
        self._idle_value_label.configure(text=f"{int(value):2d} 分钟")

    def _on_countdown_change(self, value):
        """倒计时滑块变化"""
        self._countdown_value_label.configure(text=f"{int(value):2d} 秒")

    def _on_save(self):
        """保存设置，弹出提示框"""
        updates = {
            "idle_timeout": int(self._idle_slider.get()),
            "on_work_time": self._on_work_entry.get().strip(),
            "off_work_time": self._off_work_entry.get().strip(),
            "toast_countdown": int(self._countdown_slider.get()),
            "auto_start": self._auto_start_switch.get() == 1,
        }

        self.config.update(updates)

        try:
            from src.autostart import AutoStart
        except ImportError:
            from autostart import AutoStart

        AutoStart.set_enabled(updates["auto_start"])

        if self.on_save:
            self.on_save(updates)

        self._show_save_popup()

    def _show_save_popup(self):
        """弹出位于中心位置的保存成功提示"""
        if self._window is None:
            return

        popup = ctk.CTkToplevel(self._window)
        popup.title("")
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        # 使用与主窗口一致的浅色背景，避免透明色报错
        popup.configure(fg_color="#f8fafc")

        self._window.update_idletasks()
        window_x = self._window.winfo_rootx()
        window_y = self._window.winfo_rooty()
        window_w = self._window.winfo_width()
        window_h = self._window.winfo_height()

        popup_w = 300
        popup_h = 100
        x = window_x + (window_w - popup_w) // 2
        y = window_y + (window_h - popup_h) // 2 - 54

        if x < 0 or y < 0:
            return

        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        main_frame = ctk.CTkFrame(
            popup,
            fg_color="#ffffff",
            corner_radius=14,
            border_width=1,
            border_color="#e5eaf4",
        )
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both", padx=20, pady=12)

        icon_frame = ctk.CTkFrame(
            content_frame,
            fg_color=ACCENT_GREEN,
            width=38,
            height=38,
            corner_radius=19,
        )
        icon_frame.pack(side="left", padx=(0, 12))
        icon_frame.pack_propagate(False)

        ctk.CTkLabel(
            icon_frame,
            text="✓",
            font=(FONT_FAMILY, 20, "bold"),
            text_color="#ffffff",
        ).pack(expand=True)

        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            text_frame,
            text="保存成功",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            text_frame,
            text="设置已应用到当前监控配置",
            font=(FONT_FAMILY, 11),
            text_color="#64748b",
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        def fade_out(alpha):
            if not popup or not popup.winfo_exists():
                return
            if alpha > 0:
                alpha -= 0.08
                popup.attributes("-alpha", alpha)
                popup.after(25, lambda: fade_out(alpha))
            else:
                popup.destroy()

        popup.after(1800, lambda: fade_out(1.0))

    def _on_close(self):
        """关闭设置窗口，安全销毁避免 TclError"""
        self._is_showing = False
        if self._window:
            win = self._window
            self._window = None
            try:
                # 解除关闭回调，防止重复触发
                win.protocol("WM_DELETE_WINDOW", lambda: None)
                # 先隐藏窗口，阻止后续重绘事件
                win.withdraw()
            except Exception:
                pass
            try:
                # 延迟销毁，让待处理的异步重绘事件自然失效
                win.after(100, win.destroy)
            except Exception:
                try:
                    win.destroy()
                except Exception:
                    pass

    @property
    def is_showing(self):
        return self._is_showing
