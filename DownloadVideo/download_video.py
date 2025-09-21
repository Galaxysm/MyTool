import os
import pandas as pd
import time
import subprocess
from urllib.parse import urlparse
import pyautogui
import pyperclip
import ImageMatcher.image_matcher as imgmatch

def read_magnet_links_from_excel(file_path):
    """
    从Excel文件中读取磁力链接
    """
    try:
        # 读取Excel文件中的【单选】sheet
        df = pd.read_excel(file_path, sheet_name='单选')

        # 获取B列的所有值
        magnet_links = df.iloc[:, 1].dropna().tolist()  # B列是第1列（0-based）

        # 过滤出磁力链接
        magnet_links = [link for link in magnet_links if link.startswith('magnet:?')]

        return magnet_links
    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        return []


def open_quark_browser():
    """
    打开夸克浏览器并导航到夸克网盘页面
    """
    try:
        # 尝试打开夸克浏览器
        #subprocess.Popen(['C:\\Users\\Galaxy\\AppData\\Local\\Programs\\Quark\\quark.exe','--new-window', 'https://pan.quark.cn/'])
        print("正在打开夸克浏览器...")
        time.sleep(5)  # 等待浏览器加载
    except Exception as e:
        print(f"打开夸克浏览器时出错: {e}")
        print("请确保夸克浏览器已安装，或手动打开夸克网盘页面")
        return False
    return True


def add_magnet_to_quark(magnet_link):
    """
    通过自动化操作将磁力链接添加到夸克网盘
    """
    try:
        # 复制磁力链接到剪贴板
        pyperclip.copy(magnet_link)
        time.sleep(5)

        # 调用imgmatch.main()并等待其完成
        success = imgmatch.main()

        if not success:
            print("图像匹配操作失败")
            return False



        print(f"已添加磁力链接: {magnet_link[:50]}...")
        return True
    except Exception as e:
        print(f"添加磁力链接时出错: {e}")
        return False


def main():
    # 指定Excel文件路径
    #excel_file_path = input("请输入Excel文件路径: ").strip().strip('"')
    excel_file_path = 'Resource/BT.xlsx'

    if not os.path.exists(excel_file_path):
        print("文件不存在，请检查路径是否正确")
        return

    # 读取磁力链接
    magnet_links = read_magnet_links_from_excel(excel_file_path)

    if not magnet_links:
        print("未找到有效的磁力链接")
        return

    print(f"找到 {len(magnet_links)} 个磁力链接")

    # 打开夸克浏览器
    if not open_quark_browser():
        # 如果自动打开失败，提示用户手动打开
        input("请手动打开夸克浏览器并导航到网盘页面，然后按回车继续...")

    # 添加每个磁力链接到夸克网盘
    for i, magnet_link in enumerate(magnet_links, 1):
        print(f"正在处理第 {i}/{len(magnet_links)} 个链接...")
        if add_magnet_to_quark(magnet_link):
            print("添加成功")
        else:
            print("添加失败")
        time.sleep(5)  # 等待一段时间再处理下一个


if __name__ == "__main__":
    # 安装所需库
    # pip install pandas openpyxl pyautogui pyperclip

    main()