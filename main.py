import tkinter as tk
from PIL import Image, ImageTk
import os
import actions 
import json
import time
import threading
import pygetwindow as gw
from datetime import datetime
import sys

# ================= 數據配置區 =================
SAVE_PATH = "tools/screentime.json"
LOCK_FILE = "tools/pet.lock"

# 關鍵字判定：包含這些內容的通通歸類為 "VS Code"
# 修正：新增 "vscode" (無空格) 確保不會漏抓
VSCODE_KEYWORDS = ["visual studio code", "actions.py - deskpet", "vs code", "vscode"]
IGNORE_NAMES = ["tk", "python", "task host window", "py.exe", "program manager"]
# =============================================

class DesktopPet:
    def __init__(self):
        self.check_single_instance()
        self.window = tk.Tk()

        # 1. 視窗透明與置頂
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        trans_color = '#abcdef' 
        self.window.config(bg=trans_color)
        self.window.attributes("-transparentcolor", trans_color)

        # 2. 圖片處理
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_path, "pet.png")
        original_img = Image.open(img_path).convert("RGBA")
        scale_factor = 0.30 
        self.img_width = int(original_img.width * scale_factor)
        self.img_height = int(original_img.height * scale_factor)
        resized_right = original_img.resize((self.img_width, self.img_height), Image.Resampling.LANCZOS)
        resized_left = resized_right.transpose(Image.FLIP_LEFT_RIGHT)
        self.img_right = ImageTk.PhotoImage(resized_right)
        self.img_left = ImageTk.PhotoImage(resized_left)

        # 3. 介面與位置 (座標倍數鎖定為 2.5)
        self.label = tk.Label(self.window, image=self.img_right, bg=trans_color, bd=0)
        self.label.pack()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.x = (self.screen_width // 3) * 2.5 
        self.y = 38
        self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
        
        self.direction = 1     
        self.is_dragging = False
        self.menu_open = False 

        # 4. 螢幕紀錄
        self.screen_data = self.load_data()
        self.running = True
        self.temp_seconds_map = {} 
        
        self.tracker_thread = threading.Thread(target=self.track_screen_time, daemon=True)
        self.tracker_thread.start()

        actions.setup(self)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def check_single_instance(self):
        if os.path.exists(LOCK_FILE):
            sys.exit()
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))

    def on_closing(self):
        self.running = False
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        self.window.destroy()

    def get_app_name(self, raw_title):
        if not raw_title or not raw_title.strip():
            return "待機/桌面"
        
        t_low = raw_title.lower()

        # A. 優先排除雜訊
        if any(ignore in t_low for ignore in IGNORE_NAMES):
            return "待機/桌面"

        # B. 【重要修正】優先判定 VS Code，避免被後面的 split 邏輯截斷
        if any(kw in t_low for kw in VSCODE_KEYWORDS):
            return "VS Code"

        # C. Brave 容器偵測
        if "brave" in t_low:
            return "brave"

        # D. 遊戲判斷
        if "crosvm" in t_low:
            return "薑餅人王國"
        
        # E. 其他通用：抓標題最後一部分
        if " - " in raw_title:
            return raw_title.split(" - ")[-1].strip().lower()

        return "待機/桌面"

    def load_data(self):
        if not os.path.exists("tools"): os.makedirs("tools")
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_data(self):
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.screen_data, f, indent=4, ensure_ascii=False)

    def track_screen_time(self):
        while self.running:
            try:
                active_window = gw.getActiveWindow()
                title = active_window.title if active_window and active_window.title else ""
                current_app = self.get_app_name(title)
                
                today = datetime.now().strftime("%Y-%m-%d")
                if today not in self.screen_data:
                    self.screen_data[today] = {}

                self.temp_seconds_map[current_app] = self.temp_seconds_map.get(current_app, 0) + 1
                
                if self.temp_seconds_map[current_app] >= 60:
                    self.screen_data[today][current_app] = int(self.screen_data[today].get(current_app, 0)) + 1
                    self.temp_seconds_map[current_app] = 0
                
                if int(time.time()) % 10 == 0:
                    self.save_data()
                
                time.sleep(1)
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    try:
        DesktopPet()
    finally:
        if os.path.exists(LOCK_FILE): os.remove(LOCK_FILE)