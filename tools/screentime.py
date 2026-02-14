import json
import os
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
import ctypes
from ctypes import wintypes

# --- 數據存檔路徑 ---
DATA_FILE = os.path.join(os.path.dirname(__file__), "screentime.json")

# --- 過濾名單：不計時的系統進程 ---
IGNORE_PROCS = ["python", "pythonw", "tk", "explorer", "taskhostw", "py", "pyw", "shellexperiencehost"]

def get_active_window_name():
    """使用原生 Windows API 抓取進程名稱，取代耗時的 PowerShell"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return "Idle (待機/桌面)"

        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        h_process = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if h_process:
            buf = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                full_path = buf.value
                proc_name = os.path.basename(full_path).replace(".exe", "").lower()
                ctypes.windll.kernel32.CloseHandle(h_process)
                
                # 排除過濾名單
                if proc_name in IGNORE_PROCS:
                    return "Idle (待機/桌面)"
                
                # 專屬轉換邏輯
                if "code" in proc_name:
                    return "vscode"
                if "brave" in proc_name:
                    return "brave"
                if "crosvm" in proc_name:
                    return "薑餅人王國"
                    
                return proc_name
            ctypes.windll.kernel32.CloseHandle(h_process)
    except:
        pass
    return "Idle (待機/桌面)"

def update_time():
    """累計使用時間 (由 main.py 每分鐘呼叫一次)"""
    today = str(date.today())
    app_name = get_active_window_name()
    
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}

    if today not in data:
        data[today] = {}
    
    # 紀錄 (每次呼叫 +1 分鐘)
    data[today][app_name] = data[today].get(app_name, 0) + 1
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def show_stats_window(parent):
    """彈出統計視窗"""
    top = tk.Toplevel(parent)
    top.title("螢幕使用紀錄與趨勢")
    top.geometry("400x680")
    top.attributes("-topmost", True)

    current_offset = tk.IntVar(value=0)
    week_map = ["一", "二", "三", "四", "五", "六", "日"]

    def load_all_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    all_data = load_all_data()

    # --- UI 佈局 ---
    header_frame = tk.Frame(top)
    header_frame.pack(fill="x", pady=10)

    date_label = tk.Label(header_frame, text="", font=("Microsoft JhengHei", 11, "bold"))
    
    # 前置定義畫圖函式，避免 refresh_ui 呼叫失敗
    def draw_trend_chart():
        canvas.delete("all")
        past_seven_days = []
        for i in range(-6, 1):
            d = str(date.today() + timedelta(days=i))
            mins = sum(all_data.get(d, {}).values())
            past_seven_days.append(mins)
        
        max_val = max(past_seven_days) if max(past_seven_days) > 0 else 60
        bar_width = 30
        gap = 15
        start_x = 30
        
        for i, val in enumerate(past_seven_days):
            h = (val / max_val) * 80 if max_val > 0 else 0
            x0 = start_x + i * (bar_width + gap)
            current_view_idx = 6 + current_offset.get()
            color = "#3498db" if i == current_view_idx else "#bdc3c7"
            canvas.create_rectangle(x0, 100-h, x0+bar_width, 100, fill=color, outline="")
            if val > 0:
                canvas.create_text(x0 + 15, 92-h, text=str(val), font=("Arial", 7))
            d_label = (date.today() + timedelta(days=i-6)).strftime("%m/%d")
            canvas.create_text(x0 + 15, 110, text=d_label, font=("Arial", 7))

    def refresh_ui():
        target_date = date.today() + timedelta(days=current_offset.get())
        date_str = str(target_date)
        weekday_str = week_map[target_date.weekday()]
        date_label.config(text=f"📅 日期: {date_str} ({weekday_str})")
        
        for item in tree.get_children():
            tree.delete(item)
            
        day_data = all_data.get(date_str, {})
        total_minutes = sum(day_data.values())
        
        sorted_apps = sorted(day_data.items(), key=lambda x: x[1], reverse=True)
        for i, (app, mins) in enumerate(sorted_apps[:10], 1):
            tree.insert("", tk.END, values=(i, app, mins))
            
        hours = total_minutes // 60
        mins = total_minutes % 60
        summary_var.set(f"該日總計： {hours} 小時 {mins} 分鐘")
        draw_trend_chart()

    btn_prev = tk.Button(header_frame, text="◀", command=lambda: [current_offset.set(current_offset.get()-1), refresh_ui()])
    btn_prev.pack(side=tk.LEFT, padx=20)
    date_label.pack(side=tk.LEFT, expand=True)
    btn_next = tk.Button(header_frame, text="▶", command=lambda: [current_offset.set(current_offset.get()+1), refresh_ui()])
    btn_next.pack(side=tk.RIGHT, padx=20)

    # 排名表格
    columns = ("rank", "app", "time")
    tree = ttk.Treeview(top, columns=columns, show="headings", height=8)
    tree.heading("rank", text="排名")
    tree.heading("app", text="應用程式")
    tree.heading("time", text="分鐘")
    tree.column("rank", width=40, anchor="center")
    tree.column("app", width=180, anchor="w")
    tree.column("time", width=60, anchor="center")
    tree.pack(fill="both", padx=15, pady=5)

    summary_var = tk.StringVar()
    tk.Label(top, textvariable=summary_var, font=("Microsoft JhengHei", 10, "bold"), fg="#2c3e50").pack(pady=5)

    tk.Label(top, text="📈 過去七天趨勢 (分鐘)", font=("Microsoft JhengHei", 9)).pack(pady=(10, 0))
    canvas = tk.Canvas(top, width=350, height=120, bg="white", highlightthickness=1)
    canvas.pack(pady=5)

    # 第一次執行刷新
    refresh_ui()