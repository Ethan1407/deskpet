import json
import os
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
import ctypes
from ctypes import wintypes

# 數據存檔路徑
DATA_FILE = os.path.join(os.path.dirname(__file__), "screentime.json")

# --- 過濾名單：這些是系統背景進程，不應與你的軟體並列紀錄 ---
IGNORE_PROCS = ["python", "pythonw", "tk", "explorer", "taskhostw", "shellexperiencehost"]

def get_active_window_name():
    """使用原生 API 替代 PowerShell，解決時間加倍與重疊紀錄問題"""
    try:
        # 1. 獲取當前最前面的視窗控制碼
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return "Idle (待機/桌面)"

        # 2. 獲取該視窗的進程 ID (PID)
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # 3. 打開進程並讀取其執行檔名稱
        h_process = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if h_process:
            buf = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                full_path = buf.value
                # 取得檔名並轉小寫，例如 'brave.exe' -> 'brave'
                proc_name = os.path.basename(full_path).replace(".exe", "").lower()
                ctypes.windll.kernel32.CloseHandle(h_process)
                
                # --- 過濾與校正邏輯 ---
                # 如果偵測到的是系統進程或本程式(pythonw)，直接歸類為待機
                if proc_name in IGNORE_PROCS:
                    return "Idle (待機/桌面)"
                
                # 你的專屬轉換：Code 轉換為 vscode
                if "code" in proc_name:
                    return "vscode"
                    
                return proc_name
            ctypes.windll.kernel32.CloseHandle(h_process)
    except:
        pass
    return "Idle (待機/桌面)"

def update_time():
    """累計使用時間 (每分鐘呼叫一次)"""
    today = str(date.today())
    app_name = get_active_window_name()
    
    # 讀取現有資料
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}

    if today not in data:
        data[today] = {}
    
    # 關鍵修正：單次呼叫只會增加「一個」App 的時間，絕對不會同時增加
    data[today][app_name] = data[today].get(app_name, 0) + 1
    
    # 存檔
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ... (show_stats_window 以下的繪圖邏輯保持不變)