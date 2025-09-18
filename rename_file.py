import os


def main():
    # 设置参数
    folder_path = r"F:\2025\Check\NF4016"  # 要重命名的文件夹路径
    prefix = "新文件"  # 新文件名前缀
    start_num = 1  # 起始编号

    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return

    # 获取所有文件
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    files.sort()  # 按名称排序

    print(f"找到 {len(files)} 个文件准备重命名")

    # 重命名文件
    for i, filename in enumerate(files, start=start_num):
        file_ext = os.path.splitext(filename)[1]  # 获取扩展名
        new_filename = f"{prefix}_{i:03d}{file_ext}"  # 新文件名
        old_path = os.path.join(folder_path, filename)
        new_path = os.path.join(folder_path, new_filename)

        # 避免文件名冲突
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"重命名: {filename} -> {new_filename}")
        else:
            print(f"跳过: {filename} (目标文件已存在)")

    print("重命名完成！")


if __name__ == "__main__":
    main()
