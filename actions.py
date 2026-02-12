import tkinter as tk
from tkinter import scrolledtext
import random
import subprocess
import os
from tools import hardware, screentime, monitor, translate 

def setup(pet):
    """初始化事件與背景任務"""
    # 1. 左鍵雙擊：關閉桌寵 
    pet.label.bind("<Double-Button-1>", lambda e: pet.window.destroy())
    
    # 2. 左鍵拖曳
    pet.label.bind("<Button-1>", lambda e: start_drag(e, pet))
    pet.label.bind("<B1-Motion>", lambda e: on_drag(e, pet))
    pet.label.bind("<ButtonRelease-1>", lambda e: stop_drag(e, pet))
    
    # 3. 右鍵點擊：打開選單
    pet.label.bind("<Button-3>", lambda e: open_tool_menu(e, pet))
    
    walk(pet)
    start_background_tracker()

def start_background_tracker():
    """啟動背景紀錄器"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    tracker_path = os.path.join(base_path, "tools", "tracker.pyw")
    try:
        check_cmd = 'tasklist /FI "IMAGENAME eq pythonw.exe" /FO CSV'
        output = subprocess.check_output(check_cmd, shell=True).decode('cp950', errors='ignore')
        if "pythonw.exe" not in output:
            subprocess.Popen(["pythonw.exe", tracker_path], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"背景紀錄器啟動失敗: {e}")

def show_help_window(parent):
    """彈出修正後的桌寵使用說明視窗"""
    top = tk.Toplevel(parent)
    top.title("桌寵使用說明書")
    top.geometry("450x500") # 稍微加寬一點方便閱讀
    top.attributes("-topmost", True)
    top.resizable(False, False)

    # 建立滾動文字區域
    help_text = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Microsoft JhengHei", 10))
    help_text.pack(padx=20, pady=20, fill="both", expand=True)

    # 修改內容：移除 Emoji 避免換行問題，並更新關閉步驟
    content = """【 桌寵功能說明 】
1.💻硬體資料查詢：即時監控 CPU、RAM 與網速。點擊 RAM 數值可查看前 10 名資源佔用程式。
2.🌐中英翻譯工具：支援自動語言偵測，快速進行中英互譯。
3.📊螢幕使用時間：紀錄每日各應用程式的使用時數，並提供過去一週的趨勢圖表。
4.💤桌寵最小化：當玩遊戲或看影片時，可將桌寵縮小至系統匣。點擊工作列中向上三角裡的桌寵圖示即可恢復。
5.📖快捷操作：左鍵雙擊桌寵可立即關閉；長按左鍵可任意拖曳位置。

-------------------------------------

【 如何永久關閉（取消自動啟動） 】
若您不希望桌寵在開機時自動啟動，請執行以下步驟：
1. 按下鍵盤 Win + R。
2. 輸入「shell:startup」並按確定。
3. 找到「start_pet.bat - 捷徑」並將其刪除。
4. 找到「tracker.pyw - 捷徑」並將其刪除。

-------------------------------------

【 徹底結束目前運行的程式 】
若要立即完全關閉目前的背景程式，請開啟終端機輸入：
taskkill /F /IM pythonw.exe或至工作管理員結束所有名為 Python 的程序。
"""
    help_text.insert(tk.END, content)
    help_text.config(state=tk.DISABLED)

    tk.Button(top, text="我了解了", width=15, command=top.destroy, bg="#ecf0f1").pack(pady=10)

def open_tool_menu(event, pet):
    """彈出選單並校位"""
    if pet.menu_open: return 
    pet.menu_open = True 
    
    menu_w, menu_h = 200, 320 
    target_x, target_y = event.x_root, event.y_root
    
    # 自動校位
    if target_x + menu_w > pet.screen_width: target_x = pet.screen_width - menu_w - 10 
    if target_y + menu_h > pet.screen_height: target_y = pet.screen_height - menu_h - 10
    target_x, target_y = max(0, target_x), max(0, target_y)

    menu = tk.Toplevel(pet.window)
    menu.title("工具選單")
    menu.geometry(f"{menu_w}x{menu_h}+{int(target_x)}+{int(target_y)}")
    menu.attributes("-topmost", True)

    def on_close():
        pet.menu_open = False
        menu.destroy()

    menu.protocol("WM_DELETE_WINDOW", on_close)
    tk.Label(menu, text="選擇功能", font=("Microsoft JhengHei", 10, "bold")).pack(pady=10)

    # 按鈕區
    tk.Button(menu, text="💻 硬體資料查詢", width=20,
              command=lambda: [hardware.show_hardware_window(pet.window), on_close()]).pack(pady=2)

    tk.Button(menu, text="🌐 中英翻譯工具", width=20,
              command=lambda: [translate.show_translate_window(pet.window), on_close()]).pack(pady=2)

    tk.Button(menu, text="📊 螢幕使用時間", width=20,
              command=lambda: [screentime.show_stats_window(pet.window), on_close()]).pack(pady=2)

    tk.Button(menu, text="💤 桌寵最小化", width=20,
              command=lambda: [monitor.minimize_to_tray(pet), on_close()]).pack(pady=2)

    tk.Button(menu, text="📖 桌寵使用說明", width=20, fg="#34495e",
              command=lambda: [show_help_window(pet.window), on_close()]).pack(pady=(15, 2))

    tk.Button(menu, text="取消", width=20, command=on_close).pack(pady=5)

def walk(pet):
    """右側 1/3 走動邏輯"""
    if not pet.is_dragging and not pet.menu_open:
        if pet.window.state() != "withdrawn":
            if random.random() < 0.01: pet.direction *= -1
            step = random.randint(1, 5)
            next_x = pet.x + (step * pet.direction)
            
            left_limit = (pet.screen_width // 3) * 2 
            right_limit = pet.screen_width - pet.img_width
            
            if next_x > right_limit:
                pet.x = right_limit
                pet.direction = -1
            elif next_x < left_limit:
                pet.x = left_limit
                pet.direction = 1
            else:
                pet.x = next_x
                
            pet.label.config(image=pet.img_right if pet.direction == 1 else pet.img_left)
            pet.window.geometry(f"+{int(pet.x)}+{int(pet.y)}")
    
    pet.window.after(50, lambda: walk(pet))

def start_drag(event, pet):
    pet.is_dragging = True
    pet.drag_start_x, pet.drag_start_y = event.x, event.y

def on_drag(event, pet):
    if pet.is_dragging:
        pet.x = event.x_root - pet.drag_start_x
        pet.y = event.y_root - pet.drag_start_y
        pet.window.geometry(f"+{int(pet.x)}+{int(pet.y)}")

def stop_drag(event, pet):
    pet.is_dragging = False