import tkinter as tk
from PIL import Image, ImageTk
import os
import actions 
import json
import time
import threading
from datetime import datetime
import sys
import ctypes
from ctypes import wintypes

# ================= 數據配置區 =================
SAVE_PATH = "tools/screentime.json"
LOCK_FILE = "tools/pet.lock"

# 排除不需要紀錄的系統進程
IGNORE_PROCS = ["idle", "explorer", "taskhostw", "python", "tk", "shellexperiencehost"]
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

        # 3. 介面與位置 (座標倍數絕對是 2.5)
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
        self.temp_seconds_map = {} # 暫存秒數
        
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

    def get_app_name(self):
        """ 
        使用 Windows 原生 API 獲取進程名稱 (不需要 psutil)
        """
        try:
            # 獲取目前活躍視窗控制碼
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd: return "待機/桌面"

            # 獲取進程 ID (PID)
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            # 打開進程讀取路徑 (PROCESS_QUERY_LIMITED_INFORMATION = 0x1000)
            h_process = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if h_process:
                buf = ctypes.create_unicode_buffer(260)
                size = wintypes.DWORD(260)
                # 獲取可執行檔的完整路徑
                if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                    full_path = buf.value
                    proc_name = os.path.basename(full_path).replace(".exe", "").lower()
                    ctypes.windll.kernel32.CloseHandle(h_process)
                    
                    # --- 紀錄轉化邏輯 ---
                    if proc_name in IGNORE_PROCS: return "待機/桌面"
                    if proc_name == "code": return "VS Code"
                    if "brave" in proc_name: return "brave"
                    if "crosvm" in proc_name: return "薑餅人王國"
                    return proc_name
                ctypes.windll.kernel32.CloseHandle(h_process)
        except:
            pass
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
                current_app = self.get_app_name()
                
                today = datetime.now().strftime("%Y-%m-%d")
                if today not in self.screen_data:
                    self.screen_data[today] = {}

                # 累積秒數
                self.temp_seconds_map[current_app] = self.temp_seconds_map.get(current_app, 0) + 1
                
                # 滿 60 秒後，JSON 數值整數 +1
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