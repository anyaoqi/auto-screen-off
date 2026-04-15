"""
配置管理模块测试
"""

import json
import os
import sys
import tempfile
import pytest
from unittest.mock import patch

# 将项目根目录加入 path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.config import ConfigManager, DEFAULT_CONFIG, CONFIG_DIR, CONFIG_FILE


class TestConfigManager:
    """测试配置管理器"""

    def setup_method(self):
        """每个测试前备份配置"""
        self._backup = None
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self._backup = f.read()

    def teardown_method(self):
        """每个测试后恢复配置"""
        if self._backup is not None:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(self._backup)

    def test_default_config_loaded(self):
        """测试默认配置加载"""
        config = ConfigManager()
        for key, value in DEFAULT_CONFIG.items():
            assert config.get(key) is not None

    def test_get_existing_key(self):
        """测试获取已有配置项"""
        config = ConfigManager()
        assert config.get("idle_timeout") == DEFAULT_CONFIG["idle_timeout"]

    def test_get_missing_key_with_default(self):
        """测试获取不存在的配置项（带默认值）"""
        config = ConfigManager()
        assert config.get("nonexistent", "fallback") == "fallback"

    def test_get_missing_key_without_default(self):
        """测试获取不存在的配置项（无默认值）"""
        config = ConfigManager()
        assert config.get("nonexistent") is None

    def test_set_and_get(self):
        """测试设置并获取配置项"""
        config = ConfigManager()
        config.set("idle_timeout", 20)
        assert config.get("idle_timeout") == 20

    def test_update_multiple_keys(self):
        """测试批量更新"""
        config = ConfigManager()
        config.update({
            "idle_timeout": 15,
            "toast_countdown": 45,
        })
        assert config.get("idle_timeout") == 15
        assert config.get("toast_countdown") == 45

    def test_get_all(self):
        """测试获取所有配置"""
        config = ConfigManager()
        all_config = config.get_all()
        assert isinstance(all_config, dict)
        assert "idle_timeout" in all_config
        assert "off_work_time" in all_config

    def test_get_all_returns_copy(self):
        """测试 get_all 返回副本，不影响内部状态"""
        config = ConfigManager()
        all_config = config.get_all()
        all_config["idle_timeout"] = 999
        assert config.get("idle_timeout") != 999

    def test_save_and_reload(self):
        """测试保存后重新加载"""
        config = ConfigManager()
        config.set("idle_timeout", 25)
        config.save()

        # 重新创建实例，应该从文件加载
        config2 = ConfigManager()
        assert config2.get("idle_timeout") == 25

    def test_reset_to_default(self):
        """测试重置为默认配置"""
        config = ConfigManager()
        config.set("idle_timeout", 99)
        config.reset()
        assert config.get("idle_timeout") == DEFAULT_CONFIG["idle_timeout"]

    def test_config_file_created(self):
        """测试配置文件是否自动创建"""
        config = ConfigManager()
        assert os.path.exists(CONFIG_FILE)

    def test_config_dir_created(self):
        """测试配置目录是否自动创建"""
        config = ConfigManager()
        assert os.path.exists(CONFIG_DIR)

    def test_valid_json_file(self):
        """测试配置文件是有效的 JSON"""
        config = ConfigManager()
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)
