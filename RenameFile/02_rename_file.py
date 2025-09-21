import os
import pandas as pd
from openpyxl import load_workbook
import re


def process_video_files(excel_path, folder_path):
    """
    处理视频文件重命名和Excel标记，不改变Excel原有格式

    Args:
        excel_path (str): Excel文件路径
        folder_path (str): 视频文件夹路径
    """

    # 支持的视频格式
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v', '.webm', '.MP4', '.AVI', '.MOV', '.MKV', '.mpeg']

    try:
        # 使用openpyxl加载工作簿，保持格式
        wb = load_workbook(excel_path)

        # 检查工作表是否存在
        if 'Auto超链接' not in wb.sheetnames:
            print("Excel中未找到'Auto超链接'工作表")
            return

        ws = wb['Auto超链接']

        # 查找列索引
        title_col_idx = None
        exist_col_idx = None

        # 查找标题列和存在列的位置
        for col_idx in range(1, ws.max_column + 1):
            cell_value = ws.cell(row=1, column=col_idx).value
            if cell_value == '标题':
                title_col_idx = col_idx
            elif cell_value == '存在':
                exist_col_idx = col_idx

        if title_col_idx is None:
            print("Excel中未找到'标题'列")
            return

        # 如果不存在列，则在最后一列后添加
        if exist_col_idx is None:
            exist_col_idx = ws.max_column + 1
            ws.cell(row=1, column=exist_col_idx, value='存在')
            print("已添加'存在'列")

        # 收集标题和对应的行索引
        titles_info = {}  # {标题: 行索引}
        existing_titles = set()  # 已经标记为存在的标题

        for row_idx in range(2, ws.max_row + 1):
            title_value = ws.cell(row=row_idx, column=title_col_idx).value
            exist_value = ws.cell(row=row_idx, column=exist_col_idx).value

            if title_value and pd.notna(title_value):
                titles_info[str(title_value).strip()] = row_idx
                if exist_value == '已存在':
                    existing_titles.add(str(title_value).strip())

        titles_to_process = [title for title in titles_info.keys() if title not in existing_titles]

        print(f"找到 {len(titles_info)} 个标题，其中 {len(titles_to_process)} 个需要处理")

        # 获取文件夹中的所有视频文件
        video_files = []
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext.lower()) for ext in video_extensions):
                video_files.append(file)

        print(f"找到 {len(video_files)} 个视频文件")

        # 处理每个视频文件
        processed_count = 0
        for video_file in video_files:
            file_path = os.path.join(folder_path, video_file)
            file_name, file_ext = os.path.splitext(video_file)

            # 按"-"分割文件名
            parts = file_name.split('-')

            if len(parts) >= 2:
                # 构建匹配模式
                if len(parts) == 2:
                    # 两部分的情况
                    match_pattern1 = f"{parts[0]}-{parts[1]}"
                    match_pattern2 = f"{parts[0]}{parts[1]}"
                    serial_number = None
                else:
                    # 三部分或更多的情况
                    match_pattern1 = f"{parts[0]}-{parts[1]}"
                    match_pattern2 = f"{parts[0]}{parts[1]}"
                    serial_number = parts[2]

                # 在需要处理的标题中查找匹配项
                matched_title = None
                for title in titles_to_process:
                    title_clean = title.replace(" ", "").replace("-", "")
                    pattern1_clean = match_pattern1.replace(" ", "").replace("-", "")
                    pattern2_clean = match_pattern2.replace(" ", "").replace("-", "")

                    # 多种匹配方式
                    if (match_pattern1 in title or
                            match_pattern2 in title or
                            title.startswith(match_pattern1) or
                            title.startswith(match_pattern2) or
                            pattern1_clean in title_clean or
                            pattern2_clean in title_clean):
                        matched_title = title
                        break

                if not matched_title:
                    # 检查是否已经存在
                    for title in existing_titles:
                        title_clean = title.replace(" ", "").replace("-", "")
                        pattern1_clean = match_pattern1.replace(" ", "").replace("-", "")
                        pattern2_clean = match_pattern2.replace(" ", "").replace("-", "")

                        if (match_pattern1 in title or
                                match_pattern2 in title or
                                pattern1_clean in title_clean or
                                pattern2_clean in title_clean):
                            #print(f"文件 {video_file} 匹配到已存在的标题 '{title}'，跳过处理")
                            break
                    else:
                        print(f"未找到匹配的标题: {video_file}")
                    continue

                # 构建新文件名
                if serial_number:
                    new_file_name = f"{matched_title}-{serial_number}{file_ext}"
                else:
                    new_file_name = f"{matched_title}{file_ext}"

                # 清理文件名中的非法字符
                new_file_name = re.sub(r'[<>:"/\\|?*]', '', new_file_name)

                # 重命名文件
                new_file_path = os.path.join(folder_path, new_file_name)

                try:
                    # 检查目标文件是否已存在
                    if os.path.exists(new_file_path):
                        print(f"目标文件已存在，跳过重命名: {new_file_name}")
                        continue

                    os.rename(file_path, new_file_path)
                    print(f"重命名: {video_file} -> {new_file_name}")

                    # 在Excel中标记为"已存在"
                    row_idx = titles_info[matched_title]
                    ws.cell(row=row_idx, column=exist_col_idx, value='已存在')
                    print(f"标记标题 '{matched_title}' 为已存在")

                    # 从待处理列表中移除
                    if matched_title in titles_to_process:
                        titles_to_process.remove(matched_title)

                    processed_count += 1

                except Exception as e:
                    print(f"重命名失败 {video_file}: {e}")

        # 保存Excel文件（保持原有格式）
        try:
            wb.save(excel_path)
            print(f"Excel文件已保存，共处理了 {processed_count} 个文件")
        except Exception as e:
            print(f"保存Excel失败，请确保文件没有被其他程序占用: {e}")

    except Exception as e:
        print(f"处理过程中出错: {e}")


# 使用示例
if __name__ == "__main__":
    # 设置你的Excel文件路径和视频文件夹路径
    excel_file_path = r"../DownloadVideo/Resource/BT.xlsx"  # Excel文件路径
    video_folder_path = r"E:\02_ACG\映画\步兵系列"  # 视频文件夹路径

    process_video_files(excel_file_path, video_folder_path)