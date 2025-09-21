import pyautogui
import cv2
import numpy as np
import os
import time

# ==================== 配置参数 ====================
# 模板图像路径（自动搜索多个可能位置）
TEMPLATE_FILENAME = "template.png"
POSSIBLE_TEMPLATE_PATHS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resource", TEMPLATE_FILENAME),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), TEMPLATE_FILENAME),
    TEMPLATE_FILENAME,
    os.path.join("Resource", TEMPLATE_FILENAME)
]

# 图像匹配参数
MATCH_THRESHOLD = 0.8  # 匹配阈值 (0-1)
MATCH_METHOD = cv2.TM_CCOEFF_NORMED  # 匹配方法

# 鼠标操作参数
MOVE_DURATION = 0.5  # 鼠标移动持续时间(秒)
CLICK_AFTER_MOVE = True  # 移动后是否点击
CLICK_TYPE = "left"  # 点击类型: "left", "right", "middle"
CLICK_COUNT = 1  # 点击次数

# 结果保存参数
SAVE_RESULT_IMAGE = True  # 是否保存标记结果的图像
RESULT_IMAGE_FILENAME = "/Resource/match_result.png"  # 结果图像文件名
SHOW_RESULT_PREVIEW = True  # 是否显示结果预览
PREVIEW_DURATION = 2000  # 预览显示时间(毫秒)

# 安全设置
ENABLE_FAILSAFE = True  # 启用紧急停止功能
PAUSE_BETWEEN_ACTIONS = 0.5  # 操作间暂停时间(秒)


# ==================== 功能函数 ====================
def setup_pyautogui():
    """配置PyAutoGUI安全设置"""
    pyautogui.FAILSAFE = ENABLE_FAILSAFE
    pyautogui.PAUSE = PAUSE_BETWEEN_ACTIONS


def find_template_path():
    """查找模板图像文件路径"""
    for path in POSSIBLE_TEMPLATE_PATHS:
        if os.path.exists(path):
            return path
    return None


def fullscreen_screenshot():
    """获取全屏截图"""
    print("正在截取全屏...")
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def find_image_position(screenshot, template_path):
    """
    在截图中查找模板图像的位置
    返回: (x, y, confidence) 或 None
    """
    # 读取模板图像
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法读取模板图像: {template_path}")

    # 获取模板图像尺寸
    h, w = template.shape[:-1]

    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, MATCH_METHOD)

    # 找到最佳匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 如果匹配度高于阈值，返回位置
    if max_val >= MATCH_THRESHOLD:
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y, max_val)
    else:
        return None


def find_all_matches(screenshot, template_path):
    """
    查找所有匹配的模板图像位置
    返回: [(x, y, confidence), ...]
    """
    # 读取模板图像
    template = cv2.imread(template_path)
    if template is None:
        raise ValueError(f"无法读取模板图像: {template_path}")

    # 获取模板图像尺寸
    h, w = template.shape[:-1]

    # 使用模板匹配
    result = cv2.matchTemplate(screenshot, template, MATCH_METHOD)

    # 找到所有匹配位置
    locations = np.where(result >= MATCH_THRESHOLD)
    matches = []

    for pt in zip(*locations[::-1]):
        confidence = result[pt[1], pt[0]]
        center_x = pt[0] + w // 2
        center_y = pt[1] + h // 2
        matches.append((center_x, center_y, confidence))

    # 去除重复的匹配
    return filter_duplicate_matches(matches, w, h)


def filter_duplicate_matches(matches, template_width, template_height):
    """去除重复的匹配项"""
    filtered_matches = []
    for match in matches:
        x, y, confidence = match
        # 检查是否与已有匹配太接近
        too_close = False
        for existing in filtered_matches:
            ex, ey, _ = existing
            if (abs(x - ex) < template_width // 2 and
                    abs(y - ey) < template_height // 2):
                # 保留置信度更高的匹配
                if confidence > existing[2]:
                    filtered_matches.remove(existing)
                    filtered_matches.append(match)
                too_close = True
                break
        if not too_close:
            filtered_matches.append(match)

    return filtered_matches


def move_and_click(x, y):
    """将鼠标移动到指定坐标并点击"""
    print(f"移动鼠标到坐标: ({x}, {y})")

    # 获取当前鼠标位置
    current_x, current_y = pyautogui.position()
    print(f"当前鼠标位置: ({current_x}, {current_y})")

    # 移动鼠标到目标位置
    pyautogui.moveTo(x, y, duration=MOVE_DURATION)

    if CLICK_AFTER_MOVE:
        print(f"执行{CLICK_TYPE}键点击 {CLICK_COUNT} 次")
        if CLICK_TYPE == "left":
            pyautogui.click(clicks=CLICK_COUNT)
        elif CLICK_TYPE == "right":
            pyautogui.rightClick(clicks=CLICK_COUNT)
        elif CLICK_TYPE == "middle":
            pyautogui.middleClick(clicks=CLICK_COUNT)

    # 短暂暂停
    time.sleep(0.5)


def mark_and_save_result(screenshot, matches, result_filename):
    """在截图上标记匹配位置并保存"""
    marked_screenshot = screenshot.copy()

    if len(matches) == 1:
        # 单个匹配
        x, y, confidence = matches[0]
        cv2.circle(marked_screenshot, (x, y), 10, (0, 0, 255), -1)
        cv2.putText(marked_screenshot, f"({x}, {y}) conf:{confidence:.2f}",
                    (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    else:
        # 多个匹配
        for i, (x, y, confidence) in enumerate(matches):
            color = (0, 255, 0) if i == 0 else (0, 0, 255)  # 第一个绿色，其他红色
            cv2.circle(marked_screenshot, (x, y), 10, color, -1)
            cv2.putText(marked_screenshot, f"{i + 1}:({x},{y})",
                        (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 保存结果图像
    cv2.imwrite(result_filename, marked_screenshot)
    print(f"已保存标记结果的截图: {result_filename}")

    # 显示预览
    if SHOW_RESULT_PREVIEW:
        cv2.imshow("匹配结果", marked_screenshot)
        cv2.waitKey(PREVIEW_DURATION)
        cv2.destroyAllWindows()

    return marked_screenshot


# ==================== 主函数 ====================
def main():
    """主函数 - 查找第一个匹配项并点击"""
    try:
        setup_pyautogui()

        # 查找模板图像
        template_path = find_template_path()
        if template_path is None:
            print("错误: 未找到模板图像文件")
            print("请将template.png放置在以下位置之一:")
            for path in POSSIBLE_TEMPLATE_PATHS:
                print(f"  - {path}")
            return

        print(f"使用模板图像: {template_path}")

        # 获取全屏截图
        screenshot = fullscreen_screenshot()

        # 查找模板位置
        print("正在查找图像...")
        position = find_image_position(screenshot, template_path)

        if position:
            x, y, confidence = position
            print(f"找到匹配图像! 坐标: ({x}, {y}), 置信度: {confidence:.2f}")

            # 标记并保存结果
            if SAVE_RESULT_IMAGE:
                mark_and_save_result(screenshot, [position], RESULT_IMAGE_FILENAME)

            # 移动并点击
            move_and_click(x, y)
            print("操作完成!")
        else:
            print(f"未找到匹配图像 (阈值: {MATCH_THRESHOLD})")

    except Exception as e:
        print(f"发生错误: {e}")


def advanced_main():
    """高级模式 - 查找所有匹配项并点击第一个"""
    try:
        setup_pyautogui()

        # 查找模板图像
        template_path = find_template_path()
        if template_path is None:
            print("错误: 未找到模板图像文件")
            print("请将template.png放置在以下位置之一:")
            for path in POSSIBLE_TEMPLATE_PATHS:
                print(f"  - {path}")
            return

        print(f"使用模板图像: {template_path}")

        # 获取全屏截图
        screenshot = fullscreen_screenshot()

        # 查找所有匹配位置
        print("正在查找图像...")
        matches = find_all_matches(screenshot, template_path)

        if matches:
            print(f"找到 {len(matches)} 个匹配:")
            for i, (x, y, confidence) in enumerate(matches):
                print(f"{i + 1}. 坐标: ({x}, {y}), 置信度: {confidence:.2f}")

            # 标记并保存结果
            if SAVE_RESULT_IMAGE:
                mark_and_save_result(screenshot, matches, RESULT_IMAGE_FILENAME)

            # 选择第一个匹配进行点击
            x, y, confidence = matches[0]
            print(f"选择第一个匹配进行点击: ({x}, {y})")

            # 移动并点击
            move_and_click(x, y)
            print("操作完成!")
        else:
            print(f"未找到匹配图像 (阈值: {MATCH_THRESHOLD})")

    except Exception as e:
        print(f"发生错误: {e}")


def capture_template():
    """自动捕获模板图像"""
    try:
        print("5秒后开始捕获模板图像...")
        time.sleep(5)

        # 获取鼠标位置
        x, y = pyautogui.position()
        print(f"鼠标当前位置: ({x}, {y})")

        # 设置捕获区域大小
        width, height = 100, 100

        # 计算捕获区域
        left = max(0, x - width // 2)
        top = max(0, y - height // 2)

        # 截取区域
        region = (left, top, width, height)
        screenshot = pyautogui.screenshot(region=region)

        # 转换为OpenCV格式
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 保存模板到第一个可能的位置
        template_path = POSSIBLE_TEMPLATE_PATHS[1]  # 使用第二个路径（脚本同目录）
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        cv2.imwrite(template_path, img)

        print(f"模板已保存到: {template_path}")
        print(f"捕获区域: {region}")

        # 显示预览
        cv2.imshow("捕获的模板", img)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"捕获模板时发生错误: {e}")


# ==================== 执行入口 ====================
if __name__ == "__main__":
    # 配置执行模式
    MODE = "main"  # 可选: "main", "advanced", "capture"

    if MODE == "capture":
        print("执行模板捕获模式")
        capture_template()
    elif MODE == "advanced":
        print("执行高级模式（多匹配）")
        advanced_main()
    else:
        print("执行基本模式（单匹配）")
        main()
