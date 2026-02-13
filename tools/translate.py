import tkinter as tk
from tkinter import scrolledtext
from deep_translator import GoogleTranslator

def translate_text(input_box, output_box, event=None):
    """
    執行翻譯邏輯。
    加上 event=None 是為了同時相容「滑鼠點擊」與「鍵盤 Enter」觸發。
    """
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        return "break"

    try:
        # 自動偵測語言邏輯
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            # 中翻英
            translated = GoogleTranslator(source='zh-TW', target='en').translate(text)
        else:
            # 英翻中
            translated = GoogleTranslator(source='en', target='zh-TW').translate(text)
        
        # 顯示結果
        output_box.config(state=tk.NORMAL)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, translated)
        output_box.config(state=tk.DISABLED)
    except Exception as e:
        output_box.config(state=tk.NORMAL)
        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, f"翻譯失敗: {str(e)}")
        output_box.config(state=tk.DISABLED)

    # 關鍵：回傳 "break" 可以攔截 Enter 鍵原本的換行功能，讓輸入框保持乾淨
    return "break"

def show_translate_window(parent):
    top = tk.Toplevel(parent)
    top.title("中英互譯工具")
    top.geometry("350x450")
    top.attributes("-topmost", True)
    top.resizable(False, False)

    tk.Label(top, text="請輸入文字 (自動偵測語言)", font=("Microsoft JhengHei", 10, "bold")).pack(pady=10)

    # 1. 輸入區
    input_box = scrolledtext.ScrolledText(top, height=8, width=40, font=("Consolas", 10))
    input_box.pack(padx=15, pady=5)

    # 2. 輸出區 (提前定義以供綁定使用)
    output_box = scrolledtext.ScrolledText(top, height=8, width=40, font=("Consolas", 10), state=tk.DISABLED, bg="#f0f0f0")

    # --- 鍵盤流優化 ---
    # 綁定 Enter 鍵觸發翻譯
    input_box.bind("<Return>", lambda e: translate_text(input_box, output_box))

    # 3. 翻譯按鈕 (保留原本功能)
    btn_trans = tk.Button(top, text="🔍 點我翻譯", font=("Microsoft JhengHei", 10),
                          command=lambda: translate_text(input_box, output_box),
                          bg="#3498db", fg="white", width=20)
    btn_trans.pack(pady=10)

    tk.Label(top, text="翻譯結果", font=("Microsoft JhengHei", 10, "bold")).pack(pady=5)

    # 顯示輸出區
    output_box.pack(padx=15, pady=5)

    # --- ✨ 自動聚焦 ---
    # 視窗開啟後游標自動跳到輸入框，直接打字不用點滑鼠
    input_box.focus_set()