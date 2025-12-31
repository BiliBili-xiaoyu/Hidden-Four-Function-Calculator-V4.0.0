@echo off
chcp 65001 >nul
echo.
echo ========================================
echo     四则计算器 v4.0.0 打包工具
echo ========================================
echo 作者: B站-爱好中的烦恼
echo 版本: 4.0.0
echo 年份: 2025
echo ========================================
echo.

REM 检查Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查是否在项目目录
if not exist "Calculator.py" (
    echo 错误: 请在项目目录中运行此脚本
    echo 项目目录应该包含 Calculator.py 文件
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)

echo 检查依赖...
pip install pyinstaller keyboard pillow --upgrade
if %errorlevel% neq 0 (
    echo 安装依赖失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo 开始打包...
echo.

REM 清理旧的构建文件
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
if exist "Calculator.spec" del Calculator.spec

REM 打包命令
set PYINSTALLER_CMD=pyinstaller --onefile --windowed --name Calculator --clean --noconfirm

REM 检查图标
if exist "calculator.ico" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --icon=calculator.ico
    echo 使用自定义图标...
) else (
    echo 使用默认图标...
)

REM 执行打包
%PYINSTALLER_CMD% --add-data ".;." --hidden-import keyboard --hidden-import json --hidden-import ctypes --hidden-import tkinter Calculator.py

if %errorlevel% neq 0 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo           🎉 打包成功！ 🎉
echo ========================================
echo.

REM 检查生成的文件
if exist "dist\Calculator.exe" (
    for %%F in ("dist\Calculator.exe") do (
        set "size=%%~zF"
        set /a size_mb=size/1048576
        set /a size_kb=(size%%1048576)/1024
        echo 生成文件: %cd%\dist\Calculator.exe
        echo 文件大小: !size_mb! MB !size_kb! KB
    )
    
    REM 复制其他文件
    if exist "calculator_settings.json" (
        copy "calculator_settings.json" "dist\" >nul
        echo 已复制: calculator_settings.json
    )
    
    if exist "README.md" (
        copy "README.md" "dist\" >nul
        echo 已复制: README.md
    )
    
    echo.
    echo 📋 使用方法:
    echo 1. 打开 dist 文件夹
    echo 2. 双击 Calculator.exe 运行
    echo 3. 首次运行可能需要授予管理员权限
    echo.
    echo 按任意键打开dist文件夹...
    pause >nul
    start "" "dist"
) else (
    echo 错误：未找到生成的可执行文件
    pause
)

REM 保持窗口打开
echo.
echo 按任意键退出...
pause >nul