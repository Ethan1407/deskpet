import tkinter as tk
from PIL import Image, ImageTk
import os
import actions 
import time
import threading
import sys
from tools import screentime
LOCK_FILE = "tools/pet.lock"
class DesktopPet:
    def __init__(self):
        self.check_single_instance()
        self.window = tk.Tk()
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        trans_color = '#abcdef' 
        self.window.config(bg=trans_color)
        self.window.attributes("-transparentcolor", trans_color)
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
        self.running = True
        self.tracker_thread = threading.Thread(target=self.run_tracker, daemon=True)
        self.tracker_thread.start()
        actions.setup(self)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
    def check_single_instance(self):
        if not os.path.exists("tools"): os.makedirs("tools")
        if os.path.exists(LOCK_FILE):
            sys.exit()
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    def run_tracker(self):
        while self.running:
            try:
                screentime.update_time()
                time.sleep(60)
            except Exception:
                time.sleep(5)
    def on_closing(self):
        self.running = False
        if os.path.exists(LOCK_FILE):
            try: os.remove(LOCK_FILE)
            except: pass
        self.window.destroy()
if __name__ == "__main__":
    try:
        DesktopPet()
    finally:
        if os.path.exists(LOCK_FILE):
            try: os.remove(LOCK_FILE)
            except: pass