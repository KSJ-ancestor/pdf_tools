#################################################
## editor : Kim Sean Je
## e-mail : ancestor@korea.kr
##          cowpower@kakao.com
## R-date : 2026.06.10.
#################################################
## pip install PyMuPDF PyPDF2 Pillow pycryptodome
#################################################

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import font

import tkinter as tk
import tkinter.ttk

import os
import math
import sys
import threading
from datetime import datetime
from time import time
from time import ctime
import traceback

# PDF 처리 코어 라이브러리
import fitz  # PyMuPDF
from PIL import Image, ImageTk, ImageEnhance
Image.MAX_IMAGE_PIXELS = None

import PyPDF2
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter

# ---------------------------------------------------------
# 전역 변수 초기화
# ---------------------------------------------------------
global VERSION
VERSION ="V.1.0 (Masterpiece)"

# 탭별 PyMuPDF Document 객체 보관용 (메모리 절약을 위해 객체 1개만 유지)
global tab4_doc, tab4_rotations
tab4_doc = None
tab4_rotations = []

global tab5_doc
tab5_doc = None

global tab6_doc, tab6_watermark_img
tab6_doc = None
tab6_watermark_img = None

global glb_open_file_path
glb_open_file_path = "."

# ---------------------------------------------------------
# 기본 윈도우 설정
# ---------------------------------------------------------
window = tk.Tk()
window.option_add("*Font", "Calibri 11")
window.title("PDF 도구(" + VERSION + ")")

screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()

app_w = 1100
app_h = screen_h - 110
x = int((screen_w-app_w)/2) 
y = 10 

window.geometry(f"{app_w}x{app_h}+{x}+{y}")
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
window.resizable(True, True)
window.minsize(app_w, app_h)

def resource_path(relative_path):
   base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
   return os.path.join(base_path, relative_path)

# ---------------------------------------------------------
# UI 유틸리티 함수
# ---------------------------------------------------------
def fn_pb_init(obj):
   window.config(cursor="circle")  
   window.update()
   objlen = obj.winfo_width()
   objhei = obj.winfo_height()
   objdep = obj.winfo_depth()
   objx = obj.winfo_x()
   objy = obj.winfo_y() + objdep
   vb_pb.set(0)
   pb.place(x=objx, y=objy, width=objlen, height=objhei)
   
def fn_pb_set(val):
   window.update()
   vb_pb.set(vb_pb.get() + val)
   style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(round(vb_pb.get(),0)))
   pb.update()

def fn_pb_exit():
   pb.place(x=0, y=0, width=0, height=0)
   window.config(cursor="arrow")

def donothing():
   messagebox.showinfo(VERSION,"[editor] \t Kim Seon Je \n\n\t ancestor@korea.kr \n\n\t cowpower@kakao.com")

def showSystemMessage():
   state = tabs.tab(tab7)['state']
   if state == "hidden":
      tabs.add(tab7,text=" System message ")
      tabs.select(6)
   else:
      tabs.hide(6)
      
def writeLog(msg):
   text_tab7.insert(tk.END, "[" + ctime(time()) + "]", 'time')
   text_tab7.insert(tk.END, "\n", 'body')
   text_tab7.insert(tk.END, msg, 'body')
   text_tab7.insert(tk.END, "\n", 'body')
   text_tab7.tag_config('body', foreground='#DDDDDD')  
   text_tab7.tag_config('time', foreground='yellow')   
   text_tab7.see("end")
   
def get_fitz_pixmap_as_pil(page, zoom=1.5):
    """PyMuPDF 페이지를 고해상도 PIL 이미지로 즉각 변환하는 헬퍼 함수"""
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    # RGBA 처리가 필요한 워터마크 등을 위해 분기
    mode = "RGBA" if pix.alpha else "RGB"
    img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
    return img

def fit_image_to_label(img, label_w, label_h, margin_w=200, margin_h=100):
    """라벨 크기에 맞춰 이미지 리사이징 헬퍼 함수"""
    if label_w < margin_w or label_h < margin_h:
        return img
    
    x = label_w - margin_w
    y = label_h - margin_h
    width, height = img.size
    
    if width < height:
        y = int(x * 1.4)
        if y > label_h - margin_h:
            y = label_h - margin_h
            x = int(y / 1.4)
    else:
        x = int(y * 1.4)
        if x > label_w - margin_w:
            x = label_w - margin_w
            y = int(x / 1.4)
            
    return img.resize((x, y))

# =========================================================
# TAB 1: Merge files
# =========================================================
def fn_fileAdd():
   global glb_open_file_path
   files = filedialog.askopenfilenames(initialdir = glb_open_file_path, title="select PDF files", filetypes=[("pdf files","*.pdf")])
   if files == "" : return
   glb_open_file_path = os.path.dirname(files[0])
   for i in range(len(files)):
      filesize = format(math.ceil(os.path.getsize(files[i])/1000),",") + " KB"
      modified_time = os.path.getmtime(files[i])
      modified_date = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
      tab1_tree.insert(parent='', index='end', text='', values=(files[i], filesize, modified_date))

def fn_fileDel():
    try:
        item = tab1_tree.selection()[0]
        tab1_tree.delete(item)
    except IndexError:
        messagebox.showwarning("warning","Need to select something")
      
def fn_filedelAll():
   for row in tab1_tree.get_children():
       tab1_tree.delete(row)

def fn_fileUp():
   leaves = tab1_tree.selection()
   for i in leaves: tab1_tree.move(i, tab1_tree.parent(i), tab1_tree.index(i)-1)

def fn_fileDown():
   leaves = tab1_tree.selection()
   for i in reversed(leaves): tab1_tree.move(i, tab1_tree.parent(i), tab1_tree.index(i)+1)

def fn_clear():
   fn_filedelAll()
   lb_MergedFile.config(text='')

def fn_tab1_Run():
   merger = PdfMerger()
   filecnt = len(tab1_tree.get_children())
   if filecnt==0:
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. 대상 PDF 파일들을 추가하세요.\n2단계. 파일 순서를 정렬하세요.\n3단계. 저장(병합) 버튼을 누르세요!\n4단계. 생성된 파일이나 폴더를 확인하세요.")
      return
   
   global glb_open_file_path
   filename = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='merged.pdf')
   if filename=="": return
   if filename[-3:].upper() != "PDF": filename += ".pdf"

   window.update()
   lb_MergedFile.config(text="[병합 중... " + str(filecnt) + " files]")

   try:
      i = 0
      for row in tab1_tree.get_children():
         fn = tab1_tree.item(row).get('values')[0]
         merger.append(fn)
         lb_MergedFile.config(text="[Merging... " + str(i+1) +"/" + str(filecnt) + "] " + str(round((i/filecnt) * 100,2)) + "%")
         window.update()
         i+=1
         
      lb_MergedFile.config(text="writing pdf file(" + filename + ")...")
      window.update()
      merger.write(filename)
      merger.close() # 괄호 추가 버그 픽스
      lb_MergedFile.config(text=str(filename))
      messagebox.showinfo("merge files","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("Error", e)
      lb_MergedFile.config(text="")

def fn_fileOpen():
   if lb_MergedFile.cget("text") == "": return
   os.startfile(os.path.realpath(lb_MergedFile.cget("text")))

def fn_folderOpen():
   if lb_MergedFile.cget("text") == "": return
   os.startfile(os.path.dirname(lb_MergedFile.cget("text")))

# =========================================================
# TAB 2: Convert to Image
# =========================================================
def fn_tab2_setPDFFile():
   global glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)
   fn_tab2_clear()
   lb_tab2_filename.config(text=str(file))

def fn_tab2_setFolder():
   folder=filedialog.askdirectory()
   if folder == "" : return
   lb_tab2_foldername.config(text=str(folder))

def fn_tab2_Run():
   thread = threading.Thread(target = fn_tab2_Run_thread)
   thread.daemon = True
   thread.start()

def fn_tab2_Run_thread():
   filename = lb_tab2_filename.cget("text")
   folder = lb_tab2_foldername.cget("text")
   if not(filename!="" and folder!=""):
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. 원본 PDF 파일을 선택하세요.\n2단계. 이미지 파일을 저장할 폴더를 지정하세요.\n3단계. 실행(이미지로 변환) 버튼을 누르세요!\n4단계. 변환된 이미지 파일을 확인하세요.")
      return

   fn_pb_init(bt_tab2_Run)
   fn_pb_set(10)
   try:
      doc = fitz.open(filename)
      list_tab2.delete(0,END)
      temp = (100-vb_pb.get())/len(doc)
      
      for i in range(len(doc)):
         page = doc[i]
         img = get_fitz_pixmap_as_pil(page, zoom=2.0)
         imgName = str(folder) + "/" + str(i+1) + ".jpg"
         img.save(imgName, "JPEG")
         list_tab2.insert(END, imgName)
         fn_pb_set(temp)
         
      list_tab2.selection_set(0)
      fn_tab2_showImage(list_tab2)
      messagebox.showinfo("Convert to image","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
   finally:
      fn_pb_exit()

def fn_tab2_showImage(self):
   if list_tab2.size() == 0: return
   filename=str(list_tab2.get(list_tab2.curselection()[0],list_tab2.curselection()[0])[0])
   try:
       img = Image.open(filename)
       lbx = image_label_tab2.winfo_width()
       lby = image_label_tab2.winfo_height()
       img = fit_image_to_label(img, lbx, lby, margin_w=100, margin_h=100)
       image_tab2 = ImageTk.PhotoImage(img)
       image_label_tab2.configure(image=image_tab2, width=375, height=335)
       image_label_tab2.image=image_tab2
   except Exception as e:
       pass

def fn_tab2_folderOpen():
   if lb_tab2_foldername.cget("text") == "": return
   os.startfile(os.path.realpath(lb_tab2_foldername.cget("text")))

def fn_tab2_fileOpen():
   if list_tab2.size()==0: return
   filename=str(list_tab2.get(list_tab2.curselection()[0],list_tab2.curselection()[0])[0])
   os.startfile(os.path.realpath(filename))

def fn_tab2_clear():
   lb_tab2_filename.config(text='')
   lb_tab2_foldername.config(text='')
   list_tab2.delete(0,END)
   image_label_tab2.image=""

# =========================================================
# TAB 3: Convert to Text
# =========================================================
def fn_tab3_setPDFFile():
   global glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)
   fn_tab3_clear()
   lb_tab3_filename.config(text=str(file))

def fn_tab3_setFolder():
   folder=filedialog.askdirectory()
   if folder != "": lb_tab3_foldername.config(text=str(folder))

def fn_tab3_Run():
   filename = lb_tab3_filename.cget("text")
   folder = lb_tab3_foldername.cget("text")
   if not(filename!="" and folder!=""):
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. 원본 PDF 파일을 선택하세요.\n2단계. 텍스트 파일을 저장할 폴더를 지정하세요.\n3단계. 실행(텍스트로 변환) 버튼을 누르세요!\n4단계. 변환된 텍스트 파일을 확인하세요.")
      return
   
   try:
      reader = PdfReader(filename)
      pages = reader.pages
      list_tab3.delete(0,END)
      i = 0
      for page in pages:
         i += 1
         txtName = str(folder) + "/" + str(i) + ".txt"
         text=page.extract_text()
         with open(txtName, "w", encoding='utf-8') as f:
             f.write(text if text else "")
         list_tab3.insert(END, txtName)

      list_tab3.selection_set(0)
      fn_tab3_showText(list_tab3)
      messagebox.showinfo("Convert to text","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
   
def fn_tab3_showText(self):
   if list_tab3.size() == 0: return
   filename=str(list_tab3.get(list_tab3.curselection()[0],list_tab3.curselection()[0])[0])
   with open(filename,"r", errors='ignore', encoding='utf-8') as f:
       text_tab3.delete('1.0',tk.END)
       text_tab3.insert(tk.INSERT,f.read())
   
def fn_tab3_folderOpen():
   if lb_tab3_foldername.cget("text") == "": return
   os.startfile(os.path.realpath(lb_tab3_foldername.cget("text")))

def fn_tab3_fileOpen():
   if list_tab3.size()==0: return
   filename=str(list_tab3.get(list_tab3.curselection()[0],list_tab3.curselection()[0])[0])
   os.startfile(os.path.realpath(filename))

def fn_tab3_clear():
   lb_tab3_filename.config(text='')
   lb_tab3_foldername.config(text='')
   list_tab3.delete(0,END)
   text_tab3.delete('1.0',tk.END)

# =========================================================
# TAB 4: Rotate page (Lazy Loading 적용 완료)
# =========================================================
def fn_tab4_setPDFFile():
   global tab4_doc, tab4_rotations, glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)

   try:
      fn_tab4_clear()
      lb_tab4_filename.config(text=str(file))
      
      # PyMuPDF 즉시 로드 (스레드 불필요)
      tab4_doc = fitz.open(file)
      list_tab4.delete(0, END)
      tab4_rotations = [0 for _ in range(len(tab4_doc))]
      
      for i in range(len(tab4_doc)):
         list_tab4.insert(END, str(i+1))

      if len(tab4_doc) > 0:
          list_tab4.selection_set(0)
          fn_tab4_showImage(None)
         
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)

def fn_tab4_Run():
   global tab4_rotations
   filename = lb_tab4_filename.cget("text")
   if not(filename!=""):
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. PDF 파일을 열어주세요.\n2단계. 페이지를 회전(시계/반시계)시키세요.\n3단계. 저장 버튼을 누르세요!\n4단계. 회전된 파일을 확인하세요.")
      return

   pdfReader = PdfReader(filename,"rb")
   pdfWriter = PdfWriter()

   try:
      for pageNo in range(len(pdfReader.pages)):
         page = pdfReader.pages[pageNo]
         page.rotate(90 * tab4_rotations[pageNo])
         pdfWriter.add_page(page)
   
      global glb_open_file_path
      savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='rotate.pdf')
      if savefile=="": return
      if savefile[-3:].upper() != "PDF": savefile += ".pdf"

      if myCHK.get()==1 and len(myPWD.get()) > 0 :
          pdfWriter.encrypt(myPWD.get())
            
      pdfWriter.write(savefile)
      lb_tab4_savefile.config(text=savefile)
      messagebox.showinfo("Rotate page(s)","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
   
def fn_tab4_showImage(self):
   global tab4_doc, tab4_rotations
   if list_tab4.size() == 0 or tab4_doc is None: return

   try:
      idx = int(list_tab4.curselection()[0])
      lb_tab4_PNO.config(text=idx+1)
      
      # 즉석 렌더링
      page = tab4_doc[idx]
      img = get_fitz_pixmap_as_pil(page)
      
      # 회전 적용
      rot = tab4_rotations[idx]
      for _ in range(rot):
          img = img.transpose(method=Image.Transpose.ROTATE_90)

      lbx = image_label_tab4.winfo_width()
      lby = image_label_tab4.winfo_height()
      img = fit_image_to_label(img, lbx, lby)

      image_tab4 = ImageTk.PhotoImage(img)
      image_label_tab4.configure(image=image_tab4, width=375, height=335)
      image_label_tab4.image=image_tab4
   except Exception as e:
       pass

def fn_tab4_CW():
   global tab4_rotations
   pno = lb_tab4_PNO.cget("text")
   if pno !="":
      idx = int(pno)-1
      tab4_rotations[idx] = (tab4_rotations[idx] + 1) % 4
      fn_tab4_showImage(None)

def fn_tab4_CCW():
   global tab4_rotations
   pno = lb_tab4_PNO.cget("text")
   if pno !="":
      idx = int(pno)-1
      tab4_rotations[idx] = 3 if tab4_rotations[idx] == 0 else tab4_rotations[idx] - 1
      fn_tab4_showImage(None)

def fn_tab4_folderOpen():
   filename=str(lb_tab4_savefile.cget("text"))
   if filename != "": os.startfile(os.path.dirname(filename))

def fn_tab4_fileOpen():
   filename=str(lb_tab4_savefile.cget("text"))
   if filename!="": os.startfile(os.path.realpath(filename))

def fn_tab4_clear():
   global tab4_doc
   tab4_doc = None
   lb_tab4_filename.config(text='')
   lb_tab4_savefile.config(text='')
   lb_tab4_PNO.config(text='')
   list_tab4.delete(0,END)
   image_label_tab4.image=""

# =========================================================
# TAB 5: Reorder pages (Lazy Loading 적용 완료)
# =========================================================
def fn_tab5_setPDFFile():
   global tab5_doc, glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)

   try:
      fn_tab5_clear()
      lb_tab5_filename.config(text=str(file))
      
      tab5_doc = fitz.open(file)
      list_tab5.delete(0,END)
         
      for i in range(len(tab5_doc)):
         list_tab5.insert(END, str(i+1))
            
      if len(tab5_doc) > 0:
          list_tab5.selection_set(0)
          fn_tab5_showImage(None)
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)

def fn_tab5_Run():
   filename = lb_tab5_filename.cget("text")
   if not(filename!="") or list_R_tab5.size() == 0:
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. PDF 파일을 열어주세요.\n2단계. 페이지 순서를 재정렬하세요.\n3단계. 저장 버튼을 누르세요! (필요시 비밀번호 설정 가능)\n4단계. 정렬된 파일을 확인하세요.")
      return
   
   pdfReader = PdfReader(filename,"rb")
   pdfWriter = PdfWriter()

   try:
      for pageNo in range(list_R_tab5.size()):
         page = pdfReader.pages[int(list_R_tab5.get(pageNo))-1]
         pdfWriter.add_page(page)
   
      global glb_open_file_path
      savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='reorder.pdf')
      if savefile=="": return
      if savefile[-3:].upper() != "PDF": savefile += ".pdf"

      if myCHK.get()==1 and len(myPWD.get()) > 0:
          pdfWriter.encrypt(myPWD.get())
            
      pdfWriter.write(savefile)
      lb_tab5_savefile.config(text=savefile)
      messagebox.showinfo("Reorder pages","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
   
def fn_tab5_showImage(self):
   global tab5_doc
   if list_tab5.size() == 0 or tab5_doc is None: return

   idx=int(list_tab5.curselection()[0])
   lb_tab5_PNO.config(text=idx+1)
   lb_tab5_PLR.config(text='L')
   
   page = tab5_doc[idx]
   img = get_fitz_pixmap_as_pil(page)

   lbx = image_label_tab5.winfo_width()
   lby = image_label_tab5.winfo_height()
   img = fit_image_to_label(img, lbx, lby)

   image_tab5 = ImageTk.PhotoImage(img)
   image_label_tab5.configure(image=image_tab5, width=375, height=335)
   image_label_tab5.image=image_tab5

def fn_R_tab5_showImage(self):
   global tab5_doc
   if list_R_tab5.size() == 0 or tab5_doc is None:
      image_label_tab5.image=""
      lb_tab5_PLR.config(text='')
      lb_tab5_PNO.config(text='')
      return

   idx = int(list_R_tab5.curselection()[0])
   orig_idx = int(list_R_tab5.get(idx)) - 1
   
   lb_tab5_PNO.config(text=idx+1)
   lb_tab5_PLR.config(text='R')
   
   page = tab5_doc[orig_idx]
   img = get_fitz_pixmap_as_pil(page)

   lbx = image_label_tab5.winfo_width()
   lby = image_label_tab5.winfo_height()
   img = fit_image_to_label(img, lbx, lby)

   image_tab5 = ImageTk.PhotoImage(img)
   image_label_tab5.configure(image=image_tab5, width=375, height=335)
   image_label_tab5.image=image_tab5

def fn_tab5_folderOpen():
   filename=str(lb_tab5_savefile.cget("text"))
   if filename != "": os.startfile(os.path.dirname(filename))

def fn_tab5_fileOpen():
   filename=str(lb_tab5_savefile.cget("text"))
   if filename!="": os.startfile(os.path.realpath(filename))

def fn_tab5_clear():
   global tab5_doc
   tab5_doc = None
   lb_tab5_filename.config(text='')
   lb_tab5_savefile.config(text='')
   lb_tab5_PLR.config(text='')
   lb_tab5_PNO.config(text='')
   list_tab5.delete(0,END)
   list_R_tab5.delete(0,END)
   image_label_tab5.image=""

def fn_tab5_chk():
   if myCHK.get() == 1: text_tab5.configure(state="normal")
   else:
      text_tab5.delete(0,END)
      text_tab5.configure(state="disabled")

def on_window_resize(event): pass
def closing(): window.destroy()

def fn_tab5_mol():
   selectionR = list_R_tab5.curselection()
   if(len(selectionR) == 0): return
   idxR = selectionR[0]
   list_R_tab5.delete(idxR,idxR)
   if list_R_tab5.size() == idxR: list_R_tab5.selection_set(END)
   else: list_R_tab5.selection_set(idxR)
   fn_R_tab5_showImage(list_R_tab5)

def fn_tab5_mal():
   list_R_tab5.delete(0,END)
   fn_R_tab5_showImage(list_R_tab5)

def fn_tab5_mor():
   selectionL = list_tab5.curselection()
   if(len(selectionL) == 0): return
   idxL = selectionL[0] + 1
   selectionR = list_R_tab5.curselection()
   if(len(selectionR) == 0): list_R_tab5.insert(END, idxL)
   else:
      idxR = selectionR[0] + 1
      list_R_tab5.insert(idxR, idxL)
      list_R_tab5.selection_clear(0, END)
      list_R_tab5.selection_set(idxR)

def fn_tab5_mar():
   list_R_tab5.delete(0,END)
   for R in range(list_tab5.size()): list_R_tab5.insert(END, list_tab5.get(R))

# =========================================================
# TAB 6: Set Watermark (Lazy Loading & Vector Merge)
# =========================================================
def fn_tab6_setPdfFile():
   global tab6_doc, glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)

   try:
       lb_tab6_filename.config(text=str(file))
       tab6_doc = fitz.open(file)
       list_tab6.delete(0,END)
       
       for i in range(len(tab6_doc)):
          list_tab6.insert(END, str(i+1))
          
       if len(tab6_doc) > 0:
           list_tab6.selection_set(0)
           fn_tab6_showImage(None)
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)

def fn_tab6_setWaterMarkFile():
   global tab6_watermark_img, glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])
   if file == "" : return
   glb_open_file_path = os.path.dirname(file)
   lb_tab6_watermarkfilename.config(text=str(file))

   try:
      # 워터마크 첫 페이지만 읽어와서 RGBA 투명 이미지로 변환
      wm_doc = fitz.open(file)
      page = wm_doc[0]
      img = get_fitz_pixmap_as_pil(page, zoom=2.0).convert("RGBA")

      # 하얀 배경 투명화 및 투명도 조절
      datas = img.getdata()
      newData = []
      for item in datas:
         if item[0] > 200 and item[1] > 200 and item[2] > 200:
            newData.append((item[0], item[1], item[2], 0))
         else:
            newData.append((item[0], item[1], item[2], 100))  # 100: 투명도
      img.putdata(newData)
      
      tab6_watermark_img = img
      
      if list_tab6.size() > 0:
          fn_tab6_showImage(None)

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)

def fn_tab6_showImage(self):
   global tab6_doc, tab6_watermark_img
   if list_tab6.size() == 0 or tab6_doc is None: return

   idx = int(list_tab6.curselection()[0])
   lb_tab6_PNO.config(text=idx+1)
   
   # 원본 문서 페이지 즉석 렌더링
   page = tab6_doc[idx]
   img = get_fitz_pixmap_as_pil(page).convert("RGBA")

   # 워터마크 합성 (미리보기 용도)
   if tab6_watermark_img is not None:
       wm_resized = tab6_watermark_img.resize(img.size)
       img = Image.alpha_composite(img, wm_resized)

   lbx = image_label_tab6.winfo_width()
   lby = image_label_tab6.winfo_height()
   img = fit_image_to_label(img, lbx, lby)

   image_tab6 = ImageTk.PhotoImage(img)
   image_label_tab6.configure(image=image_tab6, width=375, height=335)
   image_label_tab6.image=image_tab6

def fn_tab6_listPageNo(self):
   fn_tab6_showImage(self)

def fn_tab6_Save():
   pdfFile = lb_tab6_filename.cget("text")
   watermarkFile = lb_tab6_watermarkfilename.cget("text")
                                                  
   if not(pdfFile!="" and watermarkFile!=""):
      messagebox.showinfo(VERSION,"사용 방법\n\n1단계. 원본 PDF 파일을 설정하세요.\n2단계. 워터마크 PDF 파일을 설정하세요. (첫 페이지가 워터마크로 사용됩니다)\n3단계. 저장 버튼을 누르세요!\n4단계. 결과 파일을 확인하세요.")
      return

   global glb_open_file_path
   savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='watermark.pdf')
   if savefile=="": return
   if savefile[-3:].upper() != "PDF": savefile += ".pdf"

   # 백터 머지 방식으로 저장 속도/화질 보장
   try:
      with open(pdfFile,"rb") as input_file, open(watermarkFile,"rb") as wm_file:
         input_pdf = PdfReader(input_file)
         watermark_pdf = PdfReader(wm_file)
         watermark_page = watermark_pdf.pages[0]
         
         output = PdfWriter()
         for i in range(len(input_pdf.pages)):
            pdf_page = input_pdf.pages[i]
            pdf_page.merge_page(watermark_page)
            output.add_page(pdf_page)
            
         with open(savefile, "wb") as merged_file:
            output.write(merged_file)
            
      lb_tab6_savefile.config(text=savefile)
      messagebox.showinfo("Set Watermark","성공적으로 완료되었습니다.")
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)

def fn_tab6_folderOpen():
   filename=str(lb_tab6_savefile.cget("text"))
   if filename != "": os.startfile(os.path.dirname(filename))

def fn_tab6_fileOpen():
   filename=str(lb_tab6_savefile.cget("text"))
   if filename!="": os.startfile(os.path.realpath(filename))

def fn_tab6_clear():
   global tab6_doc, tab6_watermark_img
   tab6_doc = None
   tab6_watermark_img = None
   lb_tab6_filename.config(text='')
   lb_tab6_watermarkfilename.config(text='')
   list_tab6.delete(0,END)
   image_label_tab6.image=""
   lb_tab6_PNO.config(text='')
   lb_tab6_savefile.config(text='')

# ---------------------------------------------------------
# 메뉴 및 UI 구성 
# ---------------------------------------------------------
menubar = Menu(window)
helpmenu = Menu(menubar, tearoff=0)
menubar.add_command(label="About", command=donothing)
menubar.add_command(label="Message", command=showSystemMessage)
window.config(menu=menubar)

style = tkinter.ttk.Style(window)
style.theme_use('default')
style.configure('TNotebook.Tab', foreground="white", background="gray", width=window.winfo_screenwidth(), font=('Calibri','15','bold'), anchor="c")
style.map("TNotebook.Tab", foreground=[("selected", "gray")], background=[("selected", "white")], font=[("selected",("Calibri","15", "bold"))])

tabs=tkinter.ttk.Notebook() 
tabs.grid(row=0,column=0, sticky='nsew')

tab1=tk.Frame(tabs)
tab2=tk.Frame(tabs)
tab3=tk.Frame(tabs)
tab4=tk.Frame(tabs)
tab5=tk.Frame(tabs)
tab6=tk.Frame(tabs)
tab7=tk.Frame(tabs)

tabs.add(tab1, text="Merge files")
tabs.add(tab2, text="Convert to image")
tabs.add(tab3, text="Convert to text")
tabs.add(tab4, text="Rotate page")
tabs.add(tab5, text="Reorder pages")
tabs.add(tab6, text="Set Watermark")
tabs.add(tab7, text="System message")

tk.Grid.rowconfigure(window, 0, weight=1)
tk.Grid.columnconfigure(window, 0, weight=1)
tabs.grid(column=0, row=0, padx=1, pady=0, sticky="news")
tabs.hide(6)

style = tkinter.ttk.Style(window)
style.layout('text.Horizontal.TProgressbar', [('Horizontal.Progressbar.trough', {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})], 'sticky': 'nswe'}), ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')

vb_pb = DoubleVar()
pb = tkinter.ttk.Progressbar(tabs, maximum = 100, variable=vb_pb, mode="determinate", style="text.Horizontal.TProgressbar")
pb.config(length=0)

# =========================================================
# TAB 1 Layout
# =========================================================
bt_fileadd = tk.Button(tab1, text='Add Files', relief="groove", overrelief="solid", command=fn_fileAdd, width=10)
bt_fileadd.grid(row=0, column=0, pady=2, sticky=W+E+N+S)
bt_filedel = tk.Button(tab1, text='Delete File', relief="groove", overrelief="solid", command=fn_fileDel, width=10)
bt_filedel.grid(row=0, column=1, pady=2,  sticky=W+E+N+S)
bt_filedelAll = tk.Button(tab1, text='Delete All Files', relief="groove", overrelief="solid", command=fn_filedelAll, width=10)
bt_filedelAll.grid(row=0, column=2, pady=2,  sticky=W+E+N+S)
bt_filedown = tk.Button(tab1, text='▽', relief="groove", overrelief="solid", command=fn_fileDown, width=10)
bt_filedown.grid(row=0, column=3, pady=2,  sticky=W+E+N+S)
bt_fileup = tk.Button(tab1, text='△', relief="groove", overrelief="solid", command=fn_fileUp, width=10)
bt_fileup.grid(row=0, column=4, pady=2, sticky=W+E+N+S)

style = tkinter.ttk.Style()
style.configure("mystyle.Treeview", font=('Calibri', 11,'normal')) 
style.configure("mystyle.Treeview.Heading", font=('Calibri', 12,'normal'), relief='ridge') 

tab1_tree = tkinter.ttk.Treeview(tab1, style="mystyle.Treeview", selectmode = "browse", show="headings")
tab1_tree.grid(row=1, column=0, columnspan=5, padx=2, pady=2, sticky="nsew")
tab1_tree['columns'] = ("Name", "Size", "Update")
tab1_tree.column("Name", anchor = W, width=480, minwidth = 100)
tab1_tree.column("Size", anchor = E, width=40, minwidth = 20)
tab1_tree.column("Update", anchor = CENTER, width=40, minwidth = 20)
tab1_tree.heading("Name", text="File Name", anchor=CENTER)
tab1_tree.heading("Size", text="File Size", anchor = CENTER)
tab1_tree.heading("Update", text="Update date", anchor = CENTER)

bt_filemerge = tk.Button(tab1, text='Save', relief="groove", overrelief="solid", command=fn_tab1_Run)
bt_filemerge.grid(row=2, column=0, columnspan=5, padx=1, pady=2, sticky=W+E+N+S)
lb_MergedFile = tk.Label(tab1, height=1, bg="gray", font=('consolas',12,'bold'), fg="white", anchor="w")
lb_MergedFile.grid(row=3, column=0, columnspan=5, padx=2, pady=0, sticky=W+E+N+S)
bt_fileOpen = tk.Button(tab1, text='Open File', relief="groove", overrelief="solid", command=fn_fileOpen, width=10)
bt_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_folderOpen = tk.Button(tab1, text='Open Folder', relief="groove", overrelief="solid", command=fn_folderOpen, width=10)
bt_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_clear = tk.Button(tab1, text='Clear Screen', relief="groove", overrelief="solid", command=fn_clear, width=10)
bt_clear.grid(row=4, column=2, columnspan=3, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab1, 0, weight=0); Grid.rowconfigure(tab1, 1, weight=1); Grid.rowconfigure(tab1, 2, weight=0); Grid.rowconfigure(tab1, 3, weight=0); Grid.rowconfigure(tab1, 4, weight=0)
Grid.columnconfigure(tab1, 0, weight=1); Grid.columnconfigure(tab1, 1, weight=1); Grid.columnconfigure(tab1, 2, weight=1); Grid.columnconfigure(tab1, 3, weight=1); Grid.columnconfigure(tab1, 4, weight=1)

# =========================================================
# TAB 2 Layout
# =========================================================
bt_tab2_setPDFFile = tk.Button(tab2, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab2_setPDFFile)
bt_tab2_setPDFFile.grid(row=0, column=0, pady=2, sticky=W+E+N+S)
lb_tab2_filename = tk.Label(tab2, height=1, bg="white", font=('consolas',9,'normal'), fg="black", width=81, anchor="w")
lb_tab2_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)
bt_tab2_setFolder = tk.Button(tab2, text='Set Save Folder', relief="groove", overrelief="solid", command=fn_tab2_setFolder)
bt_tab2_setFolder.grid(row=1, column=0, pady=2, sticky=W+E+N+S)
lb_tab2_foldername = tk.Label(tab2, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab2_foldername.grid(row=1, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)
bt_tab2_Run = tk.Button(tab2, text='Run (Convert to image)', relief="groove", overrelief="solid", command=fn_tab2_Run)
bt_tab2_Run.grid(row=2, column=0, columnspan=4, padx=1, pady=2, sticky=W+E+N+S)

list_tab2 = Listbox(tab2, width=30, height=21, activestyle="none", exportselection=False)
list_tab2.grid(row=3, column=0, padx=2, pady=2, sticky=W+E+S+N)
list_tab2.bind('<<ListboxSelect>>', fn_tab2_showImage)
list_tab2_sb = tk.Scrollbar(tab2, orient="vertical", command=list_tab2.yview)
list_tab2_sb.grid(row=3, column=0, padx=4, pady=4, sticky=N+S+E)
list_tab2.configure(yscrollcommand=list_tab2_sb.set)

image_label_tab2 = tk.Label(tab2, bg="gray")
image_label_tab2.grid(row=3, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
image_label_tab2.bind("<Configure>", on_window_resize)

bt_tab2_fileOpen = tk.Button(tab2, text='Open File', relief="groove", overrelief="solid", command=fn_tab2_fileOpen, width=30)
bt_tab2_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_tab2_folderOpen = tk.Button(tab2, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab2_folderOpen, width=30)
bt_tab2_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_tab2_clear = tk.Button(tab2, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab2_clear)
bt_tab2_clear.grid(row=4, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab2, 0, weight=0); Grid.rowconfigure(tab2, 1, weight=0); Grid.rowconfigure(tab2, 2, weight=0); Grid.rowconfigure(tab2, 3, weight=1); Grid.rowconfigure(tab2, 4, weight=0)
Grid.columnconfigure(tab2, 0, weight=0); Grid.columnconfigure(tab2, 1, weight=0); Grid.columnconfigure(tab2, 2, weight=1); Grid.columnconfigure(tab2, 3, weight=1)

# =========================================================
# TAB 3 Layout
# =========================================================
bt_tab3_setPDFFile = tk.Button(tab3, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab3_setPDFFile)
bt_tab3_setPDFFile.grid(row=0, column=0, pady=2, sticky=W+E+N+S)
lb_tab3_filename = tk.Label(tab3, height=1, bg="white", font=('consolas',9,'normal'), fg="black", width=81, anchor="w")
lb_tab3_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)
bt_tab3_setFolder = tk.Button(tab3, text='Set Save Folder', relief="groove", overrelief="solid", command=fn_tab3_setFolder)
bt_tab3_setFolder.grid(row=1, column=0, pady=2, sticky=W+E+N+S)
lb_tab3_foldername = tk.Label(tab3, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab3_foldername.grid(row=1, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)
bt_tab3_Run = tk.Button(tab3, text='Run (Convert to text)', relief="groove", overrelief="solid", command=fn_tab3_Run)
bt_tab3_Run.grid(row=2, column=0, columnspan=4, padx=1, pady=2, sticky=W+E+S+N)

list_tab3 = Listbox(tab3, width=30, height=21, activestyle="none", exportselection=False)
list_tab3.grid(row=3, column=0, padx=2, pady=2, sticky=W+E+S+N)
list_tab3.bind('<<ListboxSelect>>', fn_tab3_showText)
list_tab3_sb = tk.Scrollbar(tab3, orient="vertical", command=list_tab3.yview)
list_tab3_sb.grid(row=3, column=0, padx=4, pady=4, sticky=N+S+E)
list_tab3.configure(yscrollcommand=list_tab3_sb.set)

text_tab3 = scrolledtext.ScrolledText(tab3, wrap=tk.WORD, width=52)
text_tab3.grid(row=3, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
text_tab3.config(font=("'Malgun Gothic', Consolas, 'Courier New', monospace", 11, 'normal'), spacing1=3, spacing2=3, spacing3=3)
bt_tab3_fileOpen = tk.Button(tab3, text='Open File', relief="groove", overrelief="solid", command=fn_tab3_fileOpen, width=30)
bt_tab3_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_tab3_folderOpen = tk.Button(tab3, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab3_folderOpen, width=30)
bt_tab3_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_tab3_clear = tk.Button(tab3, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab3_clear, width=54)
bt_tab3_clear.grid(row=4, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab3, 0, weight=0); Grid.rowconfigure(tab3, 1, weight=0); Grid.rowconfigure(tab3, 2, weight=0); Grid.rowconfigure(tab3, 3, weight=1); Grid.rowconfigure(tab3, 4, weight=0)
Grid.columnconfigure(tab3, 0, weight=0); Grid.columnconfigure(tab3, 1, weight=0); Grid.columnconfigure(tab3, 2, weight=1); Grid.columnconfigure(tab3, 3, weight=1)

# =========================================================
# TAB 4 Layout
# =========================================================
bt_tab4_setPDFFile = tk.Button(tab4, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab4_setPDFFile)
bt_tab4_setPDFFile.grid(row=0, column=0, pady=4, sticky=W+E+N+S)
lb_tab4_filename = tk.Label(tab4, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab4_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=4, sticky=W+E+N+S)

list_tab4 = Listbox(tab4, width=30, height=21, activestyle="none", exportselection=False, justify="center")
list_tab4.grid(row=1, column=0, padx=2, pady=2, sticky=W+E+S+N)
list_tab4.bind('<<ListboxSelect>>', fn_tab4_showImage)
list_tab4_sb = tk.Scrollbar(tab4, orient="vertical", command=list_tab4.yview)
list_tab4_sb.grid(row=1, column=0, padx=4, pady=4, sticky=N+S+E)
list_tab4.configure(yscrollcommand=list_tab4_sb.set)

image_label_tab4 = tk.Label(tab4, bg="gray")
image_label_tab4.grid(row=1, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
image_label_tab4.bind("<Configure>", on_window_resize)

bt_tab4_CW = tk.Button(tab4, text='CW', fg="white", bg="gray", font=('consolas',10,'bold'), relief="groove", overrelief="solid", width=5, height=2, command=fn_tab4_CW)
bt_tab4_CW.grid(row=1, column=1, padx=10, pady=2, sticky=W)
bt_tab4_CCW = tk.Button(tab4, text='CCW', fg="white", bg="gray", font=('consolas',10,'bold'), relief="groove", overrelief="solid", width=5, height=2, command=fn_tab4_CCW)
bt_tab4_CCW.grid(row=1, column=3, padx=10, pady=2, sticky=E)

lb_tab4_PNO = tk.Label(tab4, height=1, bg="gray", font=('consolas',40,'bold'), fg="black", anchor="w")
lb_tab4_PNO.grid(row=1, column=3, padx=10, pady=10, sticky=E+N)

bt_tab4_Run = tk.Button(tab4, text='Save', relief="groove", overrelief="solid", command=fn_tab4_Run)
bt_tab4_Run.grid(row=2, column=0, columnspan=4, padx=1, pady=2, sticky=W+E+S+N)
lb_tab4_savefile = tk.Label(tab4, height=1, bg="gray", font=('consolas',12,'bold'), fg="white", anchor="w")
lb_tab4_savefile.grid(row=3, column=0, columnspan=4, padx=2, pady=0, sticky=W+E+N+S)
bt_tab4_fileOpen = tk.Button(tab4, text='Open File', relief="groove", overrelief="solid", command=fn_tab4_fileOpen, width=30)
bt_tab4_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_tab4_folderOpen = tk.Button(tab4, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab4_folderOpen, width=30)
bt_tab4_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_tab4_clear = tk.Button(tab4, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab4_clear)
bt_tab4_clear.grid(row=4, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab4, 0, weight=0); Grid.rowconfigure(tab4, 1, weight=1); Grid.rowconfigure(tab4, 2, weight=0); Grid.rowconfigure(tab4, 3, weight=0); Grid.rowconfigure(tab4, 4, weight=0)
Grid.columnconfigure(tab4, 0, weight=0); Grid.columnconfigure(tab4, 1, weight=0); Grid.columnconfigure(tab4, 2, weight=1); Grid.columnconfigure(tab4, 3, weight=1)

# =========================================================
# TAB 5 Layout
# =========================================================
bt_tab5_setPDFFile = tk.Button(tab5, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab5_setPDFFile, width=30)
bt_tab5_setPDFFile.grid(row=0, column=0, pady=4, sticky=W+E+N+S)
lb_tab5_filename = tk.Label(tab5, height=1, bg="white", font=('consolas',9,'normal'), fg="black", width=81, anchor="w")
lb_tab5_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=4, sticky=W+E+N+S)

frm_left_tab5 = tk.Frame(tab5, width=30)
frm_left_tab5.grid(row=1, column=0, padx=0, pady=0, sticky=W+E+N+S)
list_tab5 = Listbox(frm_left_tab5, width=12, height=21, activestyle="none", exportselection=False, justify="center")
list_tab5.grid(row=0, column=0, rowspan=4, padx=2, pady=2, sticky=W+E+S+N)
list_tab5.bind('<<ListboxSelect>>', fn_tab5_showImage)
list_tab5_sb = tk.Scrollbar(frm_left_tab5, orient="vertical", command=list_tab5.yview)
list_tab5_sb.grid(row=0, column=0, rowspan=4, padx=4, pady=4, sticky=N+S+E)
list_tab5.configure(yscrollcommand=list_tab5_sb.set)

bt_tab5_MOR = tk.Button(frm_left_tab5, text='>', relief="groove", overrelief="solid", command=fn_tab5_mor)
bt_tab5_MOR.grid(row=0, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)
bt_tab5_MAR = tk.Button(frm_left_tab5, text='>>', relief="groove", overrelief="solid", command=fn_tab5_mar)
bt_tab5_MAR.grid(row=1, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)
bt_tab5_MOL = tk.Button(frm_left_tab5, text='<', relief="groove", overrelief="solid", command=fn_tab5_mol)
bt_tab5_MOL.grid(row=2, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)
bt_tab5_MAL = tk.Button(frm_left_tab5, text='<<', relief="groove", overrelief="solid", command=fn_tab5_mal)
bt_tab5_MAL.grid(row=3, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)

list_R_tab5 = Listbox(frm_left_tab5, width=12, height=21, activestyle="none", exportselection=False, justify="center")
list_R_tab5.grid(row=0, column=2, rowspan=4, padx=2, pady=2, sticky=W+E+S+N)
list_R_tab5.bind('<<ListboxSelect>>', fn_R_tab5_showImage)
list_R_tab5_sb = tk.Scrollbar(frm_left_tab5, orient="vertical", command=list_R_tab5.yview)
list_R_tab5_sb.grid(row=0, column=2, rowspan=4, padx=4, pady=4, sticky=N+S+E)
list_R_tab5.configure(yscrollcommand=list_R_tab5_sb.set)

Grid.rowconfigure(frm_left_tab5, 0, weight=1); Grid.rowconfigure(frm_left_tab5, 1, weight=1); Grid.rowconfigure(frm_left_tab5, 2, weight=1); Grid.rowconfigure(frm_left_tab5, 3, weight=1)
Grid.columnconfigure(frm_left_tab5, 0, weight=1); Grid.columnconfigure(frm_left_tab5, 1, weight=0); Grid.columnconfigure(frm_left_tab5, 2, weight=1)

image_label_tab5 = tk.Label(tab5, bg="gray")
image_label_tab5.grid(row=1, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
image_label_tab5.bind("<Configure>", on_window_resize)

lb_tab5_PLR = tk.Label(tab5, height=1, bg="gray", font=('consolas',40,'bold'), fg="black", anchor="w")
lb_tab5_PLR.grid(row=1, column=1, padx=10, pady=10, sticky=W+N)
lb_tab5_PNO = tk.Label(tab5, height=1, bg="gray", font=('consolas',40,'bold'), fg="black", anchor="w")
lb_tab5_PNO.grid(row=1, column=3, padx=10, pady=10, sticky=E+N)

frm_tab5 = tk.Frame(tab5, width=10)
frm_tab5.grid(row=2, column=0, padx=1, pady=2, sticky=W+E+N+S)

myCHK = IntVar()
myPWD = StringVar()
chk_passwd=tk.Checkbutton(frm_tab5, text="PWD", variable=myCHK, command=fn_tab5_chk)
chk_passwd.grid(row=0, column=0, columnspan=1, padx=2, pady=0, sticky=W+N+S)
text_tab5 = tk.Entry(frm_tab5, font=('consolas',10,'normal'), bd=1, relief="solid", width=2, show="*", textvariable = myPWD, state="disabled")
text_tab5.grid(row=0, column=1, columnspan=1, padx=2, pady=1, sticky=W+E+N+S)

Grid.rowconfigure(frm_tab5, 0, weight=1); Grid.columnconfigure(frm_tab5, 0, weight=0); Grid.columnconfigure(frm_tab5, 1, weight=1)

bt_tab5_Run = tk.Button(tab5, text='Save', relief="groove", overrelief="solid", command=fn_tab5_Run)
bt_tab5_Run.grid(row=2, column=1, columnspan=3, padx=1, pady=2, sticky=W+E+S+N)
lb_tab5_savefile = tk.Label(tab5, height=1, bg="gray", font=('consolas',12,'bold'), fg="white", anchor="w")
lb_tab5_savefile.grid(row=3, column=0, columnspan=4, padx=2, pady=0, sticky=W+E+N+S)
bt_tab5_fileOpen = tk.Button(tab5, text='Open File', relief="groove", overrelief="solid", command=fn_tab5_fileOpen, width=30)
bt_tab5_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_tab5_folderOpen = tk.Button(tab5, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab5_folderOpen, width=30)
bt_tab5_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_tab5_clear = tk.Button(tab5, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab5_clear)
bt_tab5_clear.grid(row=4, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab5, 0, weight=0); Grid.rowconfigure(tab5, 1, weight=1); Grid.rowconfigure(tab5, 2, weight=0); Grid.rowconfigure(tab5, 3, weight=0); Grid.rowconfigure(tab5, 4, weight=0)
Grid.columnconfigure(tab5, 0, weight=0); Grid.columnconfigure(tab5, 1, weight=0); Grid.columnconfigure(tab5, 2, weight=1); Grid.columnconfigure(tab5, 3, weight=1)

# =========================================================
# TAB 6 Layout
# =========================================================
bt_tab6_watermarkfilename = tk.Button(tab6, text='Set Watermark PDF File', relief="groove", overrelief="solid", command=fn_tab6_setWaterMarkFile)
bt_tab6_watermarkfilename.grid(row=0, column=0, pady=2, sticky=W+E+N+S)
lb_tab6_watermarkfilename = tk.Label(tab6, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab6_watermarkfilename.grid(row=0, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)

bt_tab6_setPDFFile = tk.Button(tab6, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab6_setPdfFile) 
bt_tab6_setPDFFile.grid(row=1, column=0, pady=2, sticky=W+E+N+S)
lb_tab6_filename = tk.Label(tab6, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab6_filename.grid(row=1, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)

list_tab6 = Listbox(tab6, width=30, height=21, activestyle="none", exportselection=False, justify="center")
list_tab6.grid(row=2, column=0, padx=2, pady=2, sticky=W+E+S+N)
list_tab6.bind('<<ListboxSelect>>', fn_tab6_listPageNo)
list_tab6_sb = tk.Scrollbar(tab6, orient="vertical", command=list_tab6.yview)
list_tab6_sb.grid(row=2, column=0, padx=4, pady=4, sticky=N+S+E)
list_tab6.configure(yscrollcommand=list_tab6_sb.set)

image_label_tab6 = tk.Label(tab6, bg="gray")
image_label_tab6.grid(row=2, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
image_label_tab6.bind("<Configure>", on_window_resize)

lb_tab6_PNO = tk.Label(tab6, height=1, bg="gray", font=('consolas',40,'bold'), fg="black", anchor="w")
lb_tab6_PNO.grid(row=2, column=3, padx=10, pady=10, sticky=E+N)

bt_tab6_Save = tk.Button(tab6, text='Save', relief="groove", overrelief="solid", command=fn_tab6_Save)
bt_tab6_Save.grid(row=3, column=0, columnspan=4, padx=1, pady=2, sticky=W+E+S+N)
lb_tab6_savefile = tk.Label(tab6, height=1, bg="gray", font=('consolas',12,'bold'), fg="white", anchor="w")
lb_tab6_savefile.grid(row=4, column=0, columnspan=4, padx=2, pady=0, sticky=W+E+N+S)

bt_tab6_fileOpen = tk.Button(tab6, text='Open File', relief="groove", overrelief="solid", command=fn_tab6_fileOpen, width=30)
bt_tab6_fileOpen.grid(row=5, column=0, padx=1, pady=2, sticky=W+E+N+S)
bt_tab6_folderOpen = tk.Button(tab6, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab6_folderOpen, width=30)
bt_tab6_folderOpen.grid(row=5, column=1, padx=1, pady=2, sticky=W+E+N+S)
bt_tab6_clear = tk.Button(tab6, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab6_clear)
bt_tab6_clear.grid(row=5, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)

Grid.rowconfigure(tab6, 0, weight=0); Grid.rowconfigure(tab6, 1, weight=0); Grid.rowconfigure(tab6, 2, weight=1); Grid.rowconfigure(tab6, 3, weight=0); Grid.rowconfigure(tab6, 4, weight=0); Grid.rowconfigure(tab6, 5, weight=0)
Grid.columnconfigure(tab6, 0, weight=0); Grid.columnconfigure(tab6, 1, weight=0); Grid.columnconfigure(tab6, 2, weight=0); Grid.columnconfigure(tab6, 3, weight=1)

# =========================================================
# TAB 7 Layout
# =========================================================
text_tab7 = scrolledtext.ScrolledText(tab7, wrap=tk.WORD)
text_tab7.grid(row=0, column=0, padx=2, pady=2, sticky=W+E+S+N)
text_tab7.config(font=("Consolas, 'Courier New', monospace", 12, 'bold'), bg="#222222", fg="#DDDDDD") 
Grid.rowconfigure(tab7, 0, weight=1); Grid.columnconfigure(tab7, 0, weight=1)

# ---------------------------------------------------------
# 스킨 적용 및 앱 실행
# ---------------------------------------------------------
def apply_skin(widget):
   def apply_widget_skin(w):
      new_font = font.Font(family="Spoqa Han Sans Neo Regular", size=11)
      if isinstance(widget, (tk.Menu, tk.Frame, tk.Scrollbar)): w.configure(font=new_font)
      elif isinstance(w, (tk.Label, tk.Button, tk.Entry)): w.configure(font=new_font)
      elif isinstance(w, tkinter.ttk.Treeview):
         style = tkinter.ttk.Style()
         style.configure("mystyle.Treeview", font=('Spoqa Han Sans Neo Regular', 11,'normal'))
         style.configure("mystyle.Treeview.Heading", font=('Spoqa Han Sans Neo Regular', 11,'normal'), relief='ridge')
      for child in w.winfo_children(): apply_widget_skin(child)
   apply_widget_skin(widget)
   
window.mainloop()
