import pystray
from PIL import Image
import os

# 全域變數，用來控制圖示狀態
icon = None

def minimize_to_tray(pet):
    """隱藏視窗並在系統匣顯示圖示"""
    # 1. 隱藏 Tkinter 視窗
    pet.window.withdraw()
    
    # 2. 設定圖示圖片
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(base_path, "pet.png")
    image = Image.open(img_path)

    # 3. 定義恢復視窗的函式
    def on_restore(icon, item=None):
        """恢復視窗顯示 (支援選單點擊與直接點擊圖示)"""
        icon.stop() # 停止系統匣圖示
        pet.window.after(0, pet.window.deiconify) # 恢復視窗
        pet.window.after(0, lambda: pet.window.attributes("-topmost", True))

    # 4. 建立系統匣選單 (並將恢復設為預設動作)
    menu = pystray.Menu(
        pystray.MenuItem("恢復桌寵", on_restore, default=True),
        pystray.MenuItem("結束程式", lambda: pet.window.destroy())
    )

    # 5. 啟動系統匣圖示
    global icon
    # 加入 action=on_restore 參數，讓左鍵點擊圖示直接觸發恢復
    icon = pystray.Icon("DesktopPet", image, "桌寵運行中", menu=menu, action=on_restore)
    
    icon.run_detached()