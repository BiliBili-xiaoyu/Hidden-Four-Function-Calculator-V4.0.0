# build_exe.py
import os
import sys
import subprocess
import shutil

def build():
    print("开始打包计算器...")
    
    # 清理旧的构建文件
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    
    # 打包命令
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=Calculator',
        '--clean',
        '--noconfirm',
        '--add-data=.;.',
        '--hidden-import=keyboard',
        '--hidden-import=json',
        '--hidden-import=ctypes',
        '--hidden-import=tkinter',
        '--exclude-module=tkinter.test',
        '--exclude-module=unittest',
        'Calculator.py'
    ]
    
    # 如果有图标文件，添加图标
    if os.path.exists('calculator.ico'):
        cmd.append('--icon=calculator.ico')
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 打包成功！")
        print(f"✅ 生成文件: dist/Calculator.exe")
        
        # 复制配置文件
        if os.path.exists('calculator_settings.json'):
            shutil.copy2('calculator_settings.json', 'dist/calculator_settings.json')
            print("✅ 已复制配置文件")
        
        print("\n📋 使用方法:")
        print("1. 直接运行 dist/Calculator.exe")
        print("2. 不需要安装Python或任何依赖")
        print("3. 首次运行可能需要管理员权限")
        
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")

if __name__ == "__main__":
    build()