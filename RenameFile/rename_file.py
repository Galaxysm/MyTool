import os
import shutil
from pathlib import Path


def batch_organize_files(source_folder, target_folder=None, prefix="file", start_num=1,
                         extension=None, rename_files=True):
    """
    批量整理指定文件夹中的所有文件（包括子文件夹），可选择是否重命名

    参数:
        source_folder (str): 源文件夹路径
        target_folder (str): 目标文件夹路径，None表示使用源文件夹
        prefix (str): 文件名的前缀（仅在重命名时使用）
        start_num (int): 起始编号（仅在重命名时使用）
        extension (str): 指定文件扩展名(如".txt")，None表示所有文件
        rename_files (bool): 是否重命名文件，False时只移动不重命名
    """
    # 设置目标文件夹
    if target_folder is None:
        target_folder = source_folder
    else:
        # 创建目标文件夹（如果不存在）
        os.makedirs(target_folder, exist_ok=True)

    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"错误: 源文件夹 '{source_folder}' 不存在")
        return False

    # 收集所有文件（包括子文件夹中的文件）
    all_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    # 如果指定了扩展名，过滤文件
    if extension:
        if not extension.startswith('.'):
            extension = '.' + extension
        all_files = [f for f in all_files if f.lower().endswith(extension.lower())]

    if not all_files:
        print("没有找到符合条件的文件")
        return False

    print(f"找到 {len(all_files)} 个文件准备处理")
    print(f"重命名模式: {'开启' if rename_files else '关闭'}")
    print("-" * 50)

    # 处理计数器
    processed_count = 0
    current_num = start_num

    # 处理每个文件
    for file_path in all_files:
        try:
            # 获取文件扩展名
            file_ext = os.path.splitext(file_path)[1]

            if rename_files:
                # 重命名模式：编号在前，前缀在后，保留原扩展名
                new_filename = f"{current_num:04d}_{prefix}{file_ext}"
                new_file_path = os.path.join(target_folder, new_filename)

                # 检查文件名冲突
                counter = 1
                original_new_file_path = new_file_path
                while os.path.exists(new_file_path):
                    # 冲突时在文件名末尾添加序号
                    name_without_ext = os.path.splitext(new_filename)[0]
                    new_filename = f"{name_without_ext}_{counter}{file_ext}"
                    new_file_path = os.path.join(target_folder, new_filename)
                    counter += 1

                action_desc = f"重命名并移动: '{os.path.basename(file_path)}' -> '{new_filename}'"

            else:
                # 不重命名模式：保持原文件名
                original_filename = os.path.basename(file_path)
                new_file_path = os.path.join(target_folder, original_filename)

                # 检查文件名冲突
                counter = 1
                name, ext = os.path.splitext(original_filename)
                while os.path.exists(new_file_path):
                    new_filename = f"{name}_{counter}{ext}"
                    new_file_path = os.path.join(target_folder, new_filename)
                    counter += 1

                if counter > 1:
                    action_desc = f"移动并避免冲突: '{original_filename}' -> '{os.path.basename(new_file_path)}'"
                else:
                    action_desc = f"移动: '{original_filename}'"

            # 移动文件
            shutil.move(file_path, new_file_path)
            print(action_desc)

            processed_count += 1
            if rename_files:
                current_num += 1

        except Exception as e:
            print(f"错误: 处理文件 '{file_path}' 时出错: {str(e)}")

    # 删除空文件夹
    print("\n正在清理空文件夹...")
    remove_empty_folders(source_folder)

    print(f"\n完成: 成功处理 {processed_count} 个文件")
    return True


def remove_empty_folders(folder_path):
    """递归删除空文件夹"""
    deleted_count = 0
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # 尝试删除空文件夹
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    deleted_count += 1
            except (OSError, PermissionError):
                # 如果文件夹不为空或有权限问题，跳过
                pass

    if deleted_count > 0:
        print(f"已删除 {deleted_count} 个空文件夹")


def main():
    # 直接在这里定义参数
    source_folder = r"E:\02_ACG\映画\4K原版"  # 源文件夹路径
    target_folder = r"E:\02_ACG\映画\4K原版"  # 目标文件夹路径
    prefix = "铃原爱蜜莉"  # 文件名的前缀（重命名时使用）
    start_num = 1  # 起始编号（重命名时使用）
    extension = None  # 指定扩展名，None表示所有文件
    rename_files = False  # 是否重命名文件

    print("开始批量整理文件...")
    print(f"源文件夹: {source_folder}")
    print(f"目标文件夹: {target_folder}")
    print(f"重命名模式: {'开启' if rename_files else '关闭'}")

    if rename_files:
        print(f"编号起始: {start_num}")
        print(f"文件前缀: {prefix}")

    print(f"文件类型: {'所有文件' if extension is None else extension}")
    print("-" * 50)

    # 调用批量整理函数
    success = batch_organize_files(
        source_folder=source_folder,
        target_folder=target_folder,
        prefix=prefix,
        start_num=start_num,
        extension=extension,
        rename_files=rename_files
    )

    if success:
        print("\n文件整理操作完成！")
        print(f"所有文件已移动到: {target_folder}")
    else:
        print("\n文件整理操作失败！")


if __name__ == "__main__":
    main()
