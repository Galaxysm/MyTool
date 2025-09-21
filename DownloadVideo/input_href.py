from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import time
import os


class MagnetLinkExtractor:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # 可选：无头模式（取消注释以在后台运行）
        # chrome_options.add_argument('--headless')

        # 设置下载行为（避免弹窗）
        prefs = {
            "download.default_directory": os.getcwd(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service('Resource/chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            print("浏览器驱动初始化成功")
        except Exception as e:
            print(f"浏览器驱动初始化失败: {e}")
            raise

    def click_entry_if_exists(self):
        """检查并点击'请点此进入'等入口链接"""
        entry_phrases = ["请点此进入", "点击进入", "点此进入", "进入", "进入网站", "继续访问", "访问", "进入主页"]

        for phrase in entry_phrases:
            try:
                # 尝试多种定位方式
                selectors = [
                    f"//a[contains(text(), '{phrase}')]",
                    f"//button[contains(text(), '{phrase}')]",
                    f"//div[contains(text(), '{phrase}')]",
                    f"//span[contains(text(), '{phrase}')]",
                    f"//*[contains(@onclick, '{phrase}')]"
                ]

                for selector in selectors:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if element:
                            print(f"找到'{phrase}'入口，正在点击...")
                            element.click()
                            time.sleep(2)  # 等待页面跳转
                            return True
                    except:
                        continue
            except Exception as e:
                continue

        print("未找到需要点击的入口链接")
        return False

    def find_thread_elements(self):
        """在ID为threadlist的div里面寻找class='s xst'的href链接"""
        try:
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # 查找threadlist div
            threadlist_div = self.driver.find_element(By.ID, "threadlist")
            print("找到threadlist div")

            # 在threadlist div内部查找所有class包含's xst'的链接
            links = threadlist_div.find_elements(By.XPATH, ".//a[contains(@class, 's') and contains(@class, 'xst')]")
            print(f"找到 {len(links)} 个class='s xst'的链接")

            # 提取href属性
            href_list = []
            for link in links:
                href = link.get_attribute('href')
                if href:
                    href_list.append(href)
                    print(f"找到链接: {href}")

            return href_list

        except NoSuchElementException:
            print("未找到指定的元素")
            return []
        except Exception as e:
            print(f"查找元素时出错: {e}")
            return []


    def process_all_links(self, main_url):
        """处理所有链接并提取超链接"""
        all_href_links = []

        try:
            # 访问主页面
            print(f"正在访问主页面: {main_url}")
            self.driver.get(main_url)

            # 检查并点击入口链接
            self.click_entry_if_exists()

            # 等待页面加载
            time.sleep(3)

            # 查找目标元素
            elements = self.find_thread_elements()
            if not elements:
                print("未找到超链接")
                return []

            # 提取所有链接
            print(f"共找到 {len(elements)} 个链接需要处理")

        except Exception as e:
            print(f"处理过程中出错: {e}")

        return elements

    def save_to_excel(self, href_links, excel_file, sheet_name):
        """将超链接保存到Excel"""
        try:
            # 创建DataFrame，超链接放在B列
            df = pd.DataFrame({
                'A': [''] * len(href_links),  # 空A列
                'B': href_links  # B列包含超链接
            })

            # 保存到Excel
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

            print(f"成功保存 {len(href_links)} 个超链接到 {excel_file} 的 {sheet_name} 工作表B列")

        except Exception as e:
            print(f"保存到Excel时出错: {e}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


def main():
    # 配置参数
    target_url = "https://309r.0i284.net/forum.php?mod=forumdisplay&fid=36&typeid=654&typeid=654&filter=typeid&page=1"  # 替换为实际网址
    output_excel = "Resource/BT.xlsx"  # Excel文件路径
    sheet_name = "Auto超链接"  # 工作表名称

    # 创建提取器实例
    extractor = MagnetLinkExtractor()

    try:
        # 提取超链接
        print("开始提取超链接...")
        href_links = extractor.process_all_links(target_url)

        if href_links:
            print(f"共找到 {len(href_links)} 个超链接")
            # 保存到Excel
            extractor.save_to_excel(href_links, output_excel, sheet_name)
        else:
            print("未找到任何超链接")

    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        extractor.close()


if __name__ == "__main__":
    main()

