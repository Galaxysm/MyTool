import pyautogui
import cv2
import numpy as np
import os
import glob
from PIL import Image
import time
import datetime


class ScreenClicker:
    def __init__(self):
        # 设置pyautogui的暂停时间和故障安全
        pyautogui.PAUSE = 1
        pyautogui.FAILSAFE = True

    def get_monitors_info(self):
        """
        获取所有显示器信息
        """
        try:
            import mss
            with mss.mss() as sct:
                monitors = sct.monitors
                print(f"找到 {len(monitors) - 1} 个显示器:")
                for i, monitor in enumerate(monitors[1:], 1):
                    print(f"  显示器 {i}: 位置({monitor['left']}, {monitor['top']}), "
                          f"尺寸{monitor['width']}x{monitor['height']}")
                return monitors
        except ImportError:
            print("mss模块未安装，使用单显示器模式")
            # 获取屏幕尺寸
            screen_size = pyautogui.size()
            print(f"主显示器: 尺寸{screen_size.width}x{screen_size.height}")
            return None

    def capture_screen(self, monitor=1, mark_position=None):
        """
        截取指定显示器的屏幕，并自动保存截图
        如果提供了mark_position，会在截图上标记点击位置
        """
        try:
            import mss
            with mss.mss() as sct:
                monitors = sct.monitors
                if monitor >= len(monitors):
                    print(f"显示器 {monitor} 不存在，使用主显示器")
                    monitor = 1

                # 获取选定显示器的信息
                selected_monitor = monitors[monitor]
                print(f"选择显示器 {monitor}: 位置({selected_monitor['left']}, {selected_monitor['top']}), "
                      f"尺寸{selected_monitor['width']}x{selected_monitor['height']}")

                # 截取指定显示器的屏幕
                screenshot = sct.grab(selected_monitor)
                # 转换为PIL图像
                img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')

                # 转换为OpenCV格式用于标记
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                # 如果提供了点击位置，在截图上标记
                if mark_position is not None:
                    x, y = mark_position
                    # 画一个红色的圆圈标记点击位置
                    cv2.circle(img_cv, (x, y), 20, (0, 0, 255), 3)  # 红色圆圈，半径20，线宽3
                    cv2.circle(img_cv, (x, y), 5, (0, 0, 255), -1)  # 红色实心圆心
                    # 添加文字说明
                    cv2.putText(img_cv, f"Click: ({x}, {y})", (x + 25, y - 25),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 保存截图到当前目录
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                if mark_position is not None:
                    screenshot_filename = f"screenshot_monitor{monitor}_{timestamp}_marked.png"
                else:
                    screenshot_filename = f"screenshot_monitor{monitor}_{timestamp}.png"

                # 将标记后的OpenCV图像转换回PIL图像保存
                img_marked = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
                img_marked.save(screenshot_filename)
                print(f"屏幕截图已保存: {screenshot_filename}")

                return img_cv, selected_monitor
        except ImportError:
            print("mss模块未安装，使用pyautogui进行截屏")
            # 备用方案：使用pyautogui截屏
            screenshot = pyautogui.screenshot()

            # 转换为OpenCV格式
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 如果提供了点击位置，在截图上标记
            if mark_position is not None:
                x, y = mark_position
                # 画一个红色的圆圈标记点击位置
                cv2.circle(img_cv, (x, y), 20, (0, 0, 255), 3)  # 红色圆圈，半径20，线宽3
                cv2.circle(img_cv, (x, y), 5, (0, 0, 255), -1)  # 红色实心圆心
                # 添加文字说明
                cv2.putText(img_cv, f"Click: ({x}, {y})", (x + 25, y - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 保存截图到当前目录
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if mark_position is not None:
                screenshot_filename = f"screenshot_{timestamp}_marked.png"
            else:
                screenshot_filename = f"screenshot_{timestamp}.png"

            # 将标记后的OpenCV图像转换回PIL图像保存
            img_marked = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
            img_marked.save(screenshot_filename)
            print(f"屏幕截图已保存: {screenshot_filename}")

            # 单显示器时，monitor信息为整个屏幕
            screen_size = pyautogui.size()
            monitor_info = {'left': 0, 'top': 0, 'width': screen_size.width, 'height': screen_size.height}
            return img_cv, monitor_info

    def find_template_location(self, screen_img, template_path, threshold=0.8):
        """
        在屏幕截图中查找模板图片的位置
        """
        # 读取模板图片
        template = cv2.imread(template_path)
        if template is None:
            print(f"无法读取模板图片: {template_path}")
            return None

        # 使用模板匹配
        result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"模板 {os.path.basename(template_path)} 匹配度: {max_val:.3f}")

        # 如果匹配度高于阈值，返回中心位置
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y), max_val
        else:
            print(f"未找到模板 {os.path.basename(template_path)}，匹配度 {max_val:.3f} 低于阈值 {threshold}")
            return None, max_val

    def get_image_files(self, pattern="*.png"):
        """
        获取当前目录下所有的图片文件，按文件名排序
        """
        # 获取所有匹配的图片文件
        image_files = glob.glob("Img/" + pattern)
        # 按文件名排序
        image_files.sort()
        return image_files

    def click_at_position(self, screen_position, monitor_info, click_delay=1.0):
        """
        在指定位置点击鼠标左键
        将屏幕截图内的坐标转换为全局桌面坐标
        """
        # 屏幕截图内的相对坐标
        screen_x, screen_y = screen_position

        # 转换为全局桌面坐标
        global_x = monitor_info['left'] + screen_x
        global_y = monitor_info['top'] + screen_y

        print(f"屏幕坐标: ({screen_x}, {screen_y})")
        print(f"全局坐标: ({global_x}, {global_y})")
        print(f"移动到位置: ({global_x}, {global_y})")

        # 移动到全局坐标并点击
        pyautogui.moveTo(global_x, global_y, duration=0.5)
        time.sleep(0.2)  # 短暂停顿
        pyautogui.click()
        print("点击完成")
        time.sleep(click_delay)  # 点击后的延迟

    def run_auto_click(self, monitor=1, threshold=0.8, click_delay=1.0):
        """
        主函数：每次点击前重新截屏、匹配图片并点击
        """
        print("开始自动点击程序...")

        # 显示显示器信息
        self.get_monitors_info()

        # 获取所有图片文件
        image_files = self.get_image_files("*.png")
        if not image_files:
            print("未找到任何PNG图片文件！")
            return

        print(f"找到 {len(image_files)} 个图片文件:")
        for img_file in image_files:
            print(f"  - {img_file}")

        # 对每个图片进行单独处理：截屏 -> 匹配 -> 点击
        successful_clicks = 0
        for i, img_file in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] 处理图片: {img_file}")

            # 每次点击前都重新截取屏幕
            print("截取屏幕...")
            screen_img, monitor_info = self.capture_screen(monitor)
            print("屏幕截取完成")

            position, confidence = self.find_template_location(screen_img, img_file, threshold)

            if position:
                print(f"找到目标位置，置信度: {confidence:.3f}")

                # 点击前再次截屏并标记点击位置
                print("截取带标记的屏幕...")
                self.capture_screen(monitor, mark_position=position)

                self.click_at_position(position, monitor_info, click_delay)
                successful_clicks += 1
                time.sleep(2)  # 点击后等待界面更新
            else:
                print(f"未找到图片 {img_file} 的匹配位置")

        print(f"\n自动点击程序完成！成功点击 {successful_clicks}/{len(image_files)} 个位置")


def main():
    # 创建点击器实例
    clicker = ScreenClicker()

    # 配置参数 - 在这里修改你需要的参数
    monitor = 1  # 显示器编号（1=主显示器，2=第二个显示器，以此类推）
    threshold = 0.8  # 匹配阈值（0-1之间，越高越严格）
    click_delay = 0.0  # 每次点击后的延迟（秒）

    print("多屏幕自动点击程序（每次点击前重新截屏并标记位置）")
    print("=" * 50)

    try:
        # 运行自动点击程序
        clicker.run_auto_click(monitor, threshold, click_delay)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()
