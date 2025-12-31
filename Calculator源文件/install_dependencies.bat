@echo off
chcp 65001 >nul
title 四则计算器 v4.0.0 - 依赖安装工具
color 0A

echo.
echo ========================================
echo     四则计算器 v4.0.0 依赖安装工具
echo ========================================
echo 作者: B站-爱好中的烦恼
echo 版本: 4.0.0
echo 年份: 2025
echo ========================================
echo 请稍后......                                  预计需要等待85s
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  警告：建议以管理员身份运行此脚本
    echo 这样可以确保全局快捷键功能正常工作
    echo.
    echo 是否继续？(Y/N)
    set /p choice=
    if /i "%choice%" neq "Y" (
        echo 安装已取消
        pause
        exit /b 1
    )
)

echo.
echo 正在检查系统环境...
echo.

REM 检查Python是否已安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未检测到Python
    echo.
    echo 请先安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    echo 安装时请确保勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM 获取Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ 检测到Python版本: %PYTHON_VERSION%

REM 检查pip是否已安装
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  pip未安装或需要更新，正在安装pip...
    python -m ensurepip --upgrade
    if %errorlevel% neq 0 (
        echo ❌ pip安装失败
        pause
        exit /b 1
    )
    echo ✅ pip安装成功
)

echo.
echo 正在更新pip到最新版本...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  pip更新失败，继续安装...
)

echo.
echo ========================================
echo     开始安装依赖包
echo ========================================
echo.

REM 设置国内镜像源（加速下载）
set MIRROR_SOURCE=https://pypi.tuna.tsinghua.edu.cn/simple
set MIRROR_SOURCE2=https://mirrors.aliyun.com/pypi/simple

echo 正在设置国内镜像源以加速下载...
echo.

REM 主要依赖包列表
set DEPENDENCIES=keyboard pyinstaller pillow

REM 安装主要依赖包
echo 📦 安装主要依赖包...
echo.

for %%p in (%DEPENDENCIES%) do (
    echo 正在安装: %%p
    echo ----------------------------------------
    
    REM 尝试第一个镜像源
    python -m pip install %%p -i %MIRROR_SOURCE% --trusted-host pypi.tuna.tsinghua.edu.cn
    
    if %errorlevel% neq 0 (
        echo ⚠️  第一个镜像源失败，尝试第二个...
        python -m pip install %%p -i %MIRROR_SOURCE2% --trusted-host mirrors.aliyun.com
    )
    
    if %errorlevel% neq 0 (
        echo ⚠️  镜像源失败，尝试官方源...
        python -m pip install %%p
    )
    
    if %errorlevel% neq 0 (
        echo ❌ 安装失败: %%p
    ) else (
        echo ✅ 安装成功: %%p
    )
    echo.
)

echo.
echo ========================================
echo     可选依赖包安装
echo ========================================
echo.

REM 可选依赖包（用于图标生成等）
set OPTIONAL_DEPENDENCIES=numpy

echo 是否安装可选依赖包？(Y/N)
set /p install_optional=

if /i "%install_optional%"=="Y" (
    echo.
    echo 📦 安装可选依赖包...
    echo.
    
    for %%p in (%OPTIONAL_DEPENDENCIES%) do (
        echo 正在安装: %%p
        echo ----------------------------------------
        python -m pip install %%p -i %MIRROR_SOURCE% --trusted-host pypi.tuna.tsinghua.edu.cn
        
        if %errorlevel% neq 0 (
            python -m pip install %%p
        )
        
        if %errorlevel% neq 0 (
            echo ⚠️  安装失败: %%p
        ) else (
            echo ✅ 安装成功: %%p
        )
        echo.
    )
)

echo.
echo ========================================
echo     验证安装结果
echo ========================================
echo.

echo 正在验证依赖包是否安装成功...
echo.

set VERIFY_FAILED=0

REM 验证主要依赖
for %%p in (%DEPENDENCIES%) do (
    python -c "import %%p" 2>nul
    if %errorlevel% neq 0 (
        echo ❌ 验证失败: %%p
        set VERIFY_FAILED=1
    ) else (
        echo ✅ 验证成功: %%p
    )
)

echo.
echo ========================================
echo     创建虚拟环境（可选）
echo ========================================
echo.

echo 是否创建虚拟环境？(Y/N)
echo 虚拟环境可以隔离项目依赖，避免冲突
set /p create_venv=

if /i "%create_venv%"=="Y" (
    echo.
    echo 正在创建虚拟环境...
    
    REM 检查是否已存在虚拟环境
    if exist "venv" (
        echo ⚠️  虚拟环境已存在，是否重新创建？(Y/N)
        set /p recreate_venv=
        if /i "%recreate_venv%"=="Y" (
            rmdir /s /q venv
            python -m venv venv
            if %errorlevel% neq 0 (
                echo ❌ 虚拟环境创建失败
            ) else (
                echo ✅ 虚拟环境创建成功
            )
        ) else (
            echo ℹ️  使用现有虚拟环境
        )
    ) else (
        python -m venv venv
        if %errorlevel% neq 0 (
            echo ❌ 虚拟环境创建失败
        ) else (
            echo ✅ 虚拟环境创建成功
            
            echo.
            echo 激活虚拟环境的命令：
            echo.
            echo 对于CMD：
            echo   venv\Scripts\activate.bat
            echo.
            echo 对于PowerShell：
            echo   venv\Scripts\Activate.ps1
            echo.
            echo 对于Git Bash：
            echo   source venv/Scripts/activate
        )
    )
)

echo.
echo ========================================
echo     创建配置文件
echo ========================================
echo.

REM 检查是否存在配置文件
if exist "calculator_settings.json" (
    echo ℹ️  配置文件已存在：calculator_settings.json
) else (
    echo 正在创建默认配置文件...
    
    (
    echo {
    echo     "hide_hotkey": "ctrl+shift+h",
    echo     "show_hotkey": "ctrl+shift+s",
    echo     "version": "4.0.0",
    echo     "author": "B站-爱好中的烦恼"
    echo }
    ) > calculator_settings.json
    
    if exist "calculator_settings.json" (
        echo ✅ 配置文件创建成功
    ) else (
        echo ❌ 配置文件创建失败
    )
)

echo.
echo ========================================
echo     创建requirements.txt
echo ========================================
echo.

echo 正在创建requirements.txt文件...
(
echo keyboard>=0.13.5
echo pyinstaller>=5.0.0
echo pillow>=9.0.0
) > requirements.txt

if exist "requirements.txt" (
    echo ✅ requirements.txt创建成功
) else (
    echo ❌ requirements.txt创建失败
)

echo.
echo ========================================
echo     安装结果汇总
echo ========================================
echo.

if %VERIFY_FAILED%==0 (
    echo 🎉 所有主要依赖安装成功！
    echo.
    echo 📋 已安装的包：
    echo.
    python -m pip list --format=columns ^| findstr /i "keyboard pyinstaller pillow"
) else (
    echo ⚠️  部分依赖安装失败
    echo 请尝试以下方法：
    echo 1. 以管理员身份重新运行此脚本
    echo 2. 手动安装：pip install keyboard pyinstaller pillow
    echo 3. 检查网络连接
)

echo.
echo ========================================
echo     下一步操作指南
echo ========================================
echo.

echo 📋 使用方法：
echo.
echo 1. 运行计算器：
echo    python Calculator.py
echo.
echo 2. 打包成EXE：
echo    运行 build.bat 或使用命令：
echo    pyinstaller --onefile --windowed Calculator.py
echo.
echo 3. 图标生成：
echo    运行 create_icon.py 生成程序图标
echo.
echo 4. 快捷键设置：
echo    运行程序后点击右上角 ⚙ 按钮
echo    在设置界面中配置快捷键
echo.

echo ⚠️  注意事项：
echo.
echo 1. 首次运行可能需要管理员权限
echo 2. 某些杀毒软件可能误报，请添加到白名单
echo 3. 快捷键功能需要全局键盘钩子权限
echo.

echo 📞 技术支持：
echo 作者：B站-爱好中的烦恼
echo 版本：4.0.0
echo 年份：2025
echo.

echo 按任意键打开项目文件夹...
pause >nul

REM 打开当前文件夹
start "" "%cd%"

echo.
echo 是否打开Python包文档？(Y/N)
set /p open_docs=

if /i "%open_docs%"=="Y" (
    echo.
    echo 正在打开相关文档...
    start "" "https://pypi.org/project/keyboard/"
    timeout /t 2 >nul
    start "" "https://pypi.org/project/pyinstaller/"
    timeout /t 2 >nul
    start "" "https://pypi.org/project/Pillow/"
)

echo.
echo ========================================
echo     安装完成！
echo ========================================
echo.

echo 按任意键退出...
pause >nul