# 窗口管理优化设计

**日期**: 2026-04-15
**主题**: 修复窗口最小化恢复、单例控制和启动行为

## 问题描述

1. 最小化窗口后点击托盘图标无法恢复窗口
2. 多次双击 exe 会打开多个窗口实例
3. 双击 exe 启动时没有打开设置窗口，用户无法确认应用已启动

## 设计方案

### 1. 窗口最小化恢复

**修改文件**: `src/settings_window.py`

**方案**:
- 在 `SettingsWindow` 类中增加 `restore()` 方法
- 检测窗口状态：如果窗口存在但被最小化（iconified），则调用 `deiconify()` 恢复
- 修改 `main.py` 的 `_open_settings()` 方法，在窗口已显示但最小化时调用 `restore()`

**实现逻辑**:
```python
# settings_window.py
def restore(self):
    """恢复最小化的窗口"""
    if self._window and self._is_showing:
        # 检测窗口是否最小化
        if self._window.state() == 'iconic':
            self._window.deiconify()  # 恢复窗口
        self._window.lift()  # 置顶
        self._window.focus_force()  # 获取焦点
```

### 2. 单例控制（Windows 互斥量）

**修改文件**: `src/main.py`

**方案**:
- 使用 `win32event.CreateMutex` 创建命名互斥量
- 程序启动时检查互斥量是否已存在
- 如果已存在，说明程序已在运行，直接退出新实例
- 程序退出时释放互斥量

**实现逻辑**:
```python
import win32event
import win32api

MUTEX_NAME = "AutoScreenOffAppMutex"

def is_already_running():
    """检查程序是否已在运行"""
    mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
    last_error = win32api.GetLastError()
    
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        win32api.CloseHandle(mutex)
        return True
    
    return False
```

**依赖**: 需要在 `requirements.txt` 中添加 `pywin32`

### 3. 启动时打开设置窗口

**修改文件**: `src/main.py`

**方案**:
- 在 `run()` 方法的最后，调用 `_open_settings()` 显示设置窗口
- 使用 `self._root.after(500, self._open_settings)` 延迟打开，确保主窗口和托盘已初始化

**实现逻辑**:
```python
def run(self):
    # ... 现有初始化代码 ...
    
    # 延迟 500ms 打开设置窗口
    self._root.after(500, self._open_settings)
    
    self._root.mainloop()
```

## 修改的文件

1. `src/main.py` - 添加单例检测和启动时打开设置窗口
2. `src/settings_window.py` - 添加窗口恢复方法
3. `requirements.txt` - 添加 pywin32 依赖

## 测试方案

1. 启动应用，验证设置窗口自动打开
2. 最小化设置窗口，点击托盘图标，验证窗口恢复
3. 双击 exe 启动已运行的应用，验证不会打开新实例
4. 关闭应用后再次启动，验证可以正常打开
