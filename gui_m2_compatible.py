#!/usr/bin/env python3
"""
M2 macOS 兼容版本的 GUI
专门针对 tkinter 8.5 在 M2 芯片上的问题进行优化
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
from pathlib import Path
import queue
import time
import subprocess
import platform

# Import the core functionality
from augment_tools_core.common_utils import (
    get_os_specific_vscode_paths,
    print_info,
    print_success,
    print_error,
    print_warning,
    IDEType,
    get_ide_paths,
    get_ide_display_name,
    get_ide_process_names
)
from augment_tools_core.database_manager import clean_ide_database
from augment_tools_core.telemetry_manager import modify_ide_telemetry_ids


class SimpleButton(tk.Frame):
    """简化的按钮组件，专门为 M2 macOS tkinter 8.5 优化"""
    def __init__(self, parent, text, command, style="primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.text = text
        self.style = style
        
        # 使用更简单的颜色方案，确保在 tkinter 8.5 上正确显示
        if style == "primary":
            bg_color = '#0066CC'  # 深蓝色
            fg_color = '#FFFFFF'
        elif style == "secondary":
            bg_color = '#00AA00'  # 绿色
            fg_color = '#FFFFFF'
        elif style == "warning":
            bg_color = '#FF6600'  # 橙色
            fg_color = '#FFFFFF'
        else:
            bg_color = '#CCCCCC'  # 灰色
            fg_color = '#000000'
        
        # 创建简单的按钮，避免复杂的 Canvas 操作
        self.button = tk.Button(self,
                               text=text,
                               command=command,
                               font=('Helvetica', 12, 'bold'),  # 使用标准字体
                               bg=bg_color,
                               fg=fg_color,
                               relief='raised',
                               bd=2,
                               padx=20,
                               pady=10,
                               cursor='hand2')
        self.button.pack(fill='both', expand=True)
        
        # 添加悬停效果
        def on_enter(e):
            if style == "primary":
                self.button.config(bg='#0055BB')
            elif style == "secondary":
                self.button.config(bg='#009900')
            elif style == "warning":
                self.button.config(bg='#EE5500')
            else:
                self.button.config(bg='#BBBBBB')
        
        def on_leave(e):
            self.button.config(bg=bg_color)
        
        self.button.bind('<Enter>', on_enter)
        self.button.bind('<Leave>', on_leave)
    
    def config_state(self, state):
        """配置按钮状态"""
        self.button.config(state=state)


class AugmentToolsGUI_M2:
    """M2 macOS 兼容版本的 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AugmentCode-Free (M2 macOS 兼容版)")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        # 使用简单的背景色，确保兼容性
        self.root.configure(bg='#F0F0F0')
        
        # 居中窗口
        self.center_window()
        
        # 消息队列
        self.message_queue = queue.Queue()
        
        # 设置 GUI
        self.setup_gui()
        
        # 启动消息处理
        self.process_messages()
        
        # 重定向打印函数
        self.setup_print_redirection()
    
    def center_window(self):
        """居中窗口"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_gui(self):
        """设置 GUI 组件"""
        # 主框架
        main_frame = tk.Frame(self.root, bg='#F0F0F0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame,
                              text="AugmentCode-Free",
                              font=('Helvetica', 20, 'bold'),
                              fg='#000000', bg='#F0F0F0')
        title_label.pack(pady=(0, 10))
        
        # 副标题
        subtitle_label = tk.Label(main_frame,
                                 text="M2 macOS 兼容版本",
                                 font=('Helvetica', 12),
                                 fg='#666666', bg='#F0F0F0')
        subtitle_label.pack(pady=(0, 20))
        
        # IDE 选择
        ide_frame = tk.LabelFrame(main_frame, text="选择 IDE",
                                 font=('Helvetica', 11, 'bold'),
                                 bg='#F0F0F0', fg='#000000')
        ide_frame.pack(fill='x', pady=(0, 20))
        
        self.ide_var = tk.StringVar(value="VS Code")
        ide_options = ["VS Code", "Cursor", "Windsurf"]
        
        for i, option in enumerate(ide_options):
            rb = tk.Radiobutton(ide_frame, text=option,
                               variable=self.ide_var, value=option,
                               font=('Helvetica', 10),
                               bg='#F0F0F0', fg='#000000')
            rb.pack(anchor='w', padx=10, pady=2)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg='#F0F0F0')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # 创建按钮
        self.run_all_btn = SimpleButton(button_frame, "一键修改所有配置",
                                       self.run_all_clicked, style="primary")
        self.run_all_btn.pack(fill='x', pady=(0, 10))
        
        self.close_ide_btn = SimpleButton(button_frame, "关闭选中的IDE",
                                         self.close_ide_clicked, style="warning")
        self.close_ide_btn.pack(fill='x', pady=(0, 10))
        
        self.clean_db_btn = SimpleButton(button_frame, "清理IDE数据库",
                                        self.clean_database_clicked, style="secondary")
        self.clean_db_btn.pack(fill='x', pady=(0, 10))
        
        self.modify_ids_btn = SimpleButton(button_frame, "修改IDE遥测ID",
                                          self.modify_ids_clicked, style="secondary")
        self.modify_ids_btn.pack(fill='x', pady=(0, 10))
        
        # 状态显示
        status_frame = tk.Frame(main_frame, bg='#F0F0F0')
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = tk.Label(status_frame,
                                    textvariable=self.status_var,
                                    font=('Helvetica', 10),
                                    fg='#006600', bg='#F0F0F0')
        self.status_label.pack()
        
        # 版本信息
        version_label = tk.Label(main_frame,
                                text="v0.0.3 - M2 macOS 兼容版",
                                font=('Helvetica', 9),
                                fg='#999999', bg='#F0F0F0')
        version_label.pack(side='bottom', pady=(20, 0))
        
        # 设置默认关键字
        self.keyword_var = tk.StringVar(value="augment")
    
    def get_selected_ide_type(self) -> IDEType:
        """获取选中的 IDE 类型"""
        ide_name = self.ide_var.get()
        if ide_name == "VS Code":
            return IDEType.VSCODE
        elif ide_name == "Cursor":
            return IDEType.CURSOR
        elif ide_name == "Windsurf":
            return IDEType.WINDSURF
        else:
            return IDEType.VSCODE
    
    def setup_print_redirection(self):
        """设置打印重定向"""
        # 存储原始函数
        self.original_print_info = print_info
        self.original_print_success = print_success
        self.original_print_error = print_error
        self.original_print_warning = print_warning
        
        # 替换为 GUI 版本
        import augment_tools_core.common_utils as utils
        utils.print_info = self.gui_print_info
        utils.print_success = self.gui_print_success
        utils.print_error = self.gui_print_error
        utils.print_warning = self.gui_print_warning
    
    def gui_print_info(self, message):
        """GUI 版本的 print_info"""
        self.message_queue.put(('info', message))
    
    def gui_print_success(self, message):
        """GUI 版本的 print_success"""
        self.message_queue.put(('success', message))
    
    def gui_print_error(self, message):
        """GUI 版本的 print_error"""
        self.message_queue.put(('error', message))
    
    def gui_print_warning(self, message):
        """GUI 版本的 print_warning"""
        self.message_queue.put(('warning', message))
    
    def process_messages(self):
        """处理消息队列"""
        try:
            while True:
                msg_type, message = self.message_queue.get_nowait()

                # 更新状态显示（但不覆盖手动设置的状态）
                timestamp = time.strftime("%H:%M:%S")

                # 只在没有手动设置状态时更新
                current_status = self.status_var.get()
                if not any(x in current_status for x in ["正在", "✅", "❌", "ℹ️"]):
                    if msg_type == 'success':
                        self.status_var.set("✅ 操作成功")
                        self.status_label.config(fg='#006600')
                    elif msg_type == 'error':
                        self.status_var.set("❌ 操作失败")
                        self.status_label.config(fg='#CC0000')
                    elif msg_type == 'warning':
                        self.status_var.set("⚠️ 注意")
                        self.status_label.config(fg='#FF6600')
                    else:
                        self.status_var.set("ℹ️ 处理中...")
                        self.status_label.config(fg='#0066CC')

                # 打印到控制台，包含时间戳
                print(f"[{timestamp}] [{msg_type.upper()}] {message}")

        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_messages)
    
    def set_buttons_state(self, state):
        """设置按钮状态"""
        self.run_all_btn.config_state(state)
        self.close_ide_btn.config_state(state)
        self.clean_db_btn.config_state(state)
        self.modify_ids_btn.config_state(state)

        # 如果按钮重新启用，重置状态为就绪
        if state == 'normal':
            self.root.after(2000, lambda: self.status_var.set("就绪") if "已完成" in self.status_var.get() or "失败" in self.status_var.get() else None)
    
    def show_message(self, title, message, msg_type="info"):
        """显示消息对话框"""
        if msg_type == "warning":
            return messagebox.askyesno(title, message)
        else:
            messagebox.showinfo(title, message)
            return True

    def _is_ide_running(self, ide_type: IDEType) -> bool:
        """检查指定的 IDE 是否正在运行"""
        system = platform.system().lower()
        process_names = get_ide_process_names(ide_type)

        try:
            if system == "windows":
                for process_name in process_names:
                    result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'],
                                          capture_output=True, text=True)
                    if process_name in result.stdout:
                        return True
                return False
            else:  # macOS and Linux
                for process_name in process_names:
                    # Remove .exe extension for Unix systems
                    unix_process_name = process_name.replace('.exe', '').lower()
                    result = subprocess.run(['pgrep', '-f', unix_process_name],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return True
                return False
        except Exception as e:
            self.gui_print_warning(f"检查进程时发生错误: {e}")
            return False

    def _close_ide_processes(self, ide_type: IDEType) -> bool:
        """关闭指定 IDE 的所有进程"""
        system = platform.system().lower()
        process_names = get_ide_process_names(ide_type)
        ide_name = get_ide_display_name(ide_type)

        success = False
        try:
            if system == "windows":
                for process_name in process_names:
                    result = subprocess.run(['taskkill', '/F', '/IM', process_name],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.gui_print_success(f"成功关闭 {process_name}")
                        success = True
                    elif "找不到进程" not in result.stderr and "not found" not in result.stderr.lower():
                        self.gui_print_warning(f"关闭 {process_name} 时出现问题: {result.stderr}")
            else:  # macOS and Linux
                for process_name in process_names:
                    # Remove .exe extension for Unix systems
                    unix_process_name = process_name.replace('.exe', '').lower()
                    result = subprocess.run(['pkill', '-f', unix_process_name],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.gui_print_success(f"成功关闭 {unix_process_name}")
                        success = True
                    elif result.returncode != 1:  # 1 means no process found, which is OK
                        self.gui_print_warning(f"关闭 {unix_process_name} 时出现问题")

            return success
        except Exception as e:
            self.gui_print_error(f"关闭 {ide_name} 进程时发生错误: {e}")
            return False


    # 实现真实的按钮点击功能
    def run_all_clicked(self):
        """一键修改按钮点击 - 真实功能实现"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 显示警告对话框
        result = self.show_message(
            "一键修改确认",
            f"此按钮会关闭{ide_name}并清除Augment聊天数据！\n\n"
            f"请确保：\n"
            f"• 文件已保存\n"
            f"• {ide_name}中的重要聊天记录已备份\n\n"
            f"是否继续执行一键修改？",
            "warning"
        )

        if not result:
            return

        keyword = self.keyword_var.get().strip()  # Use default "augment"

        self.set_buttons_state('disabled')
        self.status_var.set("正在执行一键修改...")

        def run_all_task():
            try:
                self.gui_print_info(f"开始执行{ide_name}一键修改操作")

                # Step 0: Close IDE first
                self.gui_print_info(f"--- 步骤 0: 关闭{ide_name} ---")
                if self._is_ide_running(ide_type):
                    if self._close_ide_processes(ide_type):
                        self.gui_print_success(f"{ide_name}已关闭")
                    else:
                        self.gui_print_warning(f"关闭{ide_name}时出现问题，继续执行后续步骤")
                else:
                    self.gui_print_info(f"{ide_name}未运行，跳过关闭步骤")

                # Step 1: Clean database
                self.gui_print_info("--- 步骤 1: 数据库清理 ---")
                try:
                    clean_ide_database(ide_type, keyword)
                except Exception as e:
                    self.gui_print_error(f"数据库清理步骤中发生错误: {e}")
                    self.gui_print_warning("尽管出现错误，仍继续下一步。")

                # Step 2: Modify telemetry IDs
                self.gui_print_info("--- 步骤 2: 遥测 ID 修改 ---")
                try:
                    modify_ide_telemetry_ids(ide_type)
                except Exception as e:
                    self.gui_print_error(f"遥测 ID 修改步骤中发生错误: {e}")

                self.gui_print_success(f"{ide_name}所有工具已完成执行序列。")
                self.root.after(0, lambda: self.status_var.set("✅ 所有工具执行已完成"))

            except Exception as e:
                self.gui_print_error(f"运行所有工具时发生错误: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("❌ 工具执行失败"))
            finally:
                self.root.after(0, lambda: self.set_buttons_state('normal'))

        threading.Thread(target=run_all_task, daemon=True).start()

    def close_ide_clicked(self):
        """关闭 IDE 按钮点击 - 真实功能实现"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # 显示警告对话框
        result = self.show_message(
            f"关闭{ide_name}确认",
            f"• 若有未保存的内容请先进行保存\n"
            f"• {ide_name}中需要备份的聊天记录请先备份\n\n"
            f"确认无误后才能关闭{ide_name}。\n\n"
            f"是否继续关闭{ide_name}？",
            "warning"
        )

        if not result:
            return

        self.set_buttons_state('disabled')
        self.status_var.set(f"正在关闭{ide_name}...")

        def close_task():
            try:
                self.gui_print_info(f"开始关闭{ide_name}进程")

                # Close IDE processes
                if self._close_ide_processes(ide_type):
                    self.gui_print_success(f"{ide_name}已成功关闭")
                    self.root.after(0, lambda: self.status_var.set(f"✅ {ide_name}已关闭"))
                else:
                    self.gui_print_warning(f"未找到运行中的{ide_name}进程")
                    self.root.after(0, lambda: self.status_var.set(f"ℹ️ {ide_name}未运行"))

            except Exception as e:
                self.gui_print_error(f"关闭{ide_name}时发生错误: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("❌ 关闭失败"))
            finally:
                self.root.after(0, lambda: self.set_buttons_state('normal'))

        threading.Thread(target=close_task, daemon=True).start()

    def clean_database_clicked(self):
        """清理数据库按钮点击 - 真实功能实现"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # Check if IDE is running
        if self._is_ide_running(ide_type):
            self.show_message(
                f"{ide_name}正在运行",
                f"检测到{ide_name}正在运行！\n\n"
                f"请先关闭{ide_name}再进行数据库清理操作。\n"
                f"您可以点击\"关闭选中的IDE\"按钮。"
            )
            return

        keyword = self.keyword_var.get().strip()
        self.set_buttons_state('disabled')
        self.status_var.set(f"正在清理{ide_name}数据库...")

        def clean_task():
            try:
                self.gui_print_info(f"开始清理 {ide_name} 数据库 (关键字: '{keyword}')")

                if clean_ide_database(ide_type, keyword):
                    self.gui_print_info("数据库清理过程完成。")
                    self.root.after(0, lambda: self.status_var.set("✅ 数据库清理已完成"))
                else:
                    self.gui_print_error("数据库清理过程报告错误。请检查之前的消息。")
                    self.root.after(0, lambda: self.status_var.set("❌ 数据库清理失败"))

            except Exception as e:
                self.gui_print_error(f"清理数据库时发生错误: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("❌ 数据库清理失败"))
            finally:
                self.root.after(0, lambda: self.set_buttons_state('normal'))

        threading.Thread(target=clean_task, daemon=True).start()

    def modify_ids_clicked(self):
        """修改 ID 按钮点击 - 真实功能实现"""
        ide_type = self.get_selected_ide_type()
        ide_name = get_ide_display_name(ide_type)

        # Check if IDE is running
        if self._is_ide_running(ide_type):
            self.show_message(
                f"{ide_name}正在运行",
                f"检测到{ide_name}正在运行！\n\n"
                f"请先关闭{ide_name}再进行遥测ID修改操作。\n"
                f"您可以点击\"关闭选中的IDE\"按钮。"
            )
            return

        self.set_buttons_state('disabled')
        self.status_var.set(f"正在修改{ide_name}遥测 ID...")

        def modify_task():
            try:
                self.gui_print_info(f"开始修改 {ide_name} 遥测 ID")

                if modify_ide_telemetry_ids(ide_type):
                    self.gui_print_info("遥测 ID 修改过程完成。")
                    self.root.after(0, lambda: self.status_var.set("✅ 遥测 ID 修改已完成"))
                else:
                    self.gui_print_error("遥测 ID 修改过程报告错误。请检查之前的消息。")
                    self.root.after(0, lambda: self.status_var.set("❌ 遥测 ID 修改失败"))

            except Exception as e:
                self.gui_print_error(f"修改遥测 ID 时发生错误: {str(e)}")
                self.root.after(0, lambda: self.status_var.set("❌ 遥测 ID 修改失败"))
            finally:
                self.root.after(0, lambda: self.set_buttons_state('normal'))

        threading.Thread(target=modify_task, daemon=True).start()


def main():
    """主函数"""
    print("🚀 启动 M2 macOS 兼容版 GUI...")

    root = tk.Tk()
    app = AugmentToolsGUI_M2(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("应用程序被用户中断")
        sys.exit(0)


if __name__ == "__main__":
    main()
