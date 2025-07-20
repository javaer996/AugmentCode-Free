#!/usr/bin/env python3
"""
M2 macOS 启动脚本
自动检测并选择最适合的 GUI 版本
"""

import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_system():
    """检查系统环境"""
    system_info = {
        'system': platform.system(),
        'release': platform.release(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }
    
    # 检查是否为 Apple Silicon
    try:
        result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                              capture_output=True, text=True)
        system_info['cpu'] = result.stdout.strip()
        system_info['is_apple_silicon'] = "Apple" in result.stdout
    except:
        system_info['cpu'] = "Unknown"
        system_info['is_apple_silicon'] = False
    
    return system_info

def check_tkinter():
    """检查 tkinter 版本"""
    try:
        import tkinter as tk
        return {
            'available': True,
            'tk_version': tk.TkVersion,
            'tcl_version': tk.TclVersion,
            'has_issues': tk.TkVersion < 8.6
        }
    except ImportError:
        return {
            'available': False,
            'tk_version': None,
            'tcl_version': None,
            'has_issues': True
        }

def show_version_selector():
    """显示版本选择器"""
    root = tk.Tk()
    root.title("AugmentCode-Free 启动器")
    root.geometry("500x400")
    root.configure(bg='#F0F0F0')
    root.resizable(False, False)
    
    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # 获取系统信息
    system_info = check_system()
    tkinter_info = check_tkinter()
    
    # 主框架
    main_frame = tk.Frame(root, bg='#F0F0F0')
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # 标题
    title_label = tk.Label(main_frame,
                          text="AugmentCode-Free 启动器",
                          font=('Helvetica', 18, 'bold'),
                          fg='#000000', bg='#F0F0F0')
    title_label.pack(pady=(0, 20))
    
    # 系统信息
    info_text = f"系统: {system_info['system']} {system_info['release']}\n"
    info_text += f"处理器: {system_info['cpu']}\n"
    info_text += f"Python: {system_info['python_version']}\n"
    
    if tkinter_info['available']:
        info_text += f"tkinter: {tkinter_info['tk_version']}"
        if tkinter_info['has_issues']:
            info_text += " (存在兼容性问题)"
    else:
        info_text += "tkinter: 未安装"
    
    info_label = tk.Label(main_frame,
                         text=info_text,
                         font=('Helvetica', 10),
                         fg='#333333', bg='#F0F0F0',
                         justify='left')
    info_label.pack(pady=(0, 20))
    
    # 推荐信息
    if system_info['is_apple_silicon'] and tkinter_info['has_issues']:
        recommendation = "🔧 检测到 Apple Silicon + tkinter 8.5\n推荐使用兼容版本以获得最佳体验"
        color = '#FF6600'
    elif system_info['is_apple_silicon']:
        recommendation = "✅ Apple Silicon 系统，两个版本都可以使用"
        color = '#006600'
    else:
        recommendation = "ℹ️ 建议使用标准版本"
        color = '#0066CC'
    
    rec_label = tk.Label(main_frame,
                        text=recommendation,
                        font=('Helvetica', 11, 'bold'),
                        fg=color, bg='#F0F0F0')
    rec_label.pack(pady=(0, 30))
    
    # 选择变量
    choice = tk.StringVar(value="auto")
    
    # 版本选择
    version_frame = tk.LabelFrame(main_frame, text="选择版本",
                                 font=('Helvetica', 12, 'bold'),
                                 bg='#F0F0F0', fg='#000000')
    version_frame.pack(fill='x', pady=(0, 20))
    
    # 自动选择
    auto_rb = tk.Radiobutton(version_frame,
                            text="自动选择 (推荐)",
                            variable=choice, value="auto",
                            font=('Helvetica', 11),
                            bg='#F0F0F0', fg='#000000')
    auto_rb.pack(anchor='w', padx=10, pady=5)
    
    # 标准版本
    standard_rb = tk.Radiobutton(version_frame,
                                text="标准版本 (原始 GUI)",
                                variable=choice, value="standard",
                                font=('Helvetica', 11),
                                bg='#F0F0F0', fg='#000000')
    standard_rb.pack(anchor='w', padx=10, pady=5)
    
    # 兼容版本
    compatible_rb = tk.Radiobutton(version_frame,
                                  text="兼容版本 (M2 macOS 优化)",
                                  variable=choice, value="compatible",
                                  font=('Helvetica', 11),
                                  bg='#F0F0F0', fg='#000000')
    compatible_rb.pack(anchor='w', padx=10, pady=5)
    
    # 按钮框架
    button_frame = tk.Frame(main_frame, bg='#F0F0F0')
    button_frame.pack(fill='x', pady=(20, 0))
    
    result = {'choice': None}
    
    def start_app():
        selected = choice.get()
        
        if selected == "auto":
            # 自动选择逻辑
            if system_info['is_apple_silicon'] and tkinter_info['has_issues']:
                selected = "compatible"
            else:
                selected = "standard"
        
        result['choice'] = selected
        root.destroy()
    
    def exit_app():
        result['choice'] = None
        root.destroy()
    
    # 启动按钮
    start_btn = tk.Button(button_frame,
                         text="启动应用",
                         command=start_app,
                         font=('Helvetica', 12, 'bold'),
                         bg='#0066CC', fg='#FFFFFF',
                         relief='raised', bd=2,
                         padx=30, pady=10,
                         cursor='hand2')
    start_btn.pack(side='left', padx=(0, 10))
    
    # 退出按钮
    exit_btn = tk.Button(button_frame,
                        text="退出",
                        command=exit_app,
                        font=('Helvetica', 12),
                        bg='#CCCCCC', fg='#000000',
                        relief='raised', bd=2,
                        padx=30, pady=10,
                        cursor='hand2')
    exit_btn.pack(side='right')
    
    root.mainloop()
    return result['choice']

def launch_version(version):
    """启动指定版本"""
    # 设置环境变量
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    
    if version == "compatible":
        print("🚀 启动 M2 macOS 兼容版本...")
        subprocess.run([sys.executable, 'gui_m2_compatible.py'])
    else:
        print("🚀 启动标准版本...")
        subprocess.run([sys.executable, 'main.py'])

def main():
    """主函数"""
    print("=" * 50)
    print("🚀 AugmentCode-Free M2 macOS 启动器")
    print("=" * 50)
    
    # 检查系统
    system_info = check_system()
    tkinter_info = check_tkinter()
    
    print(f"系统: {system_info['system']} {system_info['release']}")
    print(f"处理器: {system_info['cpu']}")
    print(f"Python: {system_info['python_version']}")
    
    if tkinter_info['available']:
        print(f"tkinter: {tkinter_info['tk_version']}")
        if tkinter_info['has_issues']:
            print("⚠️  检测到 tkinter 兼容性问题")
    else:
        print("❌ tkinter 未安装")
        return
    
    # 显示版本选择器
    try:
        choice = show_version_selector()
        if choice:
            launch_version(choice)
        else:
            print("用户取消启动")
    except Exception as e:
        print(f"启动器出错: {e}")
        print("尝试直接启动兼容版本...")
        launch_version("compatible")

if __name__ == "__main__":
    main()
