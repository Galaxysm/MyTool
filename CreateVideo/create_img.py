from PIL import Image, ImageDraw, ImageFont
import textwrap
import os


def generate_text_image(
        text,
        font_path,
        font_size,
        bg_color,
        image_size,
        output_path
):
    """
    生成文本图片并保存

    参数:
        text (str): 要转换为图片的文本
        font_path (str): 字体文件路径
        font_size (int): 字体大小
        bg_color (tuple): 背景颜色 (R, G, B)
        image_size (tuple): 图片尺寸 (width, height)
        output_path (str): 输出图片路径
    """
    try:
        font = ImageFont.truetype(font_path, font_size)
        img_width, img_height = image_size

        # 创建临时图像来计算文本尺寸
        temp_img = Image.new('RGB', (1, 1), bg_color)
        temp_draw = ImageDraw.Draw(temp_img)

        # 计算每行文本的宽度和高度
        lines = []
        max_line_width = 0
        for paragraph in text.split('\n'):
            wrapped_lines = textwrap.wrap(paragraph, width=50)  # 适当调整换行宽度
            lines.extend(wrapped_lines)

        # 计算总文本高度和最大行宽度
        line_height = font.getbbox("Ay")[3]  # 获取行高
        total_text_height = len(lines) * line_height

        for line in lines:
            bbox = temp_draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            if line_width > max_line_width:
                max_line_width = line_width

        # 创建最终图像
        image = Image.new("RGB", image_size, color=bg_color)
        draw = ImageDraw.Draw(image)

        # 计算起始Y位置（垂直居中）
        y = (img_height - total_text_height) // 2

        for line in lines:
            # 计算当前行的宽度（水平居中）
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (img_width - line_width) // 2

            # 绘制文本
            draw.text((x, y), line, fill=(255, 255, 255), font=font)
            y += line_height

        # 保存图片
        image.save(output_path)
        print(f"图片已成功保存至: {output_path}")
        return True

    except Exception as e:
        print(f"生成失败：{e}")
        return False


def main():
    count = 1
    while count <= 33:
        formatted_count = str(count).zfill(2)

        # 示例参数
        params = {
            "text": f"盗墓笔记8\n大结局上{formatted_count}",
            "font_path": r"1657940861632229.ttf",  # 替换为实际字体路径
            "font_size": 100,
            "bg_color": (0, 0, 0),
            "image_size": (1920, 1080),
            "output_path": f"E:\douyin\img\\{formatted_count}.png"
        }

        # 调用生成函数
        generate_text_image(**params)

        count += 1


if __name__ == "__main__":
    main()