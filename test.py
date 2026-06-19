import tkinter as tk
from tkinter import ttk
import threading
import time

class ModalProgress:
    def __init__(self, parent):
        """모달 창 초기화"""
        self.modal = tk.Toplevel(parent)
        self.modal.title("Processing")
        self.modal.geometry("300x150")
        self.modal.resizable(False, False)

        # 모달 창을 중간에 위치시키기
        self.modal.transient(parent)
        self.modal.grab_set()

        # 진행 변수와 프로그래스바 생성
        self.progress_var = tk.IntVar(value=0)
        self.progress_bar = ttk.Progressbar(self.modal, maximum=100, variable=self.progress_var, length=250)
        self.progress_bar.pack(pady=20)

        # 진행률 표시 레이블
        self.progress_label = tk.Label(self.modal, text="Progress: 0%")
        self.progress_label.pack()

        # 작업 종료 버튼 (초기에는 비활성화)
        self.close_button = tk.Button(self.modal, text="Close", state="disabled", command=self.modal.destroy)
        self.close_button.pack(pady=10)

    def update_progress(self, value):
        """프로그램 진행 상태 업데이트"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"Progress: {value}%")
        self.modal.update_idletasks()  # UI 강제 업데이트

    def enable_close(self):
        """작업 완료 후 종료 버튼 활성화"""
        self.close_button.config(state="normal")

def start_long_task():
    """메인 UI에서 모달 창 제어"""
    # 모달 창 생성
    progress_modal = ModalProgress(root)

    def long_running_task():
        """시간이 걸리는 작업"""
        for i in range(101):
            time.sleep(0.05)  # 작업 시뮬레이션
            progress_modal.update_progress(i)  # 진행 상태 업데이트
        progress_modal.enable_close()  # 완료 후 종료 버튼 활성화

    # 작업을 백그라운드에서 실행
    threading.Thread(target=long_running_task, daemon=True).start()

# 메인 윈도우 생성
root = tk.Tk()
root.title("Main Window")
root.geometry("400x300")

# 모달 프로그래스바 실행 버튼
button = tk.Button(root, text="Start Task", command=start_long_task)
button.pack(pady=50)

root.mainloop()
