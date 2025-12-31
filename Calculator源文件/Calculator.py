import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
from ctypes import wintypes
import json
import os
import sys
import keyboard
import threading
import time

# 版本信息
VERSION = "4.0.0"
AUTHOR = "B站-爱好中的烦恼"
YEAR = "2025"

# Windows API常量
WS_EX_TOOLWINDOW = 0x00000080
GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000

# 隐藏控制台窗口（仅Windows）
if sys.platform == "win32":
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    # 隐藏当前控制台窗口
    whnd = kernel32.GetConsoleWindow()
    if whnd != 0:
        user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE

# 加载Windows API
user32 = ctypes.windll.user32

class HotkeyRecorder:
    """快捷键录制器"""
    def __init__(self):
        self.recording = False
        self.current_keys = []
        self.recorded_keys = []
        self.callback = None
        self.hook = None
    
    def start_recording(self, callback):
        """开始录制快捷键"""
        self.recording = True
        self.current_keys = []
        self.recorded_keys = []
        self.callback = callback
        
        # 安装全局键盘钩子
        self.hook = keyboard.hook(self.on_key_event)
    
    def stop_recording(self):
        """停止录制快捷键"""
        if self.recording:
            self.recording = False
            if self.hook:
                keyboard.unhook(self.hook)
                self.hook = None
    
    def on_key_event(self, event):
        """处理键盘事件"""
        if not self.recording:
            return
        
        event_type = event.event_type
        key_name = event.name
        
        # 过滤掉重复的key_down事件
        if event_type == 'down':
            if key_name not in self.current_keys:
                self.current_keys.append(key_name)
                self.update_recorded_keys()
        
        elif event_type == 'up':
            if key_name in self.current_keys:
                self.current_keys.remove(key_name)
            
            # 当所有键都抬起时，录制完成
            if not self.current_keys and self.recorded_keys:
                self.recording = False
                if self.hook:
                    keyboard.unhook(self.hook)
                    self.hook = None
                
                if self.callback:
                    self.callback(self.get_hotkey_string())
    
    def update_recorded_keys(self):
        """更新已录制的按键"""
        if self.current_keys:
            # 保持按键顺序：修饰键在前，普通键在后
            modifiers = []
            regular_keys = []
            
            for key in self.current_keys:
                if key in ['ctrl', 'alt', 'shift', 'windows']:
                    modifiers.append(key)
                else:
                    regular_keys.append(key)
            
            # 组合按键：修饰键 + 普通键
            self.recorded_keys = modifiers + regular_keys[:1]  # 只取第一个普通键
    
    def get_hotkey_string(self):
        """获取快捷键字符串"""
        if not self.recorded_keys:
            return ""
        
        # 按键排序：ctrl, alt, shift, windows
        order = {'ctrl': 0, 'alt': 1, 'shift': 2, 'windows': 3}
        sorted_keys = sorted(
            [k for k in self.recorded_keys if k in order],
            key=lambda x: order[x]
        )
        
        # 添加非修饰键
        regular_keys = [k for k in self.recorded_keys if k not in order]
        all_keys = sorted_keys + regular_keys
        
        return '+'.join(all_keys).lower()
    
    def cancel_recording(self):
        """取消录制"""
        self.recording = False
        if self.hook:
            keyboard.unhook(self.hook)
            self.hook = None
        self.current_keys = []
        self.recorded_keys = []

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"四则计算器 v{VERSION}")
        self.root.geometry("500x800")  # 显著增大主窗口
        self.root.resizable(False, False)
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('calculator.ico')
        except:
            pass
        
        # 初始化变量
        self.hidden = False
        self.hide_hotkey = "ctrl+shift+h"
        self.show_hotkey = "ctrl+shift+s"
        self.current_expression = ""
        self.settings_file = "calculator_settings.json"
        
        # 创建快捷键录制器
        self.hotkey_recorder = HotkeyRecorder()
        
        # 绑定键盘事件
        self.bind_keyboard_events()
        
        # 加载保存的设置
        self.load_settings()
        
        # 注册全局热键
        self.register_hotkeys()
        
        # 创建UI
        self.create_ui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 设置窗口样式，使其在任务栏显示
        self.set_taskbar_visibility(True)
        
        # 更新状态
        self.update_status()
    
    def bind_keyboard_events(self):
        """绑定键盘事件"""
        # 绑定数字键和操作符
        self.root.bind('<Key>', self.on_key_press)
        # 绑定回车键（等于）
        self.root.bind('<Return>', lambda e: self.on_button_click('='))
        self.root.bind('<KP_Enter>', lambda e: self.on_button_click('='))
        # 绑定退格键
        self.root.bind('<BackSpace>', lambda e: self.on_button_click('⌫'))
        # 绑定删除键和C键（清除）
        self.root.bind('<Delete>', lambda e: self.on_button_click('C'))
        self.root.bind('c', lambda e: self.on_button_click('C'))
        self.root.bind('C', lambda e: self.on_button_click('C'))
        # 绑定ESC键
        self.root.bind('<Escape>', lambda e: self.on_button_click('C'))
    
    def on_key_press(self, event):
        """处理键盘按键事件"""
        key = event.char
        
        # 处理数字键
        if key.isdigit():
            self.on_button_click(key)
        # 处理小数点
        elif key == '.':
            self.on_button_click('.')
        # 处理运算符
        elif key == '+':
            self.on_button_click('+')
        elif key == '-':
            self.on_button_click('-')
        elif key == '*':
            self.on_button_click('×')
        elif key == '/':
            self.on_button_click('÷')
        elif key == '%':
            self.on_button_click('%')
        # 处理回车键（已单独绑定）
        elif key == '\r':
            self.on_button_click('=')
    
    def create_ui(self):
        """创建用户界面"""
        # 创建主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 顶部工具栏
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 标题
        title_label = ttk.Label(
            toolbar_frame, 
            text=f"四则计算器 v{VERSION}", 
            font=("微软雅黑", 20, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        # 设置按钮 - 使用更大的按钮
        settings_btn = ttk.Button(
            toolbar_frame, 
            text=" ⚙ 设置 ", 
            command=self.open_settings,
            style="Large.TButton"
        )
        settings_btn.pack(side=tk.RIGHT, padx=5)
        
        # 显示区域容器
        display_frame = ttk.Frame(main_container)
        display_frame.pack(fill=tk.X, pady=(0, 25))
        
        # 历史显示
        self.history_var = tk.StringVar(value="")
        history_label = tk.Label(
            display_frame,
            textvariable=self.history_var,
            font=("微软雅黑", 14),
            anchor=tk.E,
            fg="gray",
            bg="white",
            height=1
        )
        history_label.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))
        
        # 主显示区域
        display_container = ttk.Frame(display_frame, relief=tk.SUNKEN, borderwidth=3)
        display_container.pack(fill=tk.X, side=tk.TOP)
        
        self.display_var = tk.StringVar(value="0")
        display_label = tk.Label(
            display_container, 
            textvariable=self.display_var,
            font=("微软雅黑", 36),
            anchor=tk.E,
            padx=25,
            pady=25,
            bg="#f5f5f5",
            relief=tk.FLAT
        )
        display_label.pack(fill=tk.X)
        
        # 按钮框架
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # 按钮布局配置
        button_grid = [
            [('C', 0, 0, 1, 1), ('⌫', 0, 1, 1, 1), ('%', 0, 2, 1, 1), ('÷', 0, 3, 1, 1)],
            [('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1), ('9', 1, 2, 1, 1), ('×', 1, 3, 1, 1)],
            [('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1)],
            [('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1)],
            [('+/-', 4, 0, 1, 1), ('0', 4, 1, 1, 1), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)]
        ]
        
        # 配置网格权重 - 显著增大按钮尺寸
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1, minsize=85)  # 增大行高
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1, minsize=110)  # 增大列宽
        
        # 创建按钮
        for row_group in button_grid:
            for (text, row, col, rowspan, colspan) in row_group:
                # 决定按钮样式
                if text in ['÷', '×', '-', '+', '=']:
                    style_name = "Accent.TButton"
                elif text in ['C', '⌫']:
                    style_name = "Secondary.TButton"
                else:
                    style_name = "Number.TButton"
                
                btn = ttk.Button(
                    buttons_frame,
                    text=text,
                    style=style_name,
                    command=lambda t=text: self.on_button_click(t)
                )
                
                btn.grid(
                    row=row, 
                    column=col, 
                    rowspan=rowspan,
                    columnspan=colspan,
                    padx=5, 
                    pady=5, 
                    sticky="nsew"
                )
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=20,
            pady=10,
            font=("微软雅黑", 11),
            bg="#f0f0f0"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建样式
        self.create_styles()
    
    def create_styles(self):
        """创建按钮样式"""
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('clam')
        
        # 大按钮样式
        style.configure("Large.TButton",
                       font=("微软雅黑", 12),
                       padding=12)
        
        # 数字按钮样式 - 显著增大
        style.configure("Number.TButton", 
                       font=("微软雅黑", 18),
                       padding=20,
                       background="#f0f0f0",
                       borderwidth=2)
        
        # 操作按钮样式
        style.configure("Accent.TButton",
                       font=("微软雅黑", 18, "bold"),
                       background="#ff9500",
                       foreground="white",
                       borderwidth=2)
        
        # 清除按钮样式
        style.configure("Secondary.TButton",
                       font=("微软雅黑", 18),
                       background="#a6a6a6",
                       foreground="black",
                       borderwidth=2)
        
        # 设置按钮样式
        style.configure("Settings.TButton",
                       font=("微软雅黑", 12),
                       padding=12)
        
        # 悬停效果
        style.map("Number.TButton",
                 background=[('active', '#e0e0e0')])
        style.map("Accent.TButton",
                 background=[('active', '#e68600')])
        style.map("Secondary.TButton",
                 background=[('active', '#959595')])
        style.map("Large.TButton",
                 background=[('active', '#e0e0e0')])
        style.map("Settings.TButton",
                 background=[('active', '#e0e0e0')])
    
    def on_button_click(self, button_text):
        """处理按钮点击事件"""
        current_display = self.display_var.get()
        
        if button_text == 'C':
            self.current_expression = ""
            self.display_var.set("0")
            self.history_var.set("")
            
        elif button_text == '⌫':
            if len(current_display) > 1 and current_display != "错误":
                self.display_var.set(current_display[:-1])
                self.current_expression = self.current_expression[:-1]
            else:
                self.display_var.set("0")
                self.current_expression = ""
                
        elif button_text == '=':
            try:
                if not self.current_expression:
                    return
                    
                # 替换符号为Python可识别的运算符
                expression = self.current_expression
                expression = expression.replace('×', '*').replace('÷', '/')
                result = eval(expression)
                
                # 格式化结果
                if isinstance(result, float):
                    if result.is_integer():
                        result = int(result)
                    else:
                        # 限制小数位数
                        result = round(result, 10)
                
                self.history_var.set(f"{self.current_expression} =")
                self.display_var.set(str(result))
                self.current_expression = str(result)
                
            except ZeroDivisionError:
                self.display_var.set("错误：除数不能为零")
                self.current_expression = ""
            except:
                self.display_var.set("错误")
                self.current_expression = ""
                
        elif button_text == '+/-':
            if current_display and current_display != "0" and current_display != "错误":
                if current_display[0] == '-':
                    self.display_var.set(current_display[1:])
                else:
                    self.display_var.set('-' + current_display)
                self.current_expression = self.display_var.get()
                    
        elif button_text == '%':
            try:
                value = float(current_display) / 100
                self.display_var.set(str(value))
                self.current_expression = str(value)
            except:
                self.display_var.set("错误")
                
        elif button_text in ['+', '-', '×', '÷']:
            if self.current_expression and self.current_expression[-1] in '+-×÷':
                self.current_expression = self.current_expression[:-1]
            self.current_expression += button_text
            self.display_var.set(button_text)
            
        else:  # 数字或小数点
            if current_display == "0" or current_display in '+-×÷' or current_display == "错误":
                self.display_var.set(button_text)
            else:
                self.display_var.set(current_display + button_text)
            
            if self.current_expression and self.current_expression[-1] in '+-×÷':
                self.current_expression += button_text
            else:
                if self.current_expression and '=' in self.history_var.get():
                    self.current_expression = button_text
                else:
                    self.current_expression += button_text
        
        # 限制显示长度
        if len(self.display_var.get()) > 12:
            self.display_var.set(self.display_var.get()[:12])
    
    def set_taskbar_visibility(self, visible):
        """设置任务栏可见性"""
        hwnd = user32.GetParent(self.root.winfo_id())
        
        if visible:
            # 显示在任务栏
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style &= ~WS_EX_TOOLWINDOW
            style |= WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        else:
            # 从任务栏隐藏
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= WS_EX_TOOLWINDOW
            style &= ~WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    
    def hide_calculator(self):
        """隐藏计算器"""
        if not self.hidden:
            self.root.withdraw()  # 隐藏窗口
            self.set_taskbar_visibility(False)  # 从任务栏隐藏
            self.hidden = True
            self.update_status()
    
    def show_calculator(self):
        """显示计算器"""
        if self.hidden:
            self.root.deiconify()  # 显示窗口
            self.set_taskbar_visibility(True)  # 在任务栏显示
            self.hidden = False
            self.root.lift()  # 置于顶层
            self.root.focus_force()  # 获取焦点
            self.update_status()
    
    def update_status(self):
        """更新状态栏"""
        if self.hidden:
            status = f"状态：已隐藏 | 按 {self.show_hotkey.upper()} 显示计算器"
        else:
            status = f"状态：正常 | 隐藏：{self.hide_hotkey.upper()} | 显示：{self.show_hotkey.upper()}"
        self.status_var.set(status)
    
    def open_settings(self):
        """打开设置窗口 - 显著增大"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"计算器设置 v{VERSION}")
        settings_window.geometry("850x950")  # 显著增大设置窗口
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 设置窗口图标
        try:
            settings_window.iconbitmap('calculator.ico')
        except:
            pass
        
        # 设置窗口居中
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{x}+{y}")
        
        # 创建Notebook（选项卡）
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # 创建快捷键设置选项卡
        hotkey_frame = ttk.Frame(notebook)
        notebook.add(hotkey_frame, text="快捷键设置")
        self.create_hotkey_settings(hotkey_frame, settings_window)
        
        # 创建关于选项卡
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="关于")
        self.create_about_info(about_frame, settings_window)
        
        # 绑定窗口关闭事件
        settings_window.protocol("WM_DELETE_WINDOW", lambda: self.on_settings_close(settings_window))
    
    def create_hotkey_settings(self, parent, settings_window):
        """创建快捷键设置界面 - 显著增大所有元素"""
        # 主容器
        main_frame = ttk.Frame(parent, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="快捷键设置", 
            font=("微软雅黑", 18, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 25))
        
        # 当前设置显示
        current_frame = ttk.LabelFrame(main_frame, text="当前设置", padding=20)
        current_frame.pack(fill=tk.X, pady=(0, 25))
        
        ttk.Label(current_frame, text="隐藏快捷键:", font=("微软雅黑", 12)).grid(row=0, column=0, sticky=tk.W, pady=10)
        current_hide_label = ttk.Label(current_frame, text=self.hide_hotkey.upper(), 
                                      font=("微软雅黑", 12, "bold"), foreground="blue")
        current_hide_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 0), pady=10)
        
        ttk.Label(current_frame, text="显示快捷键:", font=("微软雅黑", 12)).grid(row=1, column=0, sticky=tk.W, pady=10)
        current_show_label = ttk.Label(current_frame, text=self.show_hotkey.upper(), 
                                      font=("微软雅黑", 12, "bold"), foreground="blue")
        current_show_label.grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=10)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="设置新快捷键", padding=25)
        settings_frame.pack(fill=tk.X, pady=(0, 25))
        
        # 变量
        self.recording_hide = False
        self.recording_show = False
        self.new_hide_hotkey = tk.StringVar(value="")
        self.new_show_hotkey = tk.StringVar(value="")
        
        # 隐藏快捷键设置 - 显著增大
        hide_frame = ttk.Frame(settings_frame)
        hide_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(hide_frame, text="隐藏快捷键:", width=18, font=("微软雅黑", 12)).pack(side=tk.LEFT)
        
        self.hide_entry = ttk.Entry(hide_frame, textvariable=self.new_hide_hotkey, 
                                   width=30, font=("微软雅黑", 12), state='readonly')
        self.hide_entry.pack(side=tk.LEFT, padx=(20, 15), fill=tk.X, expand=True)
        
        self.hide_record_btn = ttk.Button(
            hide_frame, 
            text="设置隐藏快捷键",
            command=lambda: self.start_recording_hotkey("hide", settings_window),
            width=20,
            style="Settings.TButton"
        )
        self.hide_record_btn.pack(side=tk.LEFT)
        
        # 显示快捷键设置 - 显著增大
        show_frame = ttk.Frame(settings_frame)
        show_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(show_frame, text="显示快捷键:", width=18, font=("微软雅黑", 12)).pack(side=tk.LEFT)
        
        self.show_entry = ttk.Entry(show_frame, textvariable=self.new_show_hotkey, 
                                   width=30, font=("微软雅黑", 12), state='readonly')
        self.show_entry.pack(side=tk.LEFT, padx=(20, 15), fill=tk.X, expand=True)
        
        self.show_record_btn = ttk.Button(
            show_frame, 
            text="设置显示快捷键",
            command=lambda: self.start_recording_hotkey("show", settings_window),
            width=20,
            style="Settings.TButton"
        )
        self.show_record_btn.pack(side=tk.LEFT)
        
        # 提示信息
        info_text = """使用方法：
1. 点击"设置隐藏快捷键"或"设置显示快捷键"按钮
2. 按下您想要设置的组合键（如：Ctrl+Shift+H）
3. 系统会捕获您按下的按键组合
4. 确认后点击"保存设置"

支持多按键组合：Ctrl, Alt, Shift + 字母/数字键"""
        
        info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding=20)
        info_frame.pack(fill=tk.X, pady=(0, 25))
        
        info_label = ttk.Label(
            info_frame, 
            text=info_text, 
            justify=tk.LEFT,
            font=("微软雅黑", 11),
            foreground="#666666"
        )
        info_label.pack(anchor=tk.W)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_settings():
            """保存设置"""
            new_hide = self.new_hide_hotkey.get().strip().lower()
            new_show = self.new_show_hotkey.get().strip().lower()
            
            # 如果用户没有设置新的快捷键，使用旧的
            if not new_hide:
                new_hide = self.hide_hotkey
            if not new_show:
                new_show = self.show_hotkey
            
            if new_hide == new_show:
                messagebox.showerror("错误", "隐藏和显示快捷键不能相同！")
                return
            
            try:
                # 卸载旧快捷键
                try:
                    keyboard.remove_hotkey(self.hide_hotkey)
                    keyboard.remove_hotkey(self.show_hotkey)
                except:
                    pass  # 如果快捷键不存在，继续执行
                
                # 更新快捷键
                self.hide_hotkey = new_hide
                self.show_hotkey = new_show
                
                # 注册新快捷键
                self.register_hotkeys()
                
                # 保存到文件
                self.save_settings_to_file()
                
                # 更新状态
                self.update_status()
                
                # 更新显示
                current_hide_label.config(text=self.hide_hotkey.upper())
                current_show_label.config(text=self.show_hotkey.upper())
                
                # 清空输入框
                self.new_hide_hotkey.set("")
                self.new_show_hotkey.set("")
                
                messagebox.showinfo("成功", "快捷键设置已保存并生效！")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存设置失败：{str(e)}")
        
        def test_hide():
            """测试隐藏功能"""
            response = messagebox.askyesno(
                "测试隐藏", 
                "即将隐藏计算器窗口。\n\n隐藏后可以使用设置的显示快捷键重新显示。\n\n是否继续？"
            )
            if response:
                settings_window.destroy()
                self.hide_calculator()
        
        # 按钮容器
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(expand=True, pady=(10, 0))
        
        # 保存按钮
        save_btn = ttk.Button(
            btn_container, 
            text="保存设置", 
            command=save_settings,
            style="Settings.TButton",
            width=18
        )
        save_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 测试按钮
        test_btn = ttk.Button(
            btn_container, 
            text="测试隐藏", 
            command=test_hide,
            style="Settings.TButton",
            width=18
        )
        test_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 取消按钮
        cancel_btn = ttk.Button(
            btn_container, 
            text="关闭", 
            command=lambda: self.on_settings_close(settings_window),
            style="Settings.TButton",
            width=18
        )
        cancel_btn.pack(side=tk.LEFT, padx=10, pady=10)
    
    def start_recording_hotkey(self, hotkey_type, settings_window):
        """开始录制快捷键"""
        # 确保没有正在录制
        if self.hotkey_recorder.recording:
            messagebox.showwarning("警告", "请先完成当前快捷键录制")
            return
        
        # 设置录制状态
        if hotkey_type == "hide":
            self.recording_hide = True
            self.hide_record_btn.config(text="正在录制...", state='disabled')
            self.show_record_btn.config(state='disabled')
        else:
            self.recording_show = True
            self.show_record_btn.config(text="正在录制...", state='disabled')
            self.hide_record_btn.config(state='disabled')
        
        # 创建提示窗口
        self.create_recording_window(hotkey_type, settings_window)
        
        # 开始录制
        def recording_callback(hotkey_str):
            # 在主线程中更新UI
            settings_window.after(0, self.on_recording_complete, hotkey_type, hotkey_str)
        
        self.hotkey_recorder.start_recording(recording_callback)
    
    def create_recording_window(self, hotkey_type, parent_window):
        """创建录制提示窗口 - 显著增大"""
        recording_window = tk.Toplevel(parent_window)
        recording_window.title("录制快捷键")
        recording_window.geometry("500x300")  # 显著增大录制窗口
        recording_window.resizable(False, False)
        recording_window.transient(parent_window)
        recording_window.grab_set()
        
        # 居中显示
        recording_window.update_idletasks()
        x = parent_window.winfo_x() + (parent_window.winfo_width() - recording_window.winfo_width()) // 2
        y = parent_window.winfo_y() + (parent_window.winfo_height() - recording_window.winfo_height()) // 2
        recording_window.geometry(f"+{x}+{y}")
        
        # 内容
        main_frame = ttk.Frame(recording_window, padding=50)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标/提示
        icon_label = ttk.Label(
            main_frame,
            text="⌨️",
            font=("Arial", 64)
        )
        icon_label.pack(pady=(0, 20))
        
        # 提示文字
        action = "隐藏" if hotkey_type == "hide" else "显示"
        prompt_label = ttk.Label(
            main_frame,
            text=f"请按下 {action} 计算器的快捷键",
            font=("微软雅黑", 14, "bold")
        )
        prompt_label.pack()
        
        # 说明文字
        info_label = ttk.Label(
            main_frame,
            text="支持多按键组合（如：Ctrl+Shift+字母）\n按下所有键后抬起即可完成录制",
            font=("微软雅黑", 11),
            justify=tk.CENTER,
            foreground="#666666"
        )
        info_label.pack(pady=15)
        
        # 当前按键显示
        self.recording_display = ttk.Label(
            main_frame,
            text="等待按键...",
            font=("微软雅黑", 16, "bold"),
            foreground="blue"
        )
        self.recording_display.pack()
        
        # 取消按钮
        cancel_btn = ttk.Button(
            main_frame,
            text="取消录制",
            command=lambda: self.cancel_recording(recording_window),
            width=18,
            style="Settings.TButton"
        )
        cancel_btn.pack(pady=(25, 0))
        
        # 保存窗口引用
        self.recording_window = recording_window
        
        # 绑定关闭事件
        recording_window.protocol("WM_DELETE_WINDOW", lambda: self.cancel_recording(recording_window))
        
        # 开始更新显示
        self.update_recording_display()
    
    def update_recording_display(self):
        """更新录制显示"""
        if hasattr(self, 'recording_window') and self.recording_window.winfo_exists():
            if self.hotkey_recorder.recording:
                if self.hotkey_recorder.current_keys:
                    keys = '+'.join(self.hotkey_recorder.current_keys).upper()
                    self.recording_display.config(text=f"已按下: {keys}")
                else:
                    self.recording_display.config(text="等待按键...")
                
                # 继续更新
                self.recording_window.after(100, self.update_recording_display)
    
    def cancel_recording(self, recording_window):
        """取消录制"""
        self.hotkey_recorder.cancel_recording()
        
        # 重置按钮状态
        self.recording_hide = False
        self.recording_show = False
        self.hide_record_btn.config(text="设置隐藏快捷键", state='normal')
        self.show_record_btn.config(text="设置显示快捷键", state='normal')
        
        # 关闭录制窗口
        if recording_window.winfo_exists():
            recording_window.destroy()
    
    def on_recording_complete(self, hotkey_type, hotkey_str):
        """录制完成回调"""
        # 关闭录制窗口
        if hasattr(self, 'recording_window') and self.recording_window.winfo_exists():
            self.recording_window.destroy()
        
        # 重置按钮状态
        self.recording_hide = False
        self.recording_show = False
        self.hide_record_btn.config(text="设置隐藏快捷键", state='normal')
        self.show_record_btn.config(text="设置显示快捷键", state='normal')
        
        if hotkey_str:
            # 更新对应的输入框
            if hotkey_type == "hide":
                self.new_hide_hotkey.set(hotkey_str)
            else:
                self.new_show_hotkey.set(hotkey_str)
            
            messagebox.showinfo("成功", f"已录制快捷键: {hotkey_str.upper()}")
        else:
            messagebox.showwarning("警告", "未检测到有效的按键组合")
    
    def on_settings_close(self, settings_window):
        """设置窗口关闭时的处理"""
        # 停止所有录制
        if self.hotkey_recorder.recording:
            self.hotkey_recorder.cancel_recording()
        
        # 关闭窗口
        settings_window.destroy()
    
    def create_about_info(self, parent, settings_window):
        """创建关于信息界面 - 显著增大"""
        # 主容器
        main_frame = ttk.Frame(parent, padding=40)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 程序图标区域
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(pady=(0, 30))
        
        # 程序标题
        title_label = ttk.Label(
            icon_frame,
            text="四则计算器",
            font=("微软雅黑", 28, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack()
        
        # 版本信息
        version_label = ttk.Label(
            icon_frame,
            text=f"版本 {VERSION}",
            font=("微软雅黑", 16),
            foreground="#7f8c8d"
        )
        version_label.pack(pady=(10, 0))
        
        # 分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=30)
        
        # 功能特点
        features_frame = ttk.LabelFrame(main_frame, text="功能特点", padding=25)
        features_frame.pack(fill=tk.X, pady=(0, 25))
        
        features = [
            "✓ 四则运算：加、减、乘、除",
            "✓ 快捷键隐藏/显示功能",
            "✓ 支持键盘输入和快捷键",
            "✓ 可视化快捷键录制",
            "✓ 设置自动保存",
            "✓ 现代化界面设计"
        ]
        
        for feature in features:
            ttk.Label(
                features_frame,
                text=feature,
                font=("微软雅黑", 12),
                justify=tk.LEFT
            ).pack(anchor=tk.W, pady=6)
        
        # 作者信息
        author_frame = ttk.LabelFrame(main_frame, text="作者信息", padding=25)
        author_frame.pack(fill=tk.X, pady=(0, 25))
        
        author_info = f"""作者：{AUTHOR}
版本：{VERSION}
年份：{YEAR}

一个功能丰富的四则计算器应用，
支持快捷键隐藏/显示功能，
专为高效计算设计。"""
        
        author_label = ttk.Label(
            author_frame,
            text=author_info,
            font=("微软雅黑", 12),
            justify=tk.LEFT
        )
        author_label.pack(anchor=tk.W)
        
        # 版权信息
        copyright_label = ttk.Label(
            main_frame,
            text=f"© {YEAR} 四则计算器 v{VERSION} | 作者：{AUTHOR}",
            font=("微软雅黑", 11),
            foreground="#95a5a6"
        )
        copyright_label.pack(pady=(30, 0))
        
        # 关闭按钮
        close_btn = ttk.Button(
            main_frame,
            text="关闭",
            command=lambda: self.on_settings_close(settings_window),
            width=18,
            style="Settings.TButton"
        )
        close_btn.pack(pady=(30, 0))
    
    def register_hotkeys(self):
        """注册全局快捷键"""
        try:
            # 清除所有现有热键
            try:
                keyboard.unhook_all()
            except:
                pass  # 如果没有热键，继续执行
            
            # 注册隐藏快捷键
            keyboard.add_hotkey(self.hide_hotkey, self.hide_calculator)
            
            # 注册显示快捷键
            keyboard.add_hotkey(self.show_hotkey, self.show_calculator)
            
            print(f"快捷键注册成功：隐藏={self.hide_hotkey}, 显示={self.show_hotkey}")
            
        except Exception as e:
            print(f"注册快捷键时出错: {e}")
    
    def save_settings_to_file(self):
        """保存设置到文件"""
        settings = {
            'hide_hotkey': self.hide_hotkey,
            'show_hotkey': self.show_hotkey,
            'version': VERSION,
            'author': AUTHOR
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            print(f"设置已保存到 {self.settings_file}")
        except Exception as e:
            print(f"保存设置时出错: {e}")
    
    def load_settings(self):
        """从文件加载设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.hide_hotkey = settings.get('hide_hotkey', 'ctrl+shift+h')
                    self.show_hotkey = settings.get('show_hotkey', 'ctrl+shift+s')
                print(f"从 {self.settings_file} 加载设置成功")
            except Exception as e:
                print(f"加载设置时出错: {e}")
        else:
            print("设置文件不存在，使用默认设置")
    
    def on_closing(self):
        """处理窗口关闭事件"""
        # 保存设置
        self.save_settings_to_file()
        
        # 停止所有录制
        if self.hotkey_recorder.recording:
            self.hotkey_recorder.cancel_recording()
        
        # 卸载所有快捷键
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # 关闭窗口
        self.root.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    
    # 设置窗口在屏幕中央
    window_width = 500
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # 尝试设置窗口图标
    try:
        root.iconbitmap('calculator.ico')
    except:
        pass
    
    app = CalculatorApp(root)
    
    root.mainloop()

if __name__ == "__main__":
    # 检查是否是打包后的exe
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe，修改工作目录到exe所在目录
        os.chdir(os.path.dirname(sys.executable))
    
    main()