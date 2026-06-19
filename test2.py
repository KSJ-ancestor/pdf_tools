import tkinter as tk
from tkinter import font as tkFont
import os
import sys

def resource_path(relative_path):
    """ PyInstaller 실행 파일에서 리소스 경로 찾기 """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 폰트 파일 경로
font1_path = resource_path(".\fonts\SpoqaHanSansNeo-Bold.ttf")
font2_path = resource_path(".\fonts\SpoqaHanSansNeo-Regular.ttf")

# Tkinter 윈도우 생성
root = tk.Tk()

# 커스텀 폰트 등록 (이름을 정해줘야 함)
font1_name = "Spoqa Han Sans Neo Bold"
font2_name = "Spoqa Han Sans Neo Regular"

# tcl에서 직접 폰트 등록
root.tk.call("font", "create", font1_name, "-family", font1_name, "-size", 14)
root.tk.call("font", "create", font2_name, "-family", font2_name, "-size", 14)

# Label 위젯에 각각 폰트 적용
label1 = tk.Label(root, text="폰트 1 적용", font=(font1_name, 14))
label1.pack()

label2 = tk.Label(root, text="폰트 2 적용", font=(font2_name, 14))
label2.pack()


print("Font1 Path:", font1_path)
print("Font2 Path:", font2_path)

print(root.tk.call("font", "names"))

root.mainloop()
