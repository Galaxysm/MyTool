import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# 生成图片的函数
def generate_text_image(
    text,
    font_path,
    font_size,
    bg_color,
    image_size
):
    try:
        font = ImageFont.truetype(font_path, font_size)
        img_width, img_height = image_size
        max_text_width = int(img_width * 0.9)

        lines = []
        for paragraph in text.split('\n'):
            wrapper = textwrap.TextWrapper(width=int(max_text_width / (font_size * 0.6)))
            wrapped_lines = wrapper.wrap(text=paragraph)
            lines.extend(wrapped_lines)

        line_height = font.getbbox("Ay")[3]
        text_height = line_height * len(lines)

        image = Image.new("RGB", image_size, color=bg_color)
        draw = ImageDraw.Draw(image)

        y = (img_height - text_height) // 2
        for line in lines:
            draw.text((100, y), line, fill=(255, 255, 255), font=font)
            y += line_height

        return image
    except Exception as e:
        print(f"生成失败：{e}")
        return None

# GUI 主程序
class TextToImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文本转图片工具")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        self.root.option_add("*Font", "微软雅黑 10")

        # 设置窗口背景色为现代风格
        self.root.configure(bg="#f4f6f9")

        # 自定义按钮样式
        self.style_button = {
            "bg": "#4A90E2",
            "fg": "white",
            "font": ("微软雅黑", 10, "bold"),
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 0,
            "activebackground": "#357ABD",
            "activeforeground": "white",
            "width": 12,
            "height": 1,
            "padx": 10,
            "pady": 5,
            "cursor": "hand2",
            "borderwidth": 0,
            "highlightcolor": "#4A90E2"
        }

        # 文本输入
        tk.Label(root, text="输入文字：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=10)
        self.text_entry = tk.Text(root, height=10, width=50, wrap=tk.WORD, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.text_entry.grid(row=0, column=1, columnspan=2, sticky="w", padx=15, pady=5)
        self.text_entry.drop_target_register(DND_FILES)
        self.text_entry.dnd_bind('<<Drop>>', self.handle_drop)

        # 字体路径
        tk.Label(root, text="字体路径：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=1, column=0, sticky="w", padx=15, pady=10)
        self.font_path_entry = tk.Entry(root, width=40, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.font_path_entry.grid(row=1, column=1, sticky="w", padx=15, pady=5)
        tk.Button(root, text="浏览...", **self.style_button, command=self.select_font).grid(row=1, column=2, padx=5, pady=5)

        # 字体大小
        tk.Label(root, text="字体大小：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=2, column=0, sticky="w", padx=15, pady=10)
        self.font_size_entry = tk.Entry(root, width=10, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.font_size_entry.insert(0, "60")
        self.font_size_entry.grid(row=2, column=1, sticky="w", padx=15, pady=5)

        # 背景颜色
        tk.Label(root, text="背景颜色（RGB）：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=3, column=0, sticky="w", padx=15, pady=10)
        self.bg_color_entry = tk.Entry(root, width=20, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.bg_color_entry.insert(0, "(0, 0, 0)")
        self.bg_color_entry.grid(row=3, column=1, sticky="w", padx=15, pady=5)

        # 图片尺寸
        tk.Label(root, text="图片尺寸（宽x高）：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=4, column=0, sticky="w", padx=15, pady=10)
        self.image_size_entry = tk.Entry(root, width=15, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.image_size_entry.insert(0, "(1920, 1080)")
        self.image_size_entry.grid(row=4, column=1, sticky="w", padx=15, pady=5)

        # 输出路径
        tk.Label(root, text="输出路径：", bg="#f4f6f9", font=("微软雅黑", 10, "bold")).grid(row=5, column=0, sticky="w", padx=15, pady=10)
        self.output_path_entry = tk.Entry(root, width=40, font=("微软雅黑", 10), bd=0, relief="solid", highlightbackground="#ccc", highlightthickness=1)
        self.output_path_entry.grid(row=5, column=1, sticky="w", padx=15, pady=5)
        tk.Button(root, text="选择保存路径", **self.style_button, command=self.select_output).grid(row=5, column=2, padx=5, pady=5)

        # 生成按钮
        tk.Button(root, text="生成图片", **self.style_button, command=self.save_image).grid(row=6, column=1, pady=20)

    def select_font(self):
        path = filedialog.askopenfilename(filetypes=[("字体文件", "*.ttf *.TTF")])
        if path:
            self.font_path_entry.delete(0, tk.END)
            self.font_path_entry.insert(0, path)

    def select_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG 图片", "*.png")])
        if path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, path)

    def handle_drop(self, event):
        file_path = event.data.strip()
        if os.path.isfile(file_path) and file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_entry.delete(1.0, tk.END)
                self.text_entry.insert(tk.END, content)

    def save_image(self):
        try:
            text = self.text_entry.get("1.0", tk.END).strip()
            if not text:
                messagebox.showerror("错误", "请输入文字内容！")
                return

            font_path = self.font_path_entry.get()
            if not os.path.isfile(font_path):
                messagebox.showerror("错误", "字体路径无效！")
                return

            font_size = int(self.font_size_entry.get())
            if font_size <= 0:
                messagebox.showerror("错误", "字体大小必须为正数！")
                return

            bg_color = eval(self.bg_color_entry.get())
            image_size = eval(self.image_size_entry.get())
            output_path = self.output_path_entry.get()

            if not output_path:
                messagebox.showerror("错误", "请选择输出路径！")
                return

            image = generate_text_image(
                text=text,
                font_path=font_path,
                font_size=font_size,
                bg_color=bg_color,
                image_size=image_size
            )

            if image:
                image.save(output_path)
                messagebox.showinfo("成功", f"图片已保存至：{output_path}")
            else:
                messagebox.showerror("错误", "图片生成失败！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

# 启动 GUI
if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = TextToImageApp(root)
    root.mainloop()