import cv2
import numpy as np
from PIL import ImageGrab
import sys
import time
import ctypes
import keyboard
import json
import os
from random import random

# 全局變量
TEMPLATE_IMG_PATH = 'play_button.jpg'
HOTKEY = 'ctrl+shift+x'  # 熱鍵組合
CONFIG_FILE = 'config.json'  # 配置文件名稱
SAMPLE_THRESHOLD = 0.6  # 模板取樣閾值
THRESHOLD = 0.7  # 迴圈閾值

# 載入或創建配置文件
def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    else:
        return {'bbox': None}

# 保存配置
def save_config(config):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

# 轉換圖像為灰階
def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 載入模板圖片並轉換為灰階
def load_template_image(path):
    image = cv2.imread(path)
    return convert_to_grayscale(image)

# 尋找匹配位置
def find_match_location(screen, template):
    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return max_val, max_loc

# 處理熱鍵觸發
def on_triggered():
    print("截圖並尋找匹配...")
    screen = np.array(ImageGrab.grab())
    screen_gray = convert_to_grayscale(screen)
    max_val, location = find_match_location(screen_gray, img_templ)

    if max_val >= SAMPLE_THRESHOLD:  # 可根據需求調整閾值
        print(f"找到匹配的圖片在位置：{location}")
        h, w = img_templ.shape[:2]
        bbox = [location[0], location[1], location[0] + w, location[1] + h]
        config['bbox'] = bbox
        save_config(config)
        print(f"配置已保存：{bbox}")
    else:
        print("沒有找到匹配的圖片。")

# 主循環
def mainLoop(bbox):
    while True:
        img_src = ImageGrab.grab(bbox=bbox)
        #模板匹配
        result = cv2.matchTemplate(img_src, img_templ, cv2.TM_CCOEFF_NORMED)
        min_max = cv2.minMaxLoc(result)  #计算匹配度
        print('result.min_max:', min_max)

        # 如果匹配度很高，则认为找到菱形，于是模拟鼠标单击
        if min_max[1] > THRESHOLD :
            print('处于对话状态，模拟鼠标单击')
            ctypes.windll.user32.mouse_event(2)
            time.sleep(0.05 + 0.1 * random())
            ctypes.windll.user32.mouse_event(4)

# 程序入口
if __name__ == '__main__':
    config = load_or_create_config()
    img_templ = load_template_image(TEMPLATE_IMG_PATH)

    while not config['bbox']:
        keyboard.add_hotkey(HOTKEY, on_triggered)
        print(f"等待按下 {HOTKEY} 進行螢幕截圖...")
        keyboard.wait(HOTKEY)

        # 在移除熱鍵前檢查它是否存在
        if HOTKEY in keyboard._hotkeys:
            keyboard.remove_hotkey(HOTKEY)

        # 重新加載配置以檢查是否已更新 bbox
        config = load_or_create_config()

    mainLoop(tuple(config['bbox']))
