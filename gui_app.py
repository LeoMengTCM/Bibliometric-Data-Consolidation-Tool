#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiDatabase 文献计量工具 - GUI版本

现代化的图形界面，支持：
- 文件夹选择
- 参数配置
- 实时进度显示
- 日志输出

作者：Meng Linghan
开发工具：Claude Code
日期：2025-11-13
版本：v1.0
"""

import os
import sys
import threading
import logging
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
import queue

# 导入工作流模块
from run_ai_workflow import AIWorkflow


class TextHandler(logging.Handler):
    """自定义日志处理器，将日志输出到GUI"""

    def __init__(self, text_widget, queue):
        super().__init__()
        self.text_widget = text_widget
        self.queue = queue

    def emit(self, record):
        msg = self.format(record)
        self.queue.put(msg)


class MultiDatabaseGUI:
    """MultiDatabase GUI应用主类"""

    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("dark")  # 深色主题
        ctk.set_default_color_theme("blue")  # 蓝色主题

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("MultiDatabase 文献计量工具 v4.3.0")
        self.root.geometry("1000x800")

        # 配置网格权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 创建日志队列
        self.log_queue = queue.Queue()

        # 变量
        self.input_dir = ctk.StringVar(value="")
        self.output_dir = ctk.StringVar(value="")
        self.year_start = ctk.StringVar(value="2015")
        self.year_end = ctk.StringVar(value="2024")
        self.language = ctk.StringVar(value="English")
        self.enable_ai = ctk.BooleanVar(value=True)
        self.enable_cleaning = ctk.BooleanVar(value=True)
        self.enable_plot = ctk.BooleanVar(value=True)
        self.cleaning_level = ctk.StringVar(value="ultimate")

        # 处理状态
        self.processing = False

        # 创建界面
        self.create_widgets()

        # 启动日志更新
        self.update_log()

    def create_widgets(self):
        """创建所有GUI组件"""

        # 主容器（带滚动）
        main_container = ctk.CTkScrollableFrame(self.root)
        main_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # ==================== 标题 ====================
        title_label = ctk.CTkLabel(
            main_container,
            text="📊 MultiDatabase 文献计量工具",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        subtitle_label = ctk.CTkLabel(
            main_container,
            text="AI增强 | WOS标准化 | 一键处理 | 专业输出",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))

        # ==================== 文件夹选择 ====================
        folder_frame = ctk.CTkFrame(main_container)
        folder_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")
        folder_frame.grid_columnconfigure(1, weight=1)

        # 输入文件夹
        ctk.CTkLabel(
            folder_frame,
            text="📁 输入文件夹:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        input_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.input_dir,
            placeholder_text="选择包含 wos.txt 和 scopus.csv 的文件夹",
            width=500
        )
        input_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            folder_frame,
            text="浏览...",
            command=self.browse_input_dir,
            width=100
        ).grid(row=0, column=2, padx=10, pady=10)

        # 输出文件夹
        ctk.CTkLabel(
            folder_frame,
            text="💾 输出文件夹:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")

        output_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.output_dir,
            placeholder_text="选择输出文件夹（留空则输出到输入文件夹）",
            width=500
        )
        output_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(
            folder_frame,
            text="浏览...",
            command=self.browse_output_dir,
            width=100
        ).grid(row=1, column=2, padx=10, pady=10)

        # ==================== 参数配置 ====================
        config_frame = ctk.CTkFrame(main_container)
        config_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        ctk.CTkLabel(
            config_frame,
            text="⚙️ 处理参数",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # 年份范围
        ctk.CTkLabel(config_frame, text="📅 年份范围:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        year_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        year_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkEntry(
            year_frame,
            textvariable=self.year_start,
            width=80,
            placeholder_text="起始年"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(year_frame, text="到").pack(side="left", padx=5)

        ctk.CTkEntry(
            year_frame,
            textvariable=self.year_end,
            width=80,
            placeholder_text="结束年"
        ).pack(side="left", padx=5)

        # 语言选择
        ctk.CTkLabel(config_frame, text="🌐 目标语言:").grid(row=2, column=0, padx=10, pady=5, sticky="w")

        language_menu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.language,
            values=["English", "Chinese", "German", "French", "Spanish", "Japanese"],
            width=150
        )
        language_menu.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # 清洗规则
        ctk.CTkLabel(config_frame, text="🧹 清洗规则:").grid(row=3, column=0, padx=10, pady=5, sticky="w")

        cleaning_menu = ctk.CTkOptionMenu(
            config_frame,
            variable=self.cleaning_level,
            values=["ultimate (终极清洗)", "enhanced (增强清洗)", "basic (基础清洗)"],
            width=200
        )
        cleaning_menu.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # ==================== 功能开关 ====================
        switch_frame = ctk.CTkFrame(main_container)
        switch_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        ctk.CTkLabel(
            switch_frame,
            text="🔧 功能开关",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # AI补全
        ai_switch = ctk.CTkSwitch(
            switch_frame,
            text="✨ AI智能补全机构信息",
            variable=self.enable_ai,
            onvalue=True,
            offvalue=False
        )
        ai_switch.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # 机构清洗
        cleaning_switch = ctk.CTkSwitch(
            switch_frame,
            text="🧹 机构名称清洗",
            variable=self.enable_cleaning,
            onvalue=True,
            offvalue=False
        )
        cleaning_switch.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        # 生成图表
        plot_switch = ctk.CTkSwitch(
            switch_frame,
            text="📊 生成文档类型分析图",
            variable=self.enable_plot,
            onvalue=True,
            offvalue=False
        )
        plot_switch.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        # ==================== 日志输出 ====================
        log_frame = ctk.CTkFrame(main_container)
        log_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            log_frame,
            text="📋 处理日志",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # 日志文本框
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=250,
            width=900,
            font=ctk.CTkFont(family="Monaco", size=11),
            wrap="word"
        )
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # ==================== 控制按钮 ====================
        button_frame = ctk.CTkFrame(main_container)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        # 开始处理按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始处理",
            command=self.start_processing,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.start_button.pack(side="left", padx=10)

        # 清空日志按钮
        ctk.CTkButton(
            button_frame,
            text="🗑️ 清空日志",
            command=self.clear_log,
            width=150,
            height=50,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=10)

        # 退出按钮
        ctk.CTkButton(
            button_frame,
            text="❌ 退出",
            command=self.root.quit,
            width=150,
            height=50,
            font=ctk.CTkFont(size=14),
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=10)

        # ==================== 状态栏 ====================
        self.status_label = ctk.CTkLabel(
            main_container,
            text="就绪",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=7, column=0, columnspan=2, pady=10)

    def browse_input_dir(self):
        """浏览输入文件夹"""
        directory = filedialog.askdirectory(title="选择输入文件夹（包含 wos.txt 和 scopus.csv）")
        if directory:
            self.input_dir.set(directory)
            # 如果输出文件夹为空，默认使用输入文件夹
            if not self.output_dir.get():
                self.output_dir.set(directory)

    def browse_output_dir(self):
        """浏览输出文件夹"""
        directory = filedialog.askdirectory(title="选择输出文件夹")
        if directory:
            self.output_dir.set(directory)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete("1.0", "end")

    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def update_log(self):
        """定期更新日志"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_message(msg)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_log)

    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_dir.get():
            messagebox.showerror("错误", "请选择输入文件夹！")
            return False

        input_path = Path(self.input_dir.get())
        if not input_path.exists():
            messagebox.showerror("错误", f"输入文件夹不存在：{input_path}")
            return False

        # 检查必需文件
        wos_file = input_path / "wos.txt"
        scopus_file = input_path / "scopus.csv"

        if not wos_file.exists():
            messagebox.showerror("错误", f"输入文件夹中未找到 wos.txt 文件！\n路径：{wos_file}")
            return False

        if not scopus_file.exists():
            messagebox.showerror("错误", f"输入文件夹中未找到 scopus.csv 文件！\n路径：{scopus_file}")
            return False

        # 验证年份
        try:
            start_year = int(self.year_start.get())
            end_year = int(self.year_end.get())
            if start_year > end_year:
                messagebox.showerror("错误", "起始年份不能大于结束年份！")
                return False
            if start_year < 1900 or end_year > 2100:
                messagebox.showerror("错误", "年份范围无效！")
                return False
        except ValueError:
            messagebox.showerror("错误", "年份必须是有效的数字！")
            return False

        return True

    def start_processing(self):
        """开始处理"""
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return

        if not self.validate_inputs():
            return

        # 确认对话框
        year_range = f"{self.year_start.get()}-{self.year_end.get()}"
        message = f"""
即将开始处理文献数据：

输入文件夹: {self.input_dir.get()}
输出文件夹: {self.output_dir.get() or '(同输入文件夹)'}
年份范围: {year_range}
目标语言: {self.language.get()}
AI补全: {'启用' if self.enable_ai.get() else '禁用'}
机构清洗: {'启用' if self.enable_cleaning.get() else '禁用'}
生成图表: {'是' if self.enable_plot.get() else '否'}

确认开始处理吗？
        """

        if not messagebox.askyesno("确认", message):
            return

        # 清空日志
        self.clear_log()

        # 禁用开始按钮
        self.processing = True
        self.start_button.configure(state="disabled", text="⏳ 处理中...")
        self.status_label.configure(text="处理中...", text_color="orange")

        # 在新线程中执行处理
        thread = threading.Thread(target=self.run_workflow, daemon=True)
        thread.start()

    def run_workflow(self):
        """在后台线程中运行工作流"""
        try:
            # 配置日志
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

            # 清除现有处理器
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

            # 添加GUI处理器
            gui_handler = TextHandler(self.log_text, self.log_queue)
            gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            logger.addHandler(gui_handler)

            # 确定数据目录
            data_dir = self.output_dir.get() if self.output_dir.get() else self.input_dir.get()

            # 如果输入和输出不同，需要先复制文件
            if self.output_dir.get() and self.output_dir.get() != self.input_dir.get():
                import shutil
                output_path = Path(self.output_dir.get())
                output_path.mkdir(parents=True, exist_ok=True)

                # 复制输入文件
                shutil.copy2(Path(self.input_dir.get()) / "wos.txt", output_path / "wos.txt")
                shutil.copy2(Path(self.input_dir.get()) / "scopus.csv", output_path / "scopus.csv")

                self.log_queue.put(f"✓ 已复制输入文件到输出文件夹")

            # 确定清洗配置文件
            cleaning_level = self.cleaning_level.get().split()[0]  # 提取 ultimate/enhanced/basic
            cleaning_config = f"config/institution_cleaning_rules_{cleaning_level}.json"

            # 创建工作流
            year_range = f"{self.year_start.get()}-{self.year_end.get()}"

            workflow = AIWorkflow(
                data_dir=data_dir,
                language=self.language.get(),
                enable_ai=self.enable_ai.get(),
                enable_cleaning=self.enable_cleaning.get(),
                cleaning_config=cleaning_config,
                year_range=year_range
            )

            # 运行工作流
            success = workflow.run()

            if success:
                # 如果需要生成图表
                if self.enable_plot.get():
                    try:
                        from plot_document_types import generate_document_type_analysis
                        final_file = Path(data_dir) / "Final_Version_Year_Filtered.txt"
                        if final_file.exists():
                            generate_document_type_analysis(str(final_file))
                            self.log_queue.put("✓ 文档类型分析图已生成")
                    except Exception as e:
                        self.log_queue.put(f"⚠ 生成图表失败: {str(e)}")

                self.log_queue.put("\n" + "=" * 80)
                self.log_queue.put("🎉 处理完成！")
                self.log_queue.put("=" * 80)
                self.log_queue.put(f"\n输出文件位置: {data_dir}")
                self.log_queue.put("\n推荐使用文件:")
                self.log_queue.put("  ⭐ Final_Version_Year_Filtered.txt - 导入VOSviewer/CiteSpace")
                self.log_queue.put("  ⭐ Final_Version_Year_Filtered_analysis_report.txt - 论文写作参考")

                self.root.after(0, lambda: self.status_label.configure(
                    text="✓ 处理完成！",
                    text_color="green"
                ))

                self.root.after(0, lambda: messagebox.showinfo(
                    "成功",
                    f"处理完成！\n\n输出文件位置:\n{data_dir}\n\n推荐使用:\nFinal_Version_Year_Filtered.txt"
                ))
            else:
                self.log_queue.put("\n❌ 处理失败，请查看日志")
                self.root.after(0, lambda: self.status_label.configure(
                    text="✗ 处理失败",
                    text_color="red"
                ))
                self.root.after(0, lambda: messagebox.showerror("错误", "处理失败，请查看日志"))

        except Exception as e:
            import traceback
            error_msg = f"错误: {str(e)}\n\n{traceback.format_exc()}"
            self.log_queue.put(f"\n❌ 发生错误:\n{error_msg}")
            self.root.after(0, lambda: self.status_label.configure(
                text="✗ 发生错误",
                text_color="red"
            ))
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))

        finally:
            # 恢复开始按钮
            self.processing = False
            self.root.after(0, lambda: self.start_button.configure(
                state="normal",
                text="🚀 开始处理"
            ))

    def run(self):
        """运行GUI应用"""
        self.root.mainloop()


def main():
    """主函数"""
    # 检查依赖
    try:
        import customtkinter
    except ImportError:
        print("错误: 缺少 customtkinter 库")
        print("\n请先安装:")
        print("  pip3 install customtkinter")
        print("\n或者:")
        print("  pip3 install --break-system-packages customtkinter")
        sys.exit(1)

    # 创建并运行应用
    app = MultiDatabaseGUI()
    app.run()


if __name__ == "__main__":
    main()
