import time
import os
import sys

# 將上一層目錄加入路徑，以便匯入 screentime 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import screentime

def run_tracker():
    """背景紀錄循環"""
    while True:
        try:
            # 呼叫你原本寫好的紀錄邏輯
            screentime.update_time()
        except:
            pass # 確保背景程式不會因為意外報錯而中斷
        
        # 每 60 秒紀錄一次
        time.sleep(60)

if __name__ == "__main__":
    run_tracker()