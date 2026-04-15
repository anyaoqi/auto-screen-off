"""
系统托盘模块
使用 pystray 实现系统托盘图标管理，提供右键菜单。
"""

import pystray
from pystray import MenuItem as Item, Menu
from PIL import Image
import os
import threading


class TrayIcon:
    """
    系统托盘图标管理器。

    菜单项：
    - 设置
    - 立即息屏
    - 暂停/恢复检测
    - 退出
    """

    def __init__(
        self,
        on_settings=None,
        on_screen_off=None,
        on_pause=None,
        on_resume=None,
        on_quit=None,
    ):
        """
        初始化系统托盘。

        Args:
            on_settings: 打开设置回调
            on_screen_off: 立即息屏回调
            on_pause: 暂停检测回调
            on_resume: 恢复检测回调
            on_quit: 退出程序回调
        """
        self.on_settings = on_settings
        self.on_screen_off = on_screen_off
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_quit = on_quit

        self._icon = None
        self._is_paused = False
        self._status_text = "加载中..."

    def _load_icon(self) -> Image.Image:
        """加载托盘图标"""
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "resources", "icon.png"
        )
        if os.path.exists(icon_path):
            try:
                return Image.open(icon_path).resize((64, 64))
            except Exception:
                pass

        # 如果图标文件不存在，创建一个简单的默认图标
        img = Image.new("RGBA", (64, 64), (102, 126, 234, 255))
        return img

    def _build_menu(self):
        """构建右键菜单"""
        pause_text = "▶️ 恢复检测" if self._is_paused else "⏸️ 暂停检测"
        pause_action = self._handle_resume if self._is_paused else self._handle_pause

        return Menu(
            Item(f"📋 {self._status_text}", None, enabled=False),
            Menu.SEPARATOR,
            Item("⚙️ 设置", self._handle_settings, default=True),
            Item("🖥️ 立即息屏", self._handle_screen_off),
            Menu.SEPARATOR,
            Item(pause_text, pause_action),
            Menu.SEPARATOR,
            Item("❌ 退出", self._handle_quit),
        )

    def start(self):
        """启动系统托盘（阻塞调用，通常在子线程运行）"""
        icon_image = self._load_icon()
        self._icon = pystray.Icon(
            name="AutoScreenOff",
            icon=icon_image,
            title="小黑 - 自动息屏助手",
            menu=self._build_menu(),
        )

        # 单击打开设置
        self._icon.on_click = self._handle_settings

        self._icon.run()

    def stop(self):
        """停止系统托盘"""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_status(self, text: str):
        """更新状态文字"""
        self._status_text = text
        self._refresh_menu()

    def set_paused(self, paused: bool):
        """设置暂停状态"""
        self._is_paused = paused
        self._refresh_menu()

    def _refresh_menu(self):
        """刷新菜单"""
        if self._icon:
            self._icon.menu = self._build_menu()
            self._icon.update_menu()

    def _handle_settings(self, icon=None, item=None):
        """处理设置菜单/单击事件"""
        if self.on_settings:
            self.on_settings()

    def _handle_screen_off(self, icon=None, item=None):
        """处理立即息屏"""
        if self.on_screen_off:
            self.on_screen_off()

    def _handle_pause(self, icon=None, item=None):
        """处理暂停检测"""
        self._is_paused = True
        self._refresh_menu()
        if self.on_pause:
            self.on_pause()

    def _handle_resume(self, icon=None, item=None):
        """处理恢复检测"""
        self._is_paused = False
        self._refresh_menu()
        if self.on_resume:
            self.on_resume()

    def _handle_quit(self, icon=None, item=None):
        """处理退出"""
        self.stop()
        if self.on_quit:
            self.on_quit()

    @property
    def is_paused(self):
        return self._is_paused
