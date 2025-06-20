import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import threading
import ttkbootstrap as tb

class VideoFrameReplacerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频帧替换工具 - v2.0")
        self.root.geometry("750x450")
        self.root.resizable(True, True)
        self.center_window()

        # 初始化变量
        self.input_video_path = tk.StringVar()
        self.image_path = tk.StringVar()
        self.output_video_path = tk.StringVar()

        # 设置样式
        self.configure_styles()

        # 创建 UI
        self.create_widgets()

    def configure_styles(self):
        style = tb.Style()
        # 设置 Entry 的文本左对齐
        style.configure("TEntry", justify="left")
        # 设置按钮样式
        style.configure("info.TButton", font=("微软雅黑", 10), padding=6)
        style.configure("danger.TButton", font=("微软雅黑", 10), padding=6)
        style.configure("success.TButton", font=("微软雅黑", 10), padding=6)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # 标题
        title_label = tb.Label(self.root, text="视频帧替换工具", bootstyle="primary", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)

        # 主框架
        main_frame = tb.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # 输入视频
        input_frame = tb.Frame(main_frame)
        input_frame.pack(pady=5, fill="x")
        tb.Label(input_frame, text="输入视频文件:", font=("微软雅黑", 10)).pack(side="left")
        tb.Entry(
            input_frame,
            textvariable=self.input_video_path,
            width=40,
        ).pack(side="left", padx=5)
        tb.Button(input_frame, text="浏览", command=self.select_video, bootstyle="primary").pack(side="left")

        # 替换图片
        image_frame = tb.Frame(main_frame)
        image_frame.pack(pady=5, fill="x")
        tb.Label(image_frame, text="替换图片:", font=("微软雅黑", 10)).pack(side="left")
        tb.Entry(
            image_frame,
            textvariable=self.image_path,
            width=40,
        ).pack(side="left", padx=5)
        tb.Button(image_frame, text="浏览", command=self.select_image, bootstyle="primary").pack(side="left")

        # 输出视频
        output_frame = tb.Frame(main_frame)
        output_frame.pack(pady=5, fill="x")
        tb.Label(output_frame, text="输出视频文件:", font=("微软雅黑", 10)).pack(side="left")
        tb.Entry(
            output_frame,
            textvariable=self.output_video_path,
            width=40,
        ).pack(side="left", padx=5)
        tb.Button(output_frame, text="浏览", command=self.select_output, bootstyle="primary").pack(side="left")

        # 进度条
        self.progress = tb.Progressbar(main_frame, orient="horizontal", length=500, mode="determinate", bootstyle="info")
        self.progress.pack(pady=10)

        # 操作按钮
        self.process_button = tb.Button(main_frame, text="开始处理", command=self.start_processing, bootstyle="success", width=15)
        self.process_button.pack(pady=5)

        # 状态标签
        self.status_label = tb.Label(main_frame, text="", font=("微软雅黑", 10), bootstyle="info")
        self.status_label.pack()

    def select_video(self):
        file_path = filedialog.askopenfilename(
            title="选择输入视频",
            filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_video_path.set(file_path)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择替换图片",
            filetypes=[("图片文件", "*.jpg *.png *.jpeg"), ("所有文件", "*.*")]
        )
        if file_path:
            self.image_path.set(file_path)

    def select_output(self):
        file_path = filedialog.asksaveasfilename(
            title="保存输出视频",
            defaultextension=".mp4",
            filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_video_path.set(file_path)

    def start_processing(self):
        if self.process_button["text"] == "开始处理":
            self.process_button.config(state=tk.DISABLED, text="处理中...")
            self.status_label.config(text="初始化...", bootstyle="info")
            self.progress["value"] = 0
            threading.Thread(target=self.process_video).start()

    def process_video(self):
        input_path = self.input_video_path.get()
        image_path = self.image_path.get()
        output_path = self.output_video_path.get()

        if not all([input_path, image_path, output_path]):
            self.update_status("请填写所有路径", bootstyle="danger")
            self.process_button.config(state=tk.NORMAL, text="开始处理")
            return

        self.update_status("处理中...", bootstyle="info")
        self.progress["value"] = 0

        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise Exception("无法打开输入视频")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            image = cv2.imread(image_path)
            if image is None:
                raise Exception("无法读取图片")

            resized_image = cv2.resize(image, (width, height))

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            if not out.isOpened():
                raise Exception("无法创建输出视频")

            for i in range(total_frames):
                out.write(resized_image)
                progress = int((i + 1) / total_frames * 100)
                self.progress["value"] = progress
                self.root.after(0, self.update_status, f"处理中... {progress}%", "info")

            out.release()
            cap.release()
            self.update_status("处理完成", "success")
            messagebox.showinfo("成功", f"视频已保存至: {output_path}")
        except Exception as e:
            self.update_status("处理失败", "danger")
            messagebox.showerror("错误", str(e))
        finally:
            self.process_button.config(state=tk.NORMAL, text="开始处理")

    def update_status(self, text, bootstyle):
        self.status_label.config(text=text, bootstyle=bootstyle)

if __name__ == "__main__":
    root = tb.Window(themename="cosmo")  # 可选主题: 'cosmo', 'darkly', 'flatly', 'journal', 'lumen', 'minty', 'pulse', 'sandstone', 'united', 'yeti'
    app = VideoFrameReplacerApp(root)
    root.mainloop()