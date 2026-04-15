"""
开机自启管理模块
通过 Windows 注册表实现开机自启动。
注册表路径: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
"""

import os
import sys
import winreg


# 注册表路径
REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "AutoScreenOff"


class AutoStart:
    """开机自启管理器"""

    @staticmethod
    def _get_exe_path() -> str:
        """
        获取当前可执行文件的路径。
        如果是打包后的 exe，返回 exe 路径（带 --autostart 参数）；
        如果是 Python 脚本运行，返回 python + 脚本路径（带 --autostart 参数）。
        """
        if getattr(sys, "frozen", False):
            # PyInstaller 打包后的 exe
            return f'"{sys.executable}" --autostart'
        else:
            # Python 脚本运行
            main_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "main.py"
            )
            return f'"{sys.executable}" "{main_script}" --autostart'

    @staticmethod
    def is_enabled() -> bool:
        """
        检查是否已启用开机自启。

        Returns:
            bool: 是否已启用
        """
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(value)
        except FileNotFoundError:
            return False
        except OSError:
            return False

    @staticmethod
    def enable():
        """启用开机自启"""
        try:
            exe_path = AutoStart._get_exe_path()
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        except OSError as e:
            print(f"[AutoStart] 启用开机自启失败: {e}")

    @staticmethod
    def disable():
        """禁用开机自启"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass  # 本来就没有，无需处理
        except OSError as e:
            print(f"[AutoStart] 禁用开机自启失败: {e}")

    @staticmethod
    def set_enabled(enabled: bool):
        """
        设置开机自启状态。

        Args:
            enabled: True 启用，False 禁用
        """
        if enabled:
            AutoStart.enable()
        else:
            AutoStart.disable()
