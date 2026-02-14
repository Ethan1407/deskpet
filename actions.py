import tkinter as tk
from tkinter import scrolledtext
import random
import os
from tools import hardware, screentime, monitor, translate 
def setup(pet):
    pet.label.bind("<Double-Button-1>", lambda e: pet.on_closing())
    pet.label.bind("<Button-1>", lambda e: start_drag(e, pet))
    pet.label.bind("<B1-Motion>", lambda e: on_drag(e, pet))
    pet.label.bind("<ButtonRelease-1>", lambda e: stop_drag(e, pet))
    pet.label.bind("<Button-3>", lambda e: open_tool_menu(e, pet))
    walk(pet)
def open_tool_menu(event, pet):
    if pet.menu_open: return 
    pet.menu_open = True 
    menu_w, menu_h = 200, 320 
    target_x, target_y = event.x_root, event.y_root
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
    tk.Button(menu, text="💻 硬體資料查詢", width=20, command=lambda: [hardware.show_hardware_window(pet.window), on_close()]).pack(pady=2)
    tk.Button(menu, text="🌐 中英翻譯工具", width=20, command=lambda: [translate.show_translate_window(pet.window), on_close()]).pack(pady=2)
    tk.Button(menu, text="📊 螢幕使用紀錄", width=20, command=lambda: [screentime.show_stats_window(pet.window), on_close()]).pack(pady=2)
    tk.Button(menu, text="💤 桌寵最小化", width=20, command=lambda: [monitor.minimize_to_tray(pet), on_close()]).pack(pady=2)
    tk.Button(menu, text="📖 桌寵使用說明", width=20, fg="#34495e", command=lambda: [show_help_window(pet.window), on_close()]).pack(pady=(15, 2))
    tk.Button(menu, text="取消", width=20, command=on_close).pack(pady=5)
def walk(pet):
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
def show_help_window(parent):
    top = tk.Toplevel(parent)
    top.title("桌寵使用說明書")
    top.geometry("500x550")
    top.attributes("-topmost", True)
    top.resizable(False, False)
    help_text = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Microsoft JhengHei", 10))
    help_text.pack(padx=20, pady=20, fill="both", expand=True)
    content = """1.💻硬體資料查詢：即時監控 CPU、RAM 與網速。點擊 RAM 數值可查看前 10 名資源佔用程式。
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
4. 找到「tracker.pyw - 捷徑」並將其刪除。"""
    help_text.insert(tk.END, content)
    help_text.config(state=tk.DISABLED)
    tk.Button(top, text="我了解了", width=15, command=top.destroy, bg="#ecf0f1").pack(pady=10)