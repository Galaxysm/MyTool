import psutil
import time
import threading
import os
import sys
from datetime import datetime


class DownloadMonitor:
    def __init__(self, check_interval=2, high_speed_threshold=50, low_speed_threshold=5,
                 duration_threshold=10, notification_callback=None):
        """
        初始化下载监控器

        参数:
            check_interval: 检查间隔(秒)
            high_speed_threshold: 高速下载阈值(MB/s)
            low_speed_threshold: 低速阈值(MB/s)，低于此值认为下载可能已完成
            duration_threshold: 持续时间阈值(秒)，低速持续这么久才认为下载完成
            notification_callback: 通知回调函数
        """
        self.check_interval = check_interval
        self.high_speed_threshold = high_speed_threshold
        self.low_speed_threshold = low_speed_threshold
        self.duration_threshold = duration_threshold
        self.notification_callback = notification_callback or self.default_notification
        self.is_monitoring = False
        self.high_speed_detected = False
        self.low_speed_start_time = None
        self.current_speed = 0.0
        self.speed_history = []
        self.max_history_size = 60  # 保存最近60秒的速度历史

    def get_network_usage(self):
        """获取当前网络使用情况(MB/s)"""
        # 获取所有网络接口的统计信息
        net_io = psutil.net_io_counters()
        bytes_recv = net_io.bytes_recv

        # 等待一段时间后再次测量
        time.sleep(1)

        net_io = psutil.net_io_counters()
        bytes_recv_new = net_io.bytes_recv

        # 计算下载速度 (MB/s)
        download_speed = (bytes_recv_new - bytes_recv) / (1024 * 1024)

        return download_speed

    def get_current_speed(self):
        """
        获取当前下载速度

        返回:
            float: 当前下载速度(MB/s)
        """
        return self.current_speed

    def get_speed_statistics(self, seconds=10):
        """
        获取指定时间范围内的速度统计信息

        参数:
            seconds: 统计时间范围(秒)

        返回:
            dict: 包含平均速度、最大速度、最小速度的字典
        """
        if not self.speed_history:
            return {"avg": 0, "max": 0, "min": 0}

        # 获取最近指定秒数的速度数据
        recent_speeds = self.speed_history[-min(seconds, len(self.speed_history)):]

        return {
            "avg": sum(recent_speeds) / len(recent_speeds),
            "max": max(recent_speeds),
            "min": min(recent_speeds)
        }

    def is_download_active(self, threshold=None):
        """
        检查当前是否有活跃下载

        参数:
            threshold: 速度阈值(MB/s)，默认为初始化时设置的高速阈值

        返回:
            bool: 是否有活跃下载
        """
        threshold = threshold or self.high_speed_threshold
        return self.current_speed > threshold

    def default_notification(self, message):
        """默认通知方式"""
        print(f"\n{'=' * 50}")
        print(f"通知: {message}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}\n")

        # 尝试发送系统通知
        try:
            if sys.platform == "darwin":  # macOS
                os.system(f"osascript -e 'display notification \"{message}\" with title \"下载完成\"'")
            elif sys.platform == "linux":  # Linux
                os.system(f'notify-send "下载完成" "{message}"')
            elif sys.platform == "win32":  # Windows
                # 需要安装win10toast库: pip install win10toast
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast("下载完成", message, duration=5)
                except ImportError:
                    print("安装win10toast可以获得更好的通知体验: pip install win10toast")
        except:
            pass  # 忽略通知错误

    def start_monitoring(self):
        """开始监控下载状态"""
        self.is_monitoring = True
        print("开始监控下载状态...")
        print(f"高速阈值: {self.high_speed_threshold} MB/s")
        print(f"低速阈值: {self.low_speed_threshold} MB/s")
        print(f"按 Ctrl+C 停止监控\n")

        try:
            while self.is_monitoring:
                speed = self.get_network_usage()
                self.current_speed = speed
                current_time = time.time()

                # 更新速度历史
                self.speed_history.append(speed)
                if len(self.speed_history) > self.max_history_size:
                    self.speed_history.pop(0)

                # 显示当前速度
                print(f"\r当前下载速度: {speed:.2f} MB/s", end="", flush=True)

                # 检测高速下载
                if speed > self.high_speed_threshold:
                    if not self.high_speed_detected:
                        print(f"\n检测到高速下载开始: {speed:.2f} MB/s")
                        self.high_speed_detected = True

                # 检测下载完成（从高速状态恢复到低速状态）
                if self.high_speed_detected and speed < self.low_speed_threshold:
                    if self.low_speed_start_time is None:
                        self.low_speed_start_time = current_time
                        print(f"\n检测到下载速度下降，开始计时...")
                    else:
                        # 检查低速状态持续时间是否超过阈值
                        if current_time - self.low_speed_start_time >= self.duration_threshold:
                            self.notification_callback("下载可能已完成！网络速度已恢复正常水平。")
                            self.high_speed_detected = False
                            self.low_speed_start_time = None
                else:
                    self.low_speed_start_time = None

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n\n用户中断监控")
        except Exception as e:
            print(f"\n监控出错: {e}")
        finally:
            self.stop_monitoring()

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        print("\n停止下载监控")


# 单例模式，方便全局访问
_monitor_instance = None


def get_download_monitor():
    """获取下载监控器实例（单例模式）"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = DownloadMonitor()
    return _monitor_instance


def start_monitoring_thread():
    """在后台线程中启动监控"""
    monitor = get_download_monitor()
    if not monitor.is_monitoring:
        thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
        thread.start()
        return thread
    return None


def main():
    # 创建监控器实例
    monitor = DownloadMonitor(
        check_interval=2,  # 每2秒检查一次
        high_speed_threshold=50,  # 50MB/s以上视为高速下载
        low_speed_threshold=5,  # 5MB/s以下视为低速
        duration_threshold=10  # 低速持续10秒认为下载完成
    )

    # 开始监控
    monitor.start_monitoring()


if __name__ == "__main__":
    # 检查是否安装了psutil
    try:
        import psutil
    except ImportError:
        print("请先安装psutil库: pip install psutil")
        exit(1)

    main()