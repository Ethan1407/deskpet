import tkinter as tk
from PIL import Image, ImageTk
import os
import actions 

class DesktopPet:
    def __init__(self):
        self.window = tk.Tk()

        # 1. 視窗透明與置頂設定
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        trans_color = '#abcdef' 
        self.window.config(bg=trans_color)
        self.window.attributes("-transparentcolor", trans_color)

        # 2. 圖片處理 (30% 縮放)
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_path, "pet.png")
        original_img = Image.open(img_path).convert("RGBA")
        
        scale_factor = 0.30 
        self.img_width = int(original_img.width * scale_factor)
        self.img_height = int(original_img.height * scale_factor)
        
        resized_right = original_img.resize((self.img_width, self.img_height), Image.LANCZOS)
        resized_left = resized_right.transpose(Image.FLIP_LEFT_RIGHT)

        self.img_right = ImageTk.PhotoImage(resized_right)
        self.img_left = ImageTk.PhotoImage(resized_left)

        # 3. 介面與狀態
        self.label = tk.Label(self.window, image=self.img_right, bg=trans_color, bd=0)
        self.label.pack()

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        # --- 安全座標：改為 2.2 倍寬度避免掉出螢幕 ---
        self.x = (self.screen_width // 3) * 2.2
        self.y = 38
        
        # 強制在啟動時先畫出位置，避免走動邏輯還沒啟動前視窗是隱形的
        self.window.geometry(f"+{int(self.x)}+{int(self.y)}")
        
        self.direction = 1     
        self.is_dragging = False
        self.menu_open = False 

        # 啟動邏輯
        actions.setup(self)
        self.window.mainloop()

if __name__ == "__main__":
    DesktopPet()