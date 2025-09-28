import os
from moviepy.editor import *


def wma_to_mp4_ffmpeg_direct(wma_file, image_file, output_mp4):
    """直接用 FFmpeg 合成（推荐）"""
    cmd = (
        f'ffmpeg -loop 1 -i "{image_file}" -i "{wma_file}" '
        f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k '
        f'-pix_fmt yuv420p -shortest -y "{output_mp4}"'
    )
    os.system(cmd)
    print(f"✅ 转换成功！输出文件：{output_mp4}")


# 参数设定
count = 1           # 起始index
max_count = 33      # 终止index
wma_file = f"E:\\01_影视动漫\有声书\盗墓笔记8之大结局上(周建龙)[33回]\盗墓笔记8-大结局上"
img_file = f"E:\douyin\img\\"
output_mp4 = f"E:\douyin\大结局上"

while count <= max_count:
    formatted_count = str(count).zfill(2)
    wma_to_mp4_ffmpeg_direct(
        wma_file + f"{formatted_count}.wma",
        img_file + f"{formatted_count}.png",
        output_mp4 + f"{formatted_count}.mp4")

    count += 1
