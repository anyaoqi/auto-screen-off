"""
PyInstaller 打包脚本
将项目打包为单个可执行文件 (.exe)。

用法:
    python build.py              # 从 VERSION 文件读取版本
    python build.py --version 0.1.0  # 指定版本号
"""

import PyInstaller.__main__
import os
import argparse

# 项目根目录
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_version():
    """从 VERSION 文件读取版本号"""
    version_file = os.path.join(ROOT_DIR, "VERSION")
    if os.path.exists(version_file):
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0.0.0"


def build(version=None):
    """执行打包"""
    if version is None:
        version = get_version()

    app_name = f"小黑-自动息屏助手-v{version}"

    print(f"开始打包...")
    print(f"版本: v{version}")
    print(f"名称: {app_name}")
    print()

    PyInstaller.__main__.run(
        [
            os.path.join(ROOT_DIR, "src", "main.py"),
            f"--name={app_name}",
            "--windowed",  # 无控制台窗口
            f"--icon={os.path.join(ROOT_DIR, 'resources', 'icon.png')}",
            f"--add-data={os.path.join(ROOT_DIR, 'resources')};resources",
            f"--add-data={os.path.join(ROOT_DIR, 'config')};config",
            "--hidden-import=customtkinter",
            "--hidden-import=pystray",
            "--hidden-import=PIL",
            "--hidden-import=PIL._tkinter_finder",
            "--clean",
            "--noconfirm",
            "--onefile",  # 打包为单文件
            f"--distpath={os.path.join(ROOT_DIR, 'dist')}",
            f"--workpath={os.path.join(ROOT_DIR, 'build')}",
            f"--specpath={ROOT_DIR}",
        ]
    )

    print("\n" + "=" * 50)
    print("OK 打包完成!")
    print(f"版本: v{version}")
    print(f"输出: {os.path.join(ROOT_DIR, 'dist', app_name)}.exe")
    print("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="打包小黑-自动息屏助手")
    parser.add_argument(
        "--version", type=str, help="指定版本号 (默认从 VERSION 文件读取)"
    )
    args = parser.parse_args()

    build(version=args.version)
