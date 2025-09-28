import os
import time
import psutil
import pandas as pd
import pyperclip

import ImageMatcher.image_matcher as imgmatch
from NetworkMonitor.network_monitor import get_download_monitor, start_monitoring_thread


# 添加网速监控类
class DownloadMonitor:
    def __init__(self, check_interval=2, high_speed_threshold=10):
        """
        初始化下载监控器
        参数:
            check_interval: 检查间隔(秒)
            high_speed_threshold: 高速下载阈值(MB/s)
        """
        self.check_interval = check_interval
        self.high_speed_threshold = high_speed_threshold
        self.current_speed = 0.0

    def get_network_usage(self):
        """获取当前网络使用情况(MB/s)"""
        try:
            # 获取所有网络接口的统计信息
            net_io = psutil.net_io_counters()
            bytes_recv = net_io.bytes_recv

            # 等待一段时间后再次测量
            time.sleep(1)

            net_io = psutil.net_io_counters()
            bytes_recv_new = net_io.bytes_recv

            # 计算下载速度 (MB/s)
            download_speed = (bytes_recv_new - bytes_recv) / (1024 * 1024)
            self.current_speed = download_speed
            return download_speed
        except:
            return 0.0

    def get_current_speed(self):
        """获取当前下载速度(MB/s)"""
        return self.current_speed

    def is_download_active(self, threshold=None):
        """
        检查当前是否有活跃下载
        参数:
            threshold: 速度阈值(MB/s)，默认为初始化时设置的高速阈值
        返回:
            bool: 是否有活跃下载
        """
        threshold = threshold or self.high_speed_threshold
        self.get_network_usage()  # 更新当前速度
        return self.current_speed > threshold


# 创建全局下载监控器实例
download_monitor = DownloadMonitor(high_speed_threshold=5)  # 5MB/s视为活跃下载


def check_download_activity():
    """检查下载活动状态"""
    print("正在检查网络下载状态...")
    speed = download_monitor.get_current_speed()
    print(f"当前下载速度: {speed:.2f} MB/s")

    if download_monitor.is_download_active():
        print("检测到活跃下载，等待下载完成...")
        return True
    else:
        print("未检测到活跃下载，可以继续添加任务")
        return False


def wait_for_download_completion(timeout=300):
    """等待下载完成或超时"""
    print("等待下载完成...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        speed = download_monitor.get_current_speed()
        print(f"\r当前下载速度: {speed:.2f} MB/s", end="", flush=True)

        if not download_monitor.is_download_active(threshold=2):  # 2MB/s以下认为下载完成
            print("\n下载已完成或暂停")
            return True

        time.sleep(5)  # 每5秒检查一次

    print("\n等待超时，继续执行后续操作")
    return False


def read_magnet_links_from_excel(file_path, sheet_name):
    """
    从Excel文件中读取磁力链接
    """
    try:
        # 读取Excel文件中的【单选】sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)

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
        # subprocess.Popen(['C:\\Users\\Galaxy\\AppData\\Local\\Programs\\Quark\\quark.exe','--new-window', 'https://pan.quark.cn/'])
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
        imgmatch.main()

        print(f"已添加磁力链接: {magnet_link[:50]}...")
        return True
    except Exception as e:
        print(f"添加磁力链接时出错: {e}")
        return False


def main():
    # 配置参数
    sheet_name = '下载页'      # 自定义磁力链接 下载页

    excel_file_path = 'Resource/BT.xlsx'
    if not os.path.exists(excel_file_path):
        print("文件不存在，请检查路径是否正确")
        return

    # 读取磁力链接
    magnet_links = read_magnet_links_from_excel(excel_file_path, sheet_name)

    if not magnet_links:
        print("未找到有效的磁力链接")
        return

    print(f"找到 {len(magnet_links)} 个磁力链接")

    # 打开夸克浏览器
    if not open_quark_browser():
        # 如果自动打开失败，提示用户手动打开
        input("请手动打开夸克浏览器并导航到网盘页面，然后按回车继续...")

    # 添加每个磁力链接到夸克网盘
    batch_size = 5  # 每批处理5个链接
    for i in range(0, len(magnet_links), batch_size):
        batch_links = magnet_links[i:i + batch_size]
        batch_number = i // batch_size + 1
        total_batches = (len(magnet_links) + batch_size - 1) // batch_size

        print(f"\n处理第 {batch_number}/{total_batches} 批链接 ({len(batch_links)} 个链接)")

        # 处理当前批次的链接
        for j, magnet_link in enumerate(batch_links, 1):
            link_number = i + j
            print(f"正在处理第 {link_number}/{len(magnet_links)} 个链接...")
            if add_magnet_to_quark(magnet_link):
                print("添加成功")
            else:
                print("添加失败")
            time.sleep(3)  # 等待一段时间再处理下一个

        # 如果不是最后一批，检查下载状态
        if i + batch_size < len(magnet_links):
            print(f"\n已完成第 {batch_number} 批链接添加，等待10秒后检查下载状态...")
            time.sleep(10)

            # 检查是否有活跃下载
            if check_download_activity():
                # 如果有活跃下载，等待下载完成或超时
                wait_for_download_completion()
            else:
                print("无活跃下载，继续处理下一批链接")

        print("-" * 50)

    print("所有磁力链接已处理完毕")


if __name__ == "__main__":
    main()
