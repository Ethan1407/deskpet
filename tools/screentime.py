import subprocess
import json
import os
import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta

# 數據存檔路徑
DATA_FILE = os.path.join(os.path.dirname(__file__), "screentime.json")

def get_active_window_name():
    """抓取視窗名稱，並強制將 Code 轉換為 vscode"""
    try:
        ps_script = "(Get-Process | Where-Object {$_.MainWindowHandle -eq (Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class User32 { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); }' -PassThru)::GetForegroundWindow()}).Name"
        output = subprocess.check_output(["powershell", "-Command", ps_script], shell=True).decode('utf-8', errors='ignore').strip()
        
        # --- 強化版轉換邏輯 ---
        name_lower = output.lower()
        if "code" in name_lower:
            return "vscode"
            
        return output if output else "Idle (待機/桌面)"
    except:
        return "Unknown"

def update_time():
    """累計使用時間 (每分鐘呼叫一次)"""
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
    
    # 紀錄
    data[today][app_name] = data[today].get(app_name, 0) + 1
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

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

    header_frame = tk.Frame(top)
    header_frame.pack(fill="x", pady=10)

    date_label = tk.Label(header_frame, text="", font=("Microsoft JhengHei", 11, "bold"))
    
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

    refresh_ui()