import tkinter as tk
from PIL import Image, ImageTk
import os
import json
import time
import threading
import pygetwindow as gw
from datetime import datetime

# ================= 配置區 =================
PET_IMAGE_PATH = "pet.png"
SAVE_PATH = "tools/screentime.json"
RESIZE_RATIO = 0.3  # 縮放比例 30%

# 名稱映射表 (在此修改顯示名稱)
NAME_MAP = {
    "vscode": "VS Code",
    "crosvm": "薑餅人王國",
    "idle": "待機/桌面"
}
# ==========================================

class DesktopPet:
    def __init__(self):
        self.window = tk.Tk()
        
        # 1. 視窗基礎設定 (透明、無邊框、永遠最上層)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.config(bg='black') # 這裡設為一個底色
        self.window.wm_attributes("-transparentcolor", "black") # 將該底色設為透明
        
        # 2. 載入並縮放圖片
        self.load_image()
        
        # 3. 滑鼠拖曳功能
        self.window.bind("<Button-1>", self.start_move)
        self.window.bind("<B1-Motion>", self.on_move)
        
        # 4. 初始化紀錄數據
        self.screen_data = self.load_data()
        
        # 5. 啟動背景監控執行緒
        self.running = True
        self.tracker_thread = threading.Thread(target=self.track_screen_time, daemon=True)
        self.tracker_thread.start()
        
        self.window.mainloop()

    def load_image(self):
        """處理桌寵圖片載入與縮放"""
        if not os.path.exists(PET_IMAGE_PATH):
            print(f"錯誤：找不到圖片 {PET_IMAGE_PATH}")
            self.label = tk.Label(self.window, text="Missing Pet.png", fg="white", bg="black")
        else:
            img = Image.open(PET_IMAGE_PATH)
            # 轉換為 RGBA 確保透明度
            img = img.convert("RGBA")
            w, h = img.size
            img = img.resize((int(w * RESIZE_RATIO), int(h * RESIZE_RATIO)), Image.Resampling.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(img)
            self.label = tk.Label(self.window, image=self.tk_img, bg='black', bd=0)
        
        self.label.pack()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")

    def get_pretty_name(self, raw_title):
        """核心：將系統名稱轉換為自定義中文名稱"""
        if not raw_title or raw_title.strip() == "":
            return "待機/桌面"
        
        raw_title_lower = raw_title.lower()
        
        # 檢查映射表
        for key, display_name in NAME_MAP.items():
            if key in raw_title_lower:
                return display_name
        
        # 如果標題包含特定編碼或關鍵字也歸類為待機
        if "idle" in raw_title_lower or "\u5f85\u6a5f" in raw_title_lower:
            return "待機/桌面"
            
        # 若都不符合，回傳截斷後的原始標題
        return raw_title[:20]

    def load_data(self):
        """讀取 JSON 紀錄"""
        if not os.path.exists("tools"):
            os.makedirs("tools")
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_data(self):
        """存檔 JSON，解決中文亂碼問題"""
        with open(SAVE_PATH, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 是讓中文直接顯示的關鍵
            json.dump(self.screen_data, f, indent=4, ensure_ascii=False)

    def track_screen_time(self):
        """每秒偵測一次視窗名稱"""
        while self.running:
            try:
                # 獲取當前作用中視窗
                active_window = gw.getActiveWindow()
                raw_title = active_window.title if active_window else "idle"
                
                # 轉換名稱
                display_name = self.get_pretty_name(raw_title)
                
                # 紀錄數據
                today = datetime.now().strftime("%Y-%m-%d")
                if today not in self.screen_data:
                    self.screen_data[today] = {}
                
                self.screen_data[today][display_name] = self.screen_data[today].get(display_name, 0) + 1
                
                # 每 10 秒執行一次物理存檔
                if int(time.time()) % 10 == 0:
                    self.save_data()
                
                time.sleep(1)
            except Exception as e:
                # 避免因為抓不到視窗而導致程式崩潰
                time.sleep(1)

if __name__ == "__main__":
    DesktopPet()