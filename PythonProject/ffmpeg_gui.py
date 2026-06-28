"""
FFmpeg 视频处理工具 - 美观增强版
具有现代化界面和完善功能的视频处理工具
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import time
from datetime import datetime


class ModernFFmpegGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("FFmpeg 专业视频处理工具")
        self.window.geometry("800x750")
        self.window.configure(bg='#1a1a2e')  # 深色主题背景

        # 设置窗口图标（可选，如果有图标文件的话）
        # self.window.iconbitmap("icon.ico")

        # 设置窗口最小尺寸
        self.window.minsize(700, 650)

        # 存储路径的变量
        self.input_video = ""
        self.output_folder = ""
        self.current_process = None

        # 颜色主题
        self.colors = {
            'bg': '#1a1a2e',  # 深蓝色背景
            'fg': '#eeeeee',  # 浅色文字
            'accent': '#0f3460',  # 深蓝色强调
            'success': '#4CAF50',  # 绿色成功
            'warning': '#FF9800',  # 橙色警告
            'danger': '#f44336',  # 红色危险
            'info': '#2196F3',  # 蓝色信息
            'frame_bg': '#16213e',  # 框架背景
            'button_bg': '#e94560',  # 按钮背景色
            'button_hover': '#c73b54'  # 按钮悬停色
        }

        # 创建界面
        self.setup_styles()
        self.create_widgets()

        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """设置界面样式"""
        # 配置 ttk 样式
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义进度条样式
        style.configure("Modern.Horizontal.TProgressbar",
                        background=self.colors['success'],
                        troughcolor=self.colors['frame_bg'],
                        bordercolor=self.colors['frame_bg'],
                        lightcolor=self.colors['success'],
                        darkcolor=self.colors['success'])

        # 自定义按钮样式（针对 ttk 按钮）
        style.configure("Modern.TButton",
                        background=self.colors['button_bg'],
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        font=('微软雅黑', 10))
        style.map("Modern.TButton",
                  background=[('active', self.colors['button_hover'])])

    def create_widgets(self):
        """创建所有界面元素"""

        # ========== 顶部标题区域 ==========
        header_frame = tk.Frame(self.window, bg=self.colors['accent'], height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # 标题
        title_label = tk.Label(
            header_frame,
            text="🎬 FFmpeg 专业视频处理工具",
            font=("微软雅黑", 20, "bold"),
            bg=self.colors['accent'],
            fg='white'
        )
        title_label.pack(pady=20)

        # 副标题
        subtitle_label = tk.Label(
            header_frame,
            text="视频逐帧提取 · 压缩 · 格式转换 · 更多功能",
            font=("微软雅黑", 9),
            bg=self.colors['accent'],
            fg='#cccccc'
        )
        subtitle_label.pack()

        # ========== 主要内容区域（使用 Notebook 标签页） ==========
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # 创建各个功能页面
        self.create_extract_tab()  # 逐帧提取页面
        self.create_compress_tab()  # 视频压缩页面
        self.create_convert_tab()  # 格式转换页面
        self.create_info_tab()  # 视频信息页面

        # ========== 底部进度区域 ==========
        bottom_frame = tk.Frame(self.window, bg=self.colors['bg'], height=100)
        bottom_frame.pack(fill="x", padx=20, pady=10)

        # 进度条
        self.progress_bar = ttk.Progressbar(
            bottom_frame,
            style="Modern.Horizontal.TProgressbar",
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=5, fill="x")

        # 状态信息
        self.status_frame = tk.Frame(bottom_frame, bg=self.colors['bg'])
        self.status_frame.pack(fill="x", pady=5)

        self.status_icon = tk.Label(self.status_frame, text="●",
                                    bg=self.colors['bg'], fg=self.colors['info'])
        self.status_icon.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(
            self.status_frame,
            text="就绪",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 9)
        )
        self.status_label.pack(side=tk.LEFT)

        # 按钮区域
        button_frame = tk.Frame(bottom_frame, bg=self.colors['bg'])
        button_frame.pack(pady=10)

        self.start_button = self.create_modern_button(
            button_frame,
            text="▶ 开始处理",
            command=self.start_processing,
            bg_color=self.colors['success'],
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = self.create_modern_button(
            button_frame,
            text="⏹ 停止",
            command=self.stop_processing,
            bg_color=self.colors['danger'],
            width=10,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = self.create_modern_button(
            button_frame,
            text="🗑 清空",
            command=self.clear_all,
            bg_color=self.colors['warning'],
            width=10
        )
        self.clear_button.pack(side=tk.LEFT, padx=10)

    def create_modern_button(self, parent, text, command, bg_color, width=None, state="normal"):
        """创建现代化按钮"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=("微软雅黑", 10, "bold"),
            relief="flat",
            cursor="hand2",
            width=width,
            state=state
        )

        # 添加悬停效果
        def on_enter(e):
            if btn['state'] == 'normal':
                btn['bg'] = self.lighten_color(bg_color)

        def on_leave(e):
            if btn['state'] == 'normal':
                btn['bg'] = bg_color

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def lighten_color(self, color):
        """提亮颜色"""
        # 简单的颜色提亮，实际使用中可以更精细
        light_colors = {
            self.colors['success']: '#6abf69',
            self.colors['danger']: '#ff6b5e',
            self.colors['warning']: '#ffb347',
            self.colors['info']: '#4a9eff'
        }
        return light_colors.get(color, color)

    def create_extract_tab(self):
        """创建逐帧提取页面"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🎞 逐帧提取")

        # 主要内容框架
        main_frame = tk.Frame(tab, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 文件选择区域
        self.create_file_section(main_frame, "输入视频文件", "extract")
        self.create_output_section(main_frame, "输出图片文件夹", "extract")

        # 设置区域
        settings_frame = tk.LabelFrame(
            main_frame,
            text="⚙ 提取设置",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 11, "bold"),
            padx=15,
            pady=15
        )
        settings_frame.pack(fill="x", pady=10)

        # 提取间隔
        interval_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        interval_frame.pack(fill="x", pady=5)

        tk.Label(
            interval_frame,
            text="📊 提取间隔：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.extract_interval = tk.IntVar(value=1)
        interval_scale = tk.Scale(
            interval_frame,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.extract_interval,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            highlightthickness=0,
            troughcolor=self.colors['accent']
        )
        interval_scale.pack(side=tk.LEFT, padx=10)

        self.interval_label = tk.Label(
            interval_frame,
            text="每 1 帧提取一张",
            bg=self.colors['frame_bg'],
            fg=self.colors['info'],
            font=("微软雅黑", 9)
        )
        self.interval_label.pack(side=tk.LEFT, padx=10)

        # 更新标签显示
        def update_interval_label(*args):
            self.interval_label.config(text=f"每 {self.extract_interval.get()} 帧提取一张")

        self.extract_interval.trace('w', update_interval_label)

        # 图片格式选择
        format_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        format_frame.pack(fill="x", pady=5)

        tk.Label(
            format_frame,
            text="🖼 图片格式：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.image_format = tk.StringVar(value="jpg")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.image_format,
            values=["jpg", "png", "bmp"],
            width=10,
            state="readonly"
        )
        format_combo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            format_frame,
            text="（JPG 文件小，PNG 质量高）",
            bg=self.colors['frame_bg'],
            fg='#888888',
            font=("微软雅黑", 8)
        ).pack(side=tk.LEFT, padx=10)

    def create_compress_tab(self):
        """创建视频压缩页面"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="📦 视频压缩")

        main_frame = tk.Frame(tab, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 文件选择区域
        self.create_file_section(main_frame, "输入视频文件", "compress")
        self.create_output_section(main_frame, "输出压缩视频", "compress")

        # 压缩设置
        settings_frame = tk.LabelFrame(
            main_frame,
            text="⚙ 压缩设置",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 11, "bold"),
            padx=15,
            pady=15
        )
        settings_frame.pack(fill="x", pady=10)

        # 压缩质量（CRF值）
        quality_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        quality_frame.pack(fill="x", pady=5)

        tk.Label(
            quality_frame,
            text="🎨 视频质量：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.compress_quality = tk.IntVar(value=23)
        quality_scale = tk.Scale(
            quality_frame,
            from_=18,
            to=51,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.compress_quality,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            highlightthickness=0,
            troughcolor=self.colors['accent']
        )
        quality_scale.pack(side=tk.LEFT, padx=10)

        self.quality_label = tk.Label(
            quality_frame,
            text="质量: 23 (平衡)",
            bg=self.colors['frame_bg'],
            fg=self.colors['info'],
            font=("微软雅黑", 9)
        )
        self.quality_label.pack(side=tk.LEFT, padx=10)

        # 更新质量标签
        def update_quality_label(*args):
            val = self.compress_quality.get()
            if val <= 23:
                desc = "高画质"
            elif val <= 35:
                desc = "中等画质"
            else:
                desc = "低画质"
            self.quality_label.config(text=f"CRF: {val} ({desc})")

        self.compress_quality.trace('w', update_quality_label)

        # 压缩预设
        preset_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        preset_frame.pack(fill="x", pady=5)

        tk.Label(
            preset_frame,
            text="⚡ 压缩速度：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.compress_preset = tk.StringVar(value="medium")
        preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.compress_preset,
            values=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
            width=15,
            state="readonly"
        )
        preset_combo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            preset_frame,
            text="（越慢压缩效果越好，文件越小）",
            bg=self.colors['frame_bg'],
            fg='#888888',
            font=("微软雅黑", 8)
        ).pack(side=tk.LEFT, padx=10)

    def create_convert_tab(self):
        """创建格式转换页面"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="🔄 格式转换")

        main_frame = tk.Frame(tab, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 文件选择区域
        self.create_file_section(main_frame, "输入视频文件", "convert")
        self.create_output_section(main_frame, "输出转换视频", "convert")

        # 转换设置
        settings_frame = tk.LabelFrame(
            main_frame,
            text="⚙ 转换设置",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 11, "bold"),
            padx=15,
            pady=15
        )
        settings_frame.pack(fill="x", pady=10)

        # 输出格式
        format_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        format_frame.pack(fill="x", pady=5)

        tk.Label(
            format_frame,
            text="📹 输出格式：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.convert_format = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.convert_format,
            values=["mp4", "avi", "mov", "mkv", "flv", "webm"],
            width=15,
            state="readonly"
        )
        format_combo.pack(side=tk.LEFT, padx=10)

        # 视频编码
        codec_frame = tk.Frame(settings_frame, bg=self.colors['frame_bg'])
        codec_frame.pack(fill="x", pady=5)

        tk.Label(
            codec_frame,
            text="🎬 视频编码：",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10)
        ).pack(side=tk.LEFT, padx=5)

        self.convert_codec = tk.StringVar(value="copy")
        codec_combo = ttk.Combobox(
            codec_frame,
            textvariable=self.convert_codec,
            values=["copy", "libx264", "libx265", "h264_nvenc"],
            width=15,
            state="readonly"
        )
        codec_combo.pack(side=tk.LEFT, padx=10)

        tk.Label(
            codec_frame,
            text="（copy=快速转换，libx264=高质量）",
            bg=self.colors['frame_bg'],
            fg='#888888',
            font=("微软雅黑", 8)
        ).pack(side=tk.LEFT, padx=10)

    def create_info_tab(self):
        """创建视频信息页面"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(tab, text="ℹ 视频信息")

        main_frame = tk.Frame(tab, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 文件选择
        self.create_file_section(main_frame, "选择视频查看信息", "info")

        # 信息显示区域
        info_frame = tk.LabelFrame(
            main_frame,
            text="📊 视频详细信息",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 11, "bold"),
            padx=15,
            pady=15
        )
        info_frame.pack(fill="both", expand=True, pady=10)

        # 使用文本框显示信息（支持滚动）
        text_frame = tk.Frame(info_frame, bg=self.colors['frame_bg'])
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_text = tk.Text(
            text_frame,
            bg='#0d1117',
            fg=self.colors['fg'],
            font=("Consolas", 10),
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            relief="flat",
            padx=10,
            pady=10
        )
        self.info_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.info_text.yview)

        # 获取信息按钮
        get_info_btn = self.create_modern_button(
            main_frame,
            text="🔍 获取视频信息",
            command=self.get_video_info,
            bg_color=self.colors['info'],
            width=20
        )
        get_info_btn.pack(pady=10)

    def create_file_section(self, parent, title, prefix):
        """创建文件选择区域"""
        frame = tk.LabelFrame(
            parent,
            text=title,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10, "bold"),
            padx=10,
            pady=10
        )
        frame.pack(fill="x", pady=5)

        # 文件路径显示
        label = tk.Label(
            frame,
            text="未选择文件",
            bg='#0d1117',
            fg=self.colors['fg'],
            relief="sunken",
            height=2,
            anchor="w",
            padx=10
        )
        label.pack(fill="x", pady=(0, 10))

        # 存储到实例变量
        setattr(self, f"{prefix}_file_label", label)

        # 选择按钮
        btn = self.create_modern_button(
            frame,
            text="📁 选择文件",
            command=lambda: self.select_file(prefix),
            bg_color=self.colors['info'],
            width=15
        )
        btn.pack()

    def create_output_section(self, parent, title, prefix):
        """创建输出文件夹选择区域"""
        frame = tk.LabelFrame(
            parent,
            text=title,
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            font=("微软雅黑", 10, "bold"),
            padx=10,
            pady=10
        )
        frame.pack(fill="x", pady=5)

        # 输出路径显示
        label = tk.Label(
            frame,
            text="未选择文件夹",
            bg='#0d1117',
            fg=self.colors['fg'],
            relief="sunken",
            height=2,
            anchor="w",
            padx=10
        )
        label.pack(fill="x", pady=(0, 10))

        # 存储到实例变量
        setattr(self, f"{prefix}_output_label", label)

        # 选择按钮
        btn = self.create_modern_button(
            frame,
            text="📂 选择文件夹",
            command=lambda: self.select_output(prefix),
            bg_color=self.colors['warning'],
            width=15
        )
        btn.pack()

    def select_file(self, prefix):
        """选择视频文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.input_video = file_path
            label = getattr(self, f"{prefix}_file_label")
            label.config(text=file_path[:80] + "..." if len(file_path) > 80 else file_path)
            self.update_status(f"已选择视频: {os.path.basename(file_path)}", 'info')

    def select_output(self, prefix):
        """选择输出文件夹"""
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder = folder_path
            label = getattr(self, f"{prefix}_output_label")
            label.config(text=folder_path)
            self.update_status(f"输出位置: {folder_path}", 'info')

    def start_processing(self):
        """开始处理"""
        if not self.input_video:
            messagebox.showerror("错误", "请先选择视频文件！")
            return

        if not self.output_folder:
            messagebox.showerror("错误", "请先选择输出文件夹！")
            return

        # 获取当前选中的功能
        current_tab = self.notebook.index(self.notebook.select())

        # 禁用开始按钮，启用停止按钮
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start(10)

        # 在新线程中处理
        self.processing_thread = threading.Thread(target=self.process, args=(current_tab,))
        self.processing_thread.start()

    def process(self, tab_index):
        """根据选中的标签页执行相应处理"""
        try:
            if tab_index == 0:  # 逐帧提取
                self.extract_frames()
            elif tab_index == 1:  # 视频压缩
                self.compress_video()
            elif tab_index == 2:  # 格式转换
                self.convert_video()
            else:
                self.update_status("请选择正确的功能", 'warning')

            self.window.after(0, self.processing_complete, True, "处理完成！")
        except Exception as e:
            self.window.after(0, self.processing_complete, False, f"错误：{str(e)}")

    def extract_frames(self):
        """逐帧提取图片"""
        output_dir = os.path.join(self.output_folder, f"frames_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(output_dir, exist_ok=True)

        interval = self.extract_interval.get()
        img_format = self.image_format.get()

        output_pattern = os.path.join(output_dir, f"frame_%06d.{img_format}")

        if interval == 1:
            cmd = ['ffmpeg', '-i', self.input_video', ' - q:v
            ', '
            2
            ', output_pattern]
            else:
            cmd = [
                'ffmpeg', '-i', self.input_video,
                '-vf', f'select=not(mod(n\\,{interval}))',
                '-vsync', 'vfr',
                '-q:v', '2',
                output_pattern
            ]

            self.update_status(f"开始提取帧，间隔: {interval}", 'info')
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"提取失败：{result.stderr}")

        frame_count = len([f for f in os.listdir(output_dir) if f.endswith(img_format)])
        self.update_status(f"成功提取 {frame_count} 张图片到 {output_dir}", 'success')

    def compress_video(self):
        """压缩视频"""
        base_name = os.path.splitext(os.path.basename(self.input_video))[0]
        output_file = os.path.join(self.output_folder,
                                   f"{base_name}_compressed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

        quality = self.compress_quality.get()
        preset = self.compress_preset.get()

        cmd = [
            'ffmpeg',
            '-i', self.input_video,
            '-vcodec', 'libx264',
            '-crf', str(quality),
            '-preset', preset,
            '-acodec', 'aac',
            '-b:a', '128k',
            output_file
        ]

        self.update_status(f"开始压缩视频，质量: CRF {quality}", 'info')
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"压缩失败：{result.stderr}")

        original_size = os.path.getsize(self.input_video) / (1024 * 1024)
        compressed_size = os.path.getsize(output_file) / (1024 * 1024)
        ratio = (1 - compressed_size / original_size) * 100

        self.update_status(
            f"压缩完成！原大小: {original_size:.1f}MB，现大小: {compressed_size:.1f}MB，减小: {ratio:.1f}%",
            'success'
        )

    def convert_video(self):
        """转换视频格式"""
        base_name = os.path.splitext(os.path.basename(self.input_video))[0]
        output_format = self.convert_format.get()
        output_file = os.path.join(self.output_folder,
                                   f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}")

        codec = self.convert_codec.get()

        if codec == 'copy':
            cmd = ['ffmpeg', '-i', self.input_video, '-c', 'copy', output_file]
        else:
            cmd = ['ffmpeg', '-i', self.input_video, '-vcodec', codec, '-acodec', 'aac', output_file]

        self.update_status(f"开始转换格式: {output_format.upper()}", 'info')
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"转换失败：{result.stderr}")

        self.update_status(f"转换完成！输出文件: {os.path.basename(output_file)}", 'success')

    def get_video_info(self):
        """获取视频信息"""
        if not self.input_video:
            messagebox.showerror("错误", "请先选择视频文件！")
            return

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "正在获取视频信息...\n")
        self.window.update()

        cmd = ['ffprobe', '-i', self.input_video, '-show_format', '-show_streams', '-v', 'quiet']

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            # 使用 ffmpeg 获取更友好的信息
            cmd2 = ['ffmpeg', '-i', self.input_video, '-hide_banner']
            result2 = subprocess.run(cmd2, capture_output=True, text=True)

            info_text = "=" * 50 + "\n"
            info_text += "视频文件信息\n"
            info_text += "=" * 50 + "\n\n"

            # 解析输出
            lines = result2.stderr.split('\n')
            for line in lines:
                if 'Duration' in line or 'Stream' in line or 'Video' in line or 'Audio' in line:
                    info_text += line.strip() + "\n"

            info_text += "\n" + "=" * 50 + "\n"
            info_text += f"文件路径: {self.input_video}\n"
            info_text += f"文件大小: {os.path.getsize(self.input_video) / (1024 * 1024):.2f} MB\n"

            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
            self.update_status("视频信息获取完成", 'success')

        except Exception as e:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"获取信息失败：{str(e)}")
            self.update_status("获取信息失败", 'danger')

    def stop_processing(self):
        """停止处理"""
        self.update_status("正在停止...", 'warning')
        # 这里可以添加终止子进程的逻辑
        self.processing_complete(False, "已停止处理")

    def update_status(self, message, status_type='info'):
        """更新状态显示"""
        colors = {
            'info': self.colors['info'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'danger': self.colors['danger']
        }
        self.status_icon.config(fg=colors.get(status_type, self.colors['info']))
        self.status_label.config(text=message)
        self.window.update_idletasks()

    def processing_complete(self, success, message):
        """处理完成后的清理"""
        self.progress_bar.stop()
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

        if success:
            self.update_status(message, 'success')
            messagebox.showinfo("完成", message)
        else:
            self.update_status(message, 'danger')
            if "错误" not in message:
                messagebox.showerror("错误", message)

    def clear_all(self):
        """清空所有选择"""
        self.input_video = ""
        self.output_folder = ""

        # 清空所有标签
        for attr in dir(self):
            if attr.endswith('_file_label') or attr.endswith('_output_label'):
                label = getattr(self, attr)
                if label:
                    label.config(text="未选择文件" if '_file_' in attr else "未选择文件夹")

        self.update_status("已清空所有选择", 'info')

    def on_closing(self):
        """窗口关闭时的处理"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.window.destroy()

    def run(self):
        """运行程序"""
        self.window.mainloop()


# 程序入口
if __name__ == "__main__":
    app = ModernFFmpegGUI()
    app.run()