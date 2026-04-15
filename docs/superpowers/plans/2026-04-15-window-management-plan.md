# 窗口管理优化实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复窗口最小化恢复、实现单例控制防止重复启动、优化启动时自动打开设置窗口

**Architecture:** 通过 Windows 互斥量实现单例模式，在 SettingsWindow 中增加窗口恢复方法，在应用启动时延迟打开设置窗口

**Tech Stack:** Python, customtkinter, pystray, pywin32, Windows API

---

## 文件映射

| 文件 | 操作 | 职责 |
|------|------|------|
| `src/main.py` | 修改 | 添加单例检测、启动时打开设置窗口、优化 `_open_settings` 逻辑 |
| `src/settings_window.py` | 修改 | 添加 `restore()` 方法用于恢复最小化窗口 |
| `requirements.txt` | 修改 | 添加 pywin32 依赖 |
| `tests/test_window_management.py` | 创建 | 测试窗口管理功能 |

---

### Task 1: 添加 pywin32 依赖

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: 添加 pywin32 依赖**

在 `requirements.txt` 末尾添加：
```
pywin32>=306
```

- [ ] **Step 2: 安装依赖**

```bash
pip install pywin32>=306
```

---

### Task 2: 实现单例检测功能

**Files:**
- Modify: `src/main.py:1-40` (imports 部分)
- Test: `tests/test_singleton.py`

- [ ] **Step 1: 编写单例检测测试**

创建 `tests/test_singleton.py`:
```python
"""测试单例检测功能"""
import pytest
import sys
import os

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_mutex_import_available():
    """测试 win32event 和 win32api 可以导入"""
    try:
        import win32event
        import win32api
        assert win32event is not None
        assert win32api is not None
    except ImportError:
        pytest.skip("pywin32 not installed")


def test_is_already_running_function_exists():
    """测试 is_already_running 函数存在于 main.py"""
    from src.main import is_already_running
    assert callable(is_already_running)


def test_is_already_running_returns_false_first_time():
    """测试第一次运行时返回 False"""
    try:
        from src.main import is_already_running
        # 第一次调用应该返回 False（没有已运行的实例）
        result = is_already_running()
        assert result == False
    except ImportError:
        pytest.skip("pywin32 not installed")
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_singleton.py -v
```

预期：测试失败，因为 `is_already_running` 函数还不存在

- [ ] **Step 3: 在 main.py 添加单例检测代码**

修改 `src/main.py`，在文件开头添加导入：
```python
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
        print("[Main] 警告: pywin32 未安装，无法进行单例检测")
        return False
    
    try:
        _global_mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
        last_error = win32api.GetLastError()
        
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            print("[Main] 检测到程序已在运行")
            win32api.CloseHandle(_global_mutex)
            _global_mutex = None
            return True
        
        return False
    except Exception as e:
        print(f"[Main] 单例检测异常: {e}")
        return False
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_singleton.py -v
```

预期：所有测试通过

- [ ] **Step 5: 提交**

```bash
git add requirements.txt src/main.py tests/test_singleton.py
git commit -m "feat: 添加 Windows 单例检测功能"
```

---

### Task 3: 在应用启动时添加单例检查

**Files:**
- Modify: `src/main.py:316-323` (main 函数)

- [ ] **Step 1: 修改 main 函数添加单例检查**

修改 `src/main.py` 的 `main()` 函数：
```python
def main():
    """程序入口"""
    # 检查是否已有实例在运行
    if is_already_running():
        print("[Main] 程序已在运行，退出当前实例")
        sys.exit(0)
    
    print("[Main] 启动新的应用实例")
    app = AutoScreenOffApp()
    app.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 手动测试单例功能**

1. 运行应用：`python src/main.py`
2. 再次运行：`python src/main.py`
3. 验证第二次运行时立即退出

- [ ] **Step 3: 提交**

```bash
git add src/main.py
git commit -m "feat: 在启动时检查单例"
```

---

### Task 4: 添加窗口恢复方法

**Files:**
- Modify: `src/settings_window.py:50-56` (show 方法附近)
- Test: `tests/test_window_management.py`

- [ ] **Step 1: 编写窗口恢复测试**

创建 `tests/test_window_management.py`:
```python
"""测试窗口管理功能"""
import pytest
import sys
import os

# 确保项目根目录在 path 中
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_settings_window_has_restore_method():
    """测试 SettingsWindow 有 restore 方法"""
    from src.settings_window import SettingsWindow
    
    # 检查方法存在
    assert hasattr(SettingsWindow, 'restore')
    assert callable(getattr(SettingsWindow, 'restore'))


def test_restore_method_signature():
    """测试 restore 方法签名正确"""
    from src.settings_window import SettingsWindow
    import inspect
    
    # 检查方法参数
    sig = inspect.signature(SettingsWindow.restore)
    params = list(sig.parameters.keys())
    assert 'self' in params
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_window_management.py -v
```

预期：测试失败，因为 `restore` 方法还不存在

- [ ] **Step 3: 在 SettingsWindow 中添加 restore 方法**

修改 `src/settings_window.py`，在 `show()` 方法后添加：
```python
def restore(self):
    """
    恢复最小化的窗口。
    如果窗口存在但被最小化，则恢复并置顶显示。
    """
    if self._window and self._is_showing:
        try:
            # 检测窗口是否最小化
            if self._window.state() == 'iconic':
                self._window.deiconify()  # 恢复窗口
            
            # 置顶并获取焦点
            self._window.lift()
            self._window.focus_force()
            self._window.attributes('-topmost', True)
        except Exception as e:
            print(f"[SettingsWindow] 恢复窗口失败: {e}")
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_window_management.py -v
```

预期：所有测试通过

- [ ] **Step 5: 提交**

```bash
git add src/settings_window.py tests/test_window_management.py
git commit -m "feat: 添加窗口恢复方法"
```

---

### Task 5: 优化 _open_settings 方法支持窗口恢复

**Files:**
- Modify: `src/main.py:227-245` (_open_settings 方法)

- [ ] **Step 1: 修改 _open_settings 方法**

修改 `src/main.py` 的 `_open_settings` 方法：
```python
def _open_settings(self):
    """打开设置窗口"""
    def _create_or_restore():
        # 如果窗口存在且正在显示，尝试恢复（从最小化状态）
        if self._settings_window and self._settings_window._window:
            try:
                # 检查窗口是否最小化
                if self._settings_window._window.state() == 'iconic':
                    self._settings_window.restore()
                    return
                # 窗口正常显示，置顶
                self._settings_window._window.lift()
                self._settings_window._window.focus_force()
                return
            except Exception:
                pass
        
        # 窗口不存在或未显示，创建新窗口
        self._settings_window = SettingsWindow(
            config_manager=self.config,
            on_save=self._on_settings_save,
        )
        self._settings_window.show()

    if self._root:
        self._root.after(0, _create_or_restore)
```

- [ ] **Step 2: 提交**

```bash
git add src/main.py
git commit -m "feat: 优化 _open_settings 支持窗口恢复和置顶"
```

---

### Task 6: 启动时自动打开设置窗口

**Files:**
- Modify: `src/main.py:72-106` (run 方法)

- [ ] **Step 1: 修改 run 方法添加启动时打开设置窗口**

修改 `src/main.py` 的 `run()` 方法，在 `self._root.mainloop()` 前添加：
```python
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

    # 延迟 500ms 打开设置窗口，确保主窗口和托盘已初始化
    self._root.after(500, self._open_settings)

    # 运行 tkinter 事件循环
    self._root.mainloop()
```

- [ ] **Step 2: 手动测试启动行为**

```bash
python src/main.py
```

预期：应用启动后 500ms 自动打开设置窗口

- [ ] **Step 3: 提交**

```bash
git add src/main.py
git commit -m "feat: 启动时自动打开设置窗口"
```

---

### Task 7: 完整测试和验证

**Files:**
- 所有修改的文件

- [ ] **Step 1: 运行所有测试**

```bash
pytest tests/ -v
```

预期：所有测试通过

- [ ] **Step 2: 手动测试完整流程**

1. **测试单例**: 
   - 启动应用
   - 再次启动，验证不会打开新实例

2. **测试窗口恢复**:
   - 最小化设置窗口
   - 点击托盘图标，验证窗口恢复并置顶

3. **测试启动行为**:
   - 关闭应用
   - 重新启动，验证设置窗口自动打开

- [ ] **Step 3: 最终提交**

```bash
git add -A
git commit -m "feat: 完成窗口管理优化 - 单例控制、窗口恢复、启动行为"
```

---

## 测试总结

| 测试项 | 文件 | 状态 |
|--------|------|------|
| 单例检测 | `tests/test_singleton.py` | 3 个测试 |
| 窗口恢复 | `tests/test_window_management.py` | 2 个测试 |
| 手动测试 | 完整流程 | 3 个场景 |

## 注意事项

1. **Windows 依赖**: pywin32 仅在 Windows 平台可用，代码中已添加 try-except 处理
2. **向后兼容**: 如果 pywin32 未安装，单例检测会跳过并打印警告
3. **窗口状态**: 使用 `state() == 'iconic'` 检测最小化状态
4. **延迟打开**: 使用 `after(500, ...)` 确保初始化完成后再打开设置窗口
