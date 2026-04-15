"""
配置管理模块
负责读写JSON配置文件，提供配置存取接口。
配置文件位于 ~/.auto-screen-off/config.json
"""

import json
import os
import shutil


# 默认配置
DEFAULT_CONFIG = {
    "idle_timeout": 10,          # 无操作息屏时间（分钟）
    "off_work_time": "18:30",    # 下班时间
    "on_work_time": "09:00",     # 上班时间
    "toast_countdown": 30,       # 提醒倒计时（秒）
    "auto_start": False          # 开机自启
}

# 配置文件目录
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".auto-screen-off")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._config = {}
        self._load()

    def _ensure_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)

    def _load(self):
        """从文件加载配置"""
        self._ensure_dir()

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._config = {}

        # 合并默认配置（补全缺失项）
        for key, value in DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value

        # 保存一次，确保文件完整
        self.save()

    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key, value):
        """设置配置项"""
        self._config[key] = value
        self.save()

    def update(self, updates: dict):
        """批量更新配置"""
        self._config.update(updates)
        self.save()

    def get_all(self) -> dict:
        """获取所有配置"""
        return self._config.copy()

    def save(self):
        """保存配置到文件"""
        self._ensure_dir()
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[Config] 保存配置失败: {e}")

    def reset(self):
        """重置为默认配置"""
        self._config = DEFAULT_CONFIG.copy()
        self.save()
