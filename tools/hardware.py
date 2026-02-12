import psutil
import time
import tkinter as tk
from tkinter import ttk

def get_net_speed():
    """計算即時網速"""
    old_io = psutil.net_io_counters()
    time.sleep(0.3) 
    new_io = psutil.net_io_counters()
    down = (new_io.bytes_recv - old_io.bytes_recv) / 1024 / 0.3
    up = (new_io.bytes_sent - old_io.bytes_sent) / 1024 / 0.3
    return f"⬇ {down:.1f} KB/s | ⬆ {up:.1f} KB/s"

def show_ram_details(parent):
    """彈出前十名 RAM 佔用程式清單"""
    detail_win = tk.Toplevel(parent)
    detail_win.title("RAM 佔用排行")
    detail_win.geometry("300x350")
    detail_win.attributes("-topmost", True)
    
    tk.Label(detail_win, text="🚀 記憶體佔用前 10 名", font=("Microsoft JhengHei", 10, "bold")).pack(pady=10)
    
    # 建立表格
    columns = ("app", "usage")
    tree = ttk.Treeview(detail_win, columns=columns, show="headings", height=10)
    tree.heading("app", text="應用程式")
    tree.heading("usage", text="佔用 %")
    tree.column("app", width=180)
    tree.column("usage", width=80, anchor="center")
    tree.pack(padx=10, pady=5, fill="both", expand=True)

    # 抓取資料
    processes = []
    for proc in psutil.process_iter(['name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # 排序並取前 10
    top10 = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
    for p in top10:
        tree.insert("", tk.END, values=(p['name'], f"{p['memory_percent']:.1f}%"))

def show_hardware_window(parent):
    """硬體監控主視窗"""
    top = tk.Toplevel(parent)
    top.title("硬體資料查詢")
    top.geometry("320x250") # 縮小一點，因為移除了 GPU
    top.attributes("-topmost", True)
    top.resizable(False, False)

    tk.Label(top, text="💻 系統即時監控", font=("Microsoft JhengHei", 12, "bold")).pack(pady=10)

    cpu_label = tk.Label(top, text="CPU: 讀取中...", font=("Consolas", 10))
    cpu_label.pack(pady=5)
    
    # RAM 標籤：加上提示訊息與點擊綁定
    ram_label = tk.Label(top, text="RAM: 讀取中...", font=("Consolas", 10), fg="#2980b9", cursor="hand2")
    ram_label.pack(pady=5)
    tk.Label(top, text="(點擊 RAM 查看詳情)", font=("Microsoft JhengHei", 8), fg="gray").pack()
    
    ram_label.bind("<Button-1>", lambda e: show_ram_details(top))

    net_label = tk.Label(top, text="網路: 讀取中...", font=("Consolas", 10))
    net_label.pack(pady=5)

    def update():
        if not top.winfo_exists(): return
        cpu_p = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        cpu_label.config(text=f"CPU 使用率: {cpu_p}%")
        ram_label.config(text=f"RAM 使用率: {ram.percent}% ({ram.used//1024//1024}MB)")
        net_label.config(text=f"網路速度: {get_net_speed()}")
        top.after(1000, update)

    update()