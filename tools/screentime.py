import json
import os
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
import ctypes
from ctypes import wintypes
import time
DATA_FILE = os.path.join(os.path.dirname(__file__), "screentime.json")
IGNORE_PROCS = ["python", "pythonw", "tk", "explorer", "taskhostw", "py", "pyw", "shellexperiencehost"]
last_recorded_app = None
last_recorded_time = None
def get_active_window_name():
    """使用原生 Windows API 抓取進程名稱，全部回傳小寫英文執行檔名"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return "idle"
        pid = wintypes.DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h_process = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if h_process:
            buf = ctypes.create_unicode_buffer(260)
            size = wintypes.DWORD(260)
            if ctypes.windll.kernel32.QueryFullProcessImageNameW(h_process, 0, buf, ctypes.byref(size)):
                full_path = buf.value
                proc_name = os.path.basename(full_path).replace(".exe", "").lower()
                ctypes.windll.kernel32.CloseHandle(h_process)
                if proc_name in IGNORE_PROCS:
                    return "idle"
                return proc_name
            ctypes.windll.kernel32.CloseHandle(h_process)
    except:
        pass
    return "idle"
def update_time():
    global last_recorded_app, last_recorded_time
    today = str(date.today())
    app_name = get_active_window_name()
    
    # 防止重複偵測：同一個應用在短時間內不重複計數
    current_time = time.time()
    if last_recorded_app == app_name and last_recorded_time is not None:
        if current_time - last_recorded_time < 55:  # 55秒內不重複計數
            return
    
    last_recorded_app = app_name
    last_recorded_time = current_time
    
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    
    if today not in data:
        data[today] = {}
    
    # 確保應用名稱統一為小寫
    app_name = app_name.lower()
    data[today][app_name] = data[today].get(app_name, 0) + 1
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
def show_stats_window(parent):
    top = tk.Toplevel(parent)
    top.title("Screen Time Stats")
    top.geometry("400x680")
    top.attributes("-topmost", True)
    current_offset = tk.IntVar(value=0)
    week_map = ["一", "二", "三", "四", "五", "六", "日"]
    def load_all_data():
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 標準化所有應用名稱為小寫，合併重複項
                    for date_key in data:
                        normalized_apps = {}
                        for app_name, minutes in data[date_key].items():
                            app_lower = app_name.lower()
                            normalized_apps[app_lower] = normalized_apps.get(app_lower, 0) + minutes
                        data[date_key] = normalized_apps
                    return data
            except:
                return {}
        return {}
    all_data = load_all_data()
    header_frame = tk.Frame(top)
    header_frame.pack(fill="x", pady=10)
    date_label = tk.Label(header_frame, text="", font=("Microsoft JhengHei", 11, "bold"))
    def draw_trend_chart():
        canvas.delete("all")
        past_seven_days = []
        for i in range(-6, 1):
            d = str(date.today() + timedelta(days=i))
            mins = sum(all_data.get(d, {}).values())
            past_seven_days.append(mins)
        max_val = max(past_seven_days) if max(past_seven_days) > 0 else 60
        bar_width, gap, start_x = 30, 15, 30
        for i, val in enumerate(past_seven_days):
            h = (val / max_val) * 80 if max_val > 0 else 0
            x0 = start_x + i * (bar_width + gap)
            current_view_idx = 6 + current_offset.get()
            color = "#3498db" if i == current_view_idx else "#bdc3c7"
            canvas.create_rectangle(x0, 100-h, x0+bar_width, 100, fill=color, outline="")
            if val > 0: canvas.create_text(x0 + 15, 92-h, text=str(val), font=("Arial", 7))
            d_label = (date.today() + timedelta(days=i-6)).strftime("%m/%d")
            canvas.create_text(x0 + 15, 110, text=d_label, font=("Arial", 7))
    def refresh_ui():
        target_date = date.today() + timedelta(days=current_offset.get())
        date_str = str(target_date)
        weekday_str = week_map[target_date.weekday()]
        date_label.config(text=f"Date: {date_str} ({weekday_str})")
        for item in tree.get_children(): tree.delete(item)
        day_data = all_data.get(date_str, {})
        total_minutes = sum(day_data.values())
        sorted_apps = sorted(day_data.items(), key=lambda x: x[1], reverse=True)
        for i, (app, mins) in enumerate(sorted_apps[:10], 1):
            tree.insert("", tk.END, values=(i, app, mins))
        hours, mins = total_minutes // 60, total_minutes % 60
        summary_var.set(f"Total: {hours} h {mins} m")
        draw_trend_chart()
    btn_prev = tk.Button(header_frame, text="◀", command=lambda: [current_offset.set(current_offset.get()-1), refresh_ui()])
    btn_prev.pack(side=tk.LEFT, padx=20)
    date_label.pack(side=tk.LEFT, expand=True)
    btn_next = tk.Button(header_frame, text="▶", command=lambda: [current_offset.set(current_offset.get()+1), refresh_ui()])
    btn_next.pack(side=tk.RIGHT, padx=20)
    columns = ("rank", "app", "time")
    tree = ttk.Treeview(top, columns=columns, show="headings", height=8)
    tree.heading("rank", text="Rank")
    tree.heading("app", text="Application")
    tree.heading("time", text="Min")
    tree.column("rank", width=40, anchor="center")
    tree.column("app", width=180, anchor="w")
    tree.column("time", width=60, anchor="center")
    tree.pack(fill="both", padx=15, pady=5)
    summary_var = tk.StringVar()
    tk.Label(top, textvariable=summary_var, font=("Consolas", 10, "bold"), fg="#2c3e50").pack(pady=5)
    canvas = tk.Canvas(top, width=350, height=120, bg="white", highlightthickness=1)
    canvas.pack(pady=5)
    refresh_ui()