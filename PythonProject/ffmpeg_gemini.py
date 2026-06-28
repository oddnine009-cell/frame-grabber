import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# 设置主题和颜色
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class VideoFrameExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("视频逐帧提取工具 (基于 FFmpeg)")
        self.geometry("720x680")
        self.resizable(False, False)

        # 1. 视频文件输入
        self.lbl_input = ctk.CTkLabel(self, text="视频文件:", font=("Arial", 14, "bold"))
        self.lbl_input.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.entry_input = ctk.CTkEntry(self, width=380, placeholder_text="请选择视频文件路径...")
        self.entry_input.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="w")

        self.btn_input = ctk.CTkButton(self, text="浏览文件", width=100, command=self.browse_input)
        self.btn_input.grid(row=0, column=2, padx=10, pady=(20, 10))

        # 2. 输出目录设置
        self.lbl_output = ctk.CTkLabel(self, text="输出目录:", font=("Arial", 14, "bold"))
        self.lbl_output.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.entry_output = ctk.CTkEntry(self, width=380, placeholder_text="请选择图片保存文件夹...")
        self.entry_output.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.btn_output = ctk.CTkButton(self, text="选择目录", width=100, command=self.browse_output)
        self.btn_output.grid(row=1, column=2, padx=10, pady=10)

        # 3. 提取模式与间隔设置
        self.lbl_mode = ctk.CTkLabel(self, text="提取设置:", font=("Arial", 14, "bold"))
        self.lbl_mode.grid(row=2, column=0, padx=20, pady=10, sticky="nw")

        self.frame_mode = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_mode.grid(row=2, column=1, columnspan=2, sticky="w")

        self.mode_var = ctk.StringVar(value="interval")

        self.radio_interval = ctk.CTkRadioButton(
            self.frame_mode,
            text="按时间间隔",
            variable=self.mode_var,
            value="interval"
        )
        self.radio_interval.grid(row=0, column=0, padx=(10, 20), pady=10)

        self.radio_all = ctk.CTkRadioButton(
            self.frame_mode,
            text="提取所有帧(极占空间)",
            variable=self.mode_var,
            value="all"
        )
        self.radio_all.grid(row=0, column=1, padx=10, pady=10)

        self.entry_interval = ctk.CTkEntry(self.frame_mode, width=80)
        self.entry_interval.insert(0, "1")
        self.entry_interval.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.lbl_sec = ctk.CTkLabel(self.frame_mode, text="秒 / 帧", text_color="gray")
        self.lbl_sec.grid(row=1, column=0, padx=(100, 0), pady=5, sticky="w")

        # 4. 图片格式选择
        self.lbl_format = ctk.CTkLabel(self, text="图片格式:", font=("Arial", 14, "bold"))
        self.lbl_format.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.combo_format = ctk.CTkComboBox(self, values=["jpg", "png"], width=120)
        self.combo_format.set("jpg")
        self.combo_format.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # 5. 画质设置
        self.lbl_quality = ctk.CTkLabel(self, text="图片画质:", font=("Arial", 14, "bold"))
        self.lbl_quality.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.combo_quality = ctk.CTkComboBox(
            self,
            values=["最高质量", "高质量", "中等质量", "低占用"],
            width=120
        )
        self.combo_quality.set("高质量")
        self.combo_quality.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.lbl_quality_tip = ctk.CTkLabel(
            self,
            text="JPG 会影响清晰度；PNG 主要影响压缩大小",
            text_color="gray"
        )
        self.lbl_quality_tip.grid(row=4, column=1, padx=(150, 0), pady=10, sticky="w")

        # 6. 分辨率设置
        self.lbl_resolution = ctk.CTkLabel(self, text="输出分辨率:", font=("Arial", 14, "bold"))
        self.lbl_resolution.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.frame_resolution = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resolution.grid(row=5, column=1, columnspan=2, sticky="w")

        self.combo_resolution = ctk.CTkComboBox(
            self.frame_resolution,
            values=["保持原始", "720p", "1080p", "2K", "4K", "自定义"],
            width=120,
            command=self.on_resolution_change
        )
        self.combo_resolution.set("保持原始")
        self.combo_resolution.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.entry_width = ctk.CTkEntry(self.frame_resolution, width=80, placeholder_text="宽")
        self.entry_width.grid(row=0, column=1, padx=(20, 5), pady=5)

        self.lbl_x = ctk.CTkLabel(self.frame_resolution, text="×")
        self.lbl_x.grid(row=0, column=2, padx=5)

        self.entry_height = ctk.CTkEntry(self.frame_resolution, width=80, placeholder_text="高")
        self.entry_height.grid(row=0, column=3, padx=5, pady=5)

        self.lbl_resolution_tip = ctk.CTkLabel(
            self.frame_resolution,
            text="自定义时填写，例如 1920 × 1080",
            text_color="gray"
        )
        self.lbl_resolution_tip.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")

        self.entry_width.configure(state="disabled")
        self.entry_height.configure(state="disabled")

        # 7. 日志与进度输出
        self.log_textbox = ctk.CTkTextbox(self, width=660, height=170, font=("Consolas", 12))
        self.log_textbox.grid(row=6, column=0, columnspan=3, padx=20, pady=15)
        self.log_textbox.insert("0.0", "准备就绪。等待开始...\n")
        self.log_textbox.configure(state="disabled")

        # 8. 开始按钮
        self.btn_start = ctk.CTkButton(
            self,
            text="▶ 开始批量提取",
            height=40,
            font=("Arial", 16, "bold"),
            command=self.start_processing
        )
        self.btn_start.grid(row=7, column=0, columnspan=3, pady=(10, 20))

    # ---------------- 交互逻辑 ----------------

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
                ("所有文件", "*.*")
            ]
        )

        if file_path:
            self.entry_input.delete(0, "end")
            self.entry_input.insert(0, file_path)

            default_out_dir = os.path.splitext(file_path)[0] + "_frames"
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, default_out_dir)

    def browse_output(self):
        dir_path = filedialog.askdirectory(title="选择图片保存路径")

        if dir_path:
            self.entry_output.delete(0, "end")
            self.entry_output.insert(0, dir_path)

    def on_resolution_change(self, choice):
        """选择自定义分辨率时，允许输入宽高"""
        if choice == "自定义":
            self.entry_width.configure(state="normal")
            self.entry_height.configure(state="normal")
        else:
            self.entry_width.delete(0, "end")
            self.entry_height.delete(0, "end")
            self.entry_width.configure(state="disabled")
            self.entry_height.configure(state="disabled")

    def log(self, message):
        """将信息打印到界面文本框中，兼容多线程"""
        if threading.current_thread() is not threading.main_thread():
            self.after(0, lambda: self.log(message))
            return

        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_processing(self):
        in_file = self.entry_input.get().strip()
        out_dir = self.entry_output.get().strip()
        mode = self.mode_var.get()
        fmt = self.combo_format.get()
        interval = self.entry_interval.get().strip()
        quality = self.combo_quality.get()
        resolution = self.combo_resolution.get()
        width = self.entry_width.get().strip()
        height = self.entry_height.get().strip()

        # 校验视频文件
        if not in_file or not os.path.isfile(in_file):
            messagebox.showerror("错误", "请提供有效的视频文件路径！")
            return

        # 校验输出目录
        if not out_dir:
            messagebox.showerror("错误", "请提供输出目录！")
            return

        # 校验时间间隔
        if mode == "interval":
            try:
                val = float(interval)
                if val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("错误", "时间间隔必须是大于 0 的数字！")
                return

        # 校验自定义分辨率
        if resolution == "自定义":
            if not width or not height:
                messagebox.showerror("错误", "自定义分辨率需要填写宽度和高度！")
                return

            try:
                width_val = int(width)
                height_val = int(height)

                if width_val <= 0 or height_val <= 0:
                    raise ValueError

                # FFmpeg 更推荐偶数分辨率
                if width_val % 2 != 0 or height_val % 2 != 0:
                    messagebox.showerror("错误", "宽度和高度建议填写偶数，例如 1920 × 1080！")
                    return

            except ValueError:
                messagebox.showerror("错误", "宽度和高度必须是正整数！")
                return

        # 创建输出文件夹
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录：{e}")
                return

        # 禁用按钮，防止重复点击
        self.btn_start.configure(state="disabled", text="处理中...")
        self.log("-" * 50)
        self.log(f"开始处理: {os.path.basename(in_file)}")
        self.log(f"图片格式: {fmt}")
        self.log(f"画质设置: {quality}")
        self.log(f"分辨率设置: {resolution}")

        # 开启新线程运行 FFmpeg
        threading.Thread(
            target=self.run_ffmpeg,
            args=(in_file, out_dir, mode, interval, fmt, quality, resolution, width, height),
            daemon=True
        ).start()

    def run_ffmpeg(self, in_file, out_dir, mode, interval, fmt, quality, resolution, width, height):
        output_pattern = os.path.join(out_dir, f"frame_%06d.{fmt}")

        cmd = ["ffmpeg", "-y", "-i", in_file]

        # ---------------- 组装滤镜 ----------------
        filters = []

        # 按时间间隔抽帧
        if mode == "interval":
            filters.append(f"fps=1/{interval}")

        # 分辨率设置
        if resolution == "720p":
            filters.append("scale=-2:720")
        elif resolution == "1080p":
            filters.append("scale=-2:1080")
        elif resolution == "2K":
            filters.append("scale=-2:1440")
        elif resolution == "4K":
            filters.append("scale=-2:2160")
        elif resolution == "自定义":
            filters.append(f"scale={width}:{height}")

        # 如果有滤镜，就加入 -vf
        if filters:
            cmd.extend(["-vf", ",".join(filters)])

        # ---------------- 画质设置 ----------------
        if fmt == "jpg":
            # JPG 的 -q:v 数值越小，画质越高，文件越大
            jpg_quality_map = {
                "最高质量": "1",
                "高质量": "2",
                "中等质量": "5",
                "低占用": "8"
            }
            cmd.extend(["-q:v", jpg_quality_map.get(quality, "2")])

        elif fmt == "png":
            # PNG 是无损格式，compression_level 主要影响文件大小和压缩速度
            png_compress_map = {
                "最高质量": "0",
                "高质量": "3",
                "中等质量": "6",
                "低占用": "9"
            }
            cmd.extend(["-compression_level", png_compress_map.get(quality, "3")])

        cmd.append(output_pattern)

        self.log(f"执行命令: {' '.join(cmd)}")

        try:
            # 隐藏命令行窗口，主要针对 Windows
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
                startupinfo=startupinfo
            )

            # 读取 FFmpeg 输出，避免管道堵塞
            for line in process.stdout:
                # 不逐行打印，避免日志太多导致界面卡顿
                pass

            process.wait()

            if process.returncode == 0:
                self.log(f"✅ 提取完成！图片已保存至:\n{out_dir}")
            else:
                self.log(f"❌ 处理失败，FFmpeg 返回码: {process.returncode}")

        except FileNotFoundError:
            self.log("❌ 找不到 FFmpeg！请确认是否已安装并添加到了环境变量。")
        except Exception as e:
            self.log(f"❌ 发生意外错误: {str(e)}")
        finally:
            self.after(
                0,
                lambda: self.btn_start.configure(
                    state="normal",
                    text="▶ 开始批量提取"
                )
            )


if __name__ == "__main__":
    app = VideoFrameExtractor()
    app.mainloop()