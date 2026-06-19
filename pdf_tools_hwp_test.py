##
## pip install PyPDF2
## pip install pdf2image
##    : pdf2image needs poppler
##       => https://github.com/oschwartz10612/poppler-windows/releases/
##       ==> XXXX : set env PATH .../Library/bin

## pip install img2pdf

## pip install pyinstaller

## pip install pycryptodome
##

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext

import tkinter as tk
import tkinter.ttk

from collections import Counter
import os
import math
import sys
import tempfile


from Crypto.Cipher import AES

import PyPDF2
from PyPDF2 import Transformation
from PyPDF2 import PdfMerger
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter

import pdf2image
from pdf2image import convert_from_path
import img2pdf

from PIL import Image, ImageTk, ImageEnhance
Image.MAX_IMAGE_PIXELS = None

import traceback

from time import time
from time import ctime

from datetime import datetime

from pathlib import Path

global VERSION
VERSION ="V.0.5.5"

global tab4_images_array
tab4_images_arrary=[]
global tab4_images


global tab6_images_array
tab6_images_arrary=[]
global tab6_sum_images
global tab6_pdf_images
global tab6_watermark_image

global cfp_lib_path
cfp_lib_path = "./lib/poppler-24.07.0/Library/bin"


global glb_open_file_path
glb_open_file_path = "."


window = tk.Tk()
window.option_add("*Font", "Calibri 11")


#window.lift()
##window.wm_attributes("-topmost", True) ## modal
#window.wait_visibility()

window.title("PDF 도구(" + VERSION + ")")

screen_w = window.winfo_screenwidth()
screen_h = window.winfo_screenheight()

app_w = 1100
app_h = screen_h - 110

x = int((screen_w-app_w)/2) 
y = 10 ##int((screen_h-app_h)/2) 


window.geometry(f"{app_w}x{app_h}+{x}+{y}")
##window.option_add("*Font", "consolas")

window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

#window.resizable(False, False)
window.resizable(True, True)
window.minsize(app_w, app_h)

## window.wm_attributes("-transparentcolor", "red")  # red을 투명하게 구현

def resource_path(relative_path):
   base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
   return os.path.join(base_path, relative_path)


window.iconbitmap(resource_path("./icon.ico"))



def fn_pb_init(obj):
   window.config(cursor="circle")  #heart
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


   
#################################################
def donothing():
   messagebox.showinfo(VERSION,"[editor] \t Kim Seon Je \n\n\t ancestor@korea.kr \n\n\t tkf.fkd.gk.wk@gmail.com")


   
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

   text_tab7.tag_config('body', foreground='#DDDDDD')  # <-- Change colors of texts tagged `body`
   text_tab7.tag_config('time', foreground='yellow')   # <-- Change colors of texts tagged `time`
   text_tab7.see("end")
   

def fn_fileAdd():
   global glb_open_file_path
   list_file = []
   files = filedialog.askopenfilenames(initialdir = glb_open_file_path, title="select PDF or HWP files", filetypes=[("pdf files","*.pdf"),("hwp files","*.hwp")])
   
   if files == "" : return

   glb_open_file_path = os.path.dirname(files[0])

   file_extension = os.path.splitext(files[0])[1].lower()

   print(file_extension)
   
   for i in range(len(files)):
      filesize = format(math.ceil(os.path.getsize(files[i])/1000),",") + " KB"

      modified_time = os.path.getmtime(files[i])
      modified_date = datetime.fromtimestamp(modified_time)
      modified_date = modified_date.strftime('%Y-%m-%d %H:%M:%S')

      tab1_tree.insert(parent='', index='end', text='', values=(files[i], filesize, modified_date, file_extension))

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
   for i in leaves:
      tab1_tree.move(i, tab1_tree.parent(i), tab1_tree.index(i)-1)

def fn_fileDown():
   leaves = tab1_tree.selection()
   for i in reversed(leaves):
      tab1_tree.move(i, tab1_tree.parent(i), tab1_tree.index(i)+1)


def fn_clear():
   fn_filedelAll()
   lb_MergedFile.config(text='')


import win32com.client as win32


def fn_tab1_hwptopdf(hwp_file):

   hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
   win32gui.FindWindow(None, "빈 문서 1 - 한글")

   # 한글 프로그램 백그라운드 실행
   hwp.XHwpWindows.Item(0).Visible = False

   # 보안모듈 안 띄우기
   hwp.RegisterModule('FilePathCheckDLL','FileAuto')

   hwp.Open(hwp_file)
   hwp.HAction.GetDefault('FileSaveAsPdf', hwp.HParameterSet.HFileOpenSave.HSet)
   hwp.HParameterSet.HFileOpenSave.filename = hwp_file.replace('.hwp', '.pdf')
   hwp.HParameterSet.HFileOpenSave.Format = 'PDF'
   hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)


   return hwp_file.replace('.hwp', '.pdf')
   
def fn_tab1_Run():

   global hwp
   
   merger = PdfMerger()

   filecnt = len(tab1_tree.get_children())
   
   if filecnt==0:
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Add source files.\n" +
                                  "Step 2. Sort files.\n" +
                                  "Step 3. Save(Merge)!\n" +
                                  "Step 4. Check the file or folder.")
      return
   
   global glb_open_file_path
   filename = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='merged.pdf')

   if filename=="": return
   
   if filename[-3:].upper() != "PDF":
      filename += ".pdf"

   window.update()
   lb_MergedFile.config(text="[merging... " + str(filecnt) + " files]")


   try:
      i = 0
      for row in tab1_tree.get_children():
         fn = tab1_tree.item(row).get('values')[0]
         ft = tab1_tree.item(row).get('values')[3]


         if ft == ".hwp":
            fn=fn_tab1_hwptopdf(fn)

         print(fn)
         merger.append(fn)
         
         lb_MergedFile.config(text="[Merging... " + str(i+1) +"/" + str(filecnt) + "] " + str(round((i/filecnt) * 100,2)) + "%")
         window.update()
         i+=1
         
      lb_MergedFile.config(text="writing pdf file(" + filename + ")...")
      window.update()
           
      merger.write(filename)
      merger.close

      lb_MergedFile.config(text=str(filename))
   
      messagebox.showinfo("merge files","Successfully done.")

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo(e, fn) #, e)
      lb_MergedFile.config(text="")

   


def fn_fileOpen():
   if lb_MergedFile.cget("text") == "":
      return
   
   path = os.path.realpath(lb_MergedFile.cget("text"))
   os.startfile(path)

def fn_folderOpen():
   if lb_MergedFile.cget("text") == "":
      return

   path = os.path.dirname(lb_MergedFile.cget("text"))
   os.startfile(path)


def fn_tab2_setPDFFile():
   global glb_open_file_path
   list_file = []
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
   filename = lb_tab2_filename.cget("text")
   folder = lb_tab2_foldername.cget("text")

   if not(filename!="" and folder!=""):
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Set source PDF file.\n" +
                                  "Step 2. Set directory to save image files.\n" +
                                  "Step 3. Run(Convert to image)!\n" +
                                  "Step 4. Check the image file(s).")
      return


   try:
      
      ## x = filename.split('/')
      ## filenm = x[-1]
      ## filenm = filenm.split(".")[0]
      
      if folder !="":
         if filename != "":
            images = convert_from_path(filename, fmt="jpg", poppler_path=resource_path(cfp_lib_path)) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

            list_tab2.delete(0,END)
            
            for i in range(len(images)):
               imgName = str(folder) + "/" + str(i+1) + ".jpg"
               images[i].save(imgName, "JPEG")
               list_tab2.insert(END, imgName)

            list_tab2.selection_set(0)
            fn_tab2_showImage(list_tab2)

            messagebox.showinfo("Convert to image","Successfully done.")
            
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return


def fn_tab2_showImage(self):

   if list_tab2.size() == 0:
      return
   
   lbx = image_label_tab2.winfo_width()
   lby = image_label_tab2.winfo_height()
   
   # 이미지 불러오기
   filename=str(list_tab2.get(list_tab2.curselection()[0],list_tab2.curselection()[0])[0])
   img = Image.open(filename)

   width, height = img.size

   x = 0
   y = 0

   if lbx < 101:
      return
   if lby < 101:
      return

   x = lbx - 100
   y = lby - 100
   
   if width < height:
      y = int(x * 1.4)

      if y > lby - 100:
         y = lby - 100
         x = int(y/1.4)
   else:
      x = int(y * 1.4)

      if x > lbx - 100:
         x = lbx - 100
         y = int(x/1.4)


   img = img.resize((x,y))
      
   # 이미지 표시
   image_tab2 = ImageTk.PhotoImage(img)
   image_label_tab2.configure(image=image_tab2, width=375, height=335)
   image_label_tab2.image=image_tab2

   
def fn_tab2_folderOpen():
   if lb_tab2_foldername.cget("text") == "":
      return

   path = os.path.realpath(lb_tab2_foldername.cget("text"))
   os.startfile(path)


def fn_tab2_fileOpen():

   if list_tab2.size()==0:
      return

   try:
      filename=str(list_tab2.get(list_tab2.curselection()[0],list_tab2.curselection()[0])[0])
      if filename == "":
         return
   except:
      return
   
   path = os.path.realpath(filename)
   os.startfile(path)


def fn_tab2_clear():
   lb_tab2_filename.config(text='')
   lb_tab2_foldername.config(text='')
   list_tab2.delete(0,END)
   image_label_tab2.image=""



def fn_tab3_setPDFFile():
   global glb_open_file_path
   list_file = []
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])

   if file == "" : return
   glb_open_file_path = os.path.dirname(file)
   
   fn_tab3_clear()
   lb_tab3_filename.config(text=str(file))



def fn_tab3_setFolder():
   folder=filedialog.askdirectory()
   if folder != "":
      lb_tab3_foldername.config(text=str(folder))



def fn_tab3_Run():
   filename = lb_tab3_filename.cget("text")
   folder = lb_tab3_foldername.cget("text")

   if not(filename!="" and folder!=""):
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Set source PDF file.\n" +
                                  "Step 2. Set directory to save text files.\n" +
                                  "Step 3. Run(Convert to text)!\n" +
                                  "Step 4. Check the text file(s).")
      return
   
   try:
      
      if folder !="":
         if filename != "":

            
            reader = PdfReader(filename)
            pages = reader.pages
            
            list_tab3.delete(0,END)

            i = 0
            
            for page in pages:
               i += 1
               txtName = str(folder) + "/" + str(i) + ".txt"
               
               text=page.extract_text()
               
               file1=open(txtName,"a", encoding='utf-8')
               file1.writelines(text)
               list_tab3.insert(END, txtName)


            list_tab3.selection_set(0)
            fn_tab3_showText(list_tab3)

            messagebox.showinfo("Convert to image","Successfully done.")
            
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return
   

def fn_tab3_showText(self):
   if list_tab3.size() == 0:
      return
   # 이미지 불러오기
   filename=str(list_tab3.get(list_tab3.curselection()[0],list_tab3.curselection()[0])[0])
   f=open(filename,"r", errors='ignore', encoding='utf-8')
   text_tab3.delete('1.0',tk.END)
   text_tab3.insert(tk.INSERT,f.read())
   
   f.close()
   
   
def fn_tab3_folderOpen():
   if lb_tab3_foldername.cget("text") == "":
      return

   path = os.path.realpath(lb_tab3_foldername.cget("text"))
   os.startfile(path)


def fn_tab3_fileOpen():

   if list_tab3.size()==0:
      return

   try:
      filename=str(list_tab3.get(list_tab3.curselection()[0],list_tab3.curselection()[0])[0])
      if filename == "":
         return

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return


   path = os.path.realpath(filename)
   os.startfile(path)


def fn_tab3_clear():
   lb_tab3_filename.config(text='')
   lb_tab3_foldername.config(text='')
   list_tab3.delete(0,END)
   text_tab3.delete('1.0',tk.END)


def fn_tab4_setPDFFile():

   global tab4_images_array
   global tab4_images


   global glb_open_file_path
   list_file = []
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])

   if file == "" : return
   glb_open_file_path = os.path.dirname(file)
   
   try:
      
      fn_tab4_clear()
         
      lb_tab4_filename.config(text=str(file))
         
      tab4_images = convert_from_path(file, fmt="jpg", poppler_path=resource_path(cfp_lib_path)) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

      list_tab4.delete(0,END)

      tab4_images_array = [0 for i in range(len(tab4_images))]
         
      for i in range(len(tab4_images)):
         imgName = str(i+1) + " page"
         list_tab4.insert(END, imgName)


      list_tab4.selection_set(0)
      fn_tab4_showImage(list_tab4)
         
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return



def fn_tab4_Run():

   global tab4_images_array
   filename = lb_tab4_filename.cget("text")

   if not(filename!=""):
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Open PDF file.\n" +
                                  "Step 2. Rotate page(s).\n" +
                                  "Step 3. Save!\n" +
                                  "Step 4. Check the file.")
      return

   pdfReader = PdfReader(filename,"rb")
   pdfWriter = PdfWriter()

   try:
      for pageNo in range(len(pdfReader.pages)):
         page = pdfReader.pages[pageNo]
         page.rotate(90 * tab4_images_array[pageNo])
         pdfWriter.add_page(page)

   
      global glb_open_file_path
      
      savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='rotate.pdf')

      if savefile=="": return
   

      if savefile[-3:].upper() != "PDF":
         savefile += ".pdf"



      if myCHK.get()==1:
         if len(myPWD.get()) > 0 :
            pdfWriter.encrypt(myPWD.get())
            
      pdfWriter.write(savefile)
      lb_tab4_savefile.config(text=savefile)
      messagebox.showinfo("Rotate page(s)","Successfully done.")

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return
   

'''
 1. 이미지 라벨 크기 가져오기
 2. 이미지 라벨 크기에 따른 이미지 크기 resize
 3. (tab2) [초기]  386 * 336 [최대] 956 * 837
 4. (tab4) [초기]  573 * 342 [최대] 1428 * 843

       window.update()
      print(image_label_tab4.winfo_width())
      print(image_label_tab4.winfo_height())
'''
def fn_tab4_showImage(self):
   # 이미지 불러오기

   global tab4_images

   if list_tab4.size() == 0: return

   try:
      #window.update()
      lbx = image_label_tab4.winfo_width()
      lby = image_label_tab4.winfo_height()

      
      idx=int(list_tab4.curselection()[0])
      lb_tab4_PNO.config(text=idx+1)
      img=tab4_images[idx]

      width, height = img.size

      x = 0
      y = 0

      if lbx < 200:
         return
      if lby < 100:
         return

      x = lbx - 200
      y = lby - 100
      
      if width < height:
         y = int(x * 1.4)

         if y > lby - 100:
            y = lby - 100
            x = int(y/1.4)
      else:
         x = int(y * 1.4)

         if x > lbx - 200:
            x = lbx - 200
            y = int(x/1.4)


      img = img.resize((x,y))


      image_tab4 = ImageTk.PhotoImage(img)
      image_label_tab4.configure(image=image_tab4, width=375, height=335)
      image_label_tab4.image=image_tab4

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return

   
def fn_tab4_folderOpen():

   filename=str(lb_tab4_savefile.cget("text"))
   
   if filename == "":
      return

   path = os.path.dirname(filename)
   os.startfile(path)


def fn_tab4_fileOpen():

   filename=str(lb_tab4_savefile.cget("text"))
   
   if filename=="":
      return
   
   path = os.path.realpath(filename)
   os.startfile(path)


def fn_tab4_clear():
   lb_tab4_filename.config(text='')
   lb_tab4_savefile.config(text='')
   lb_tab4_PNO.config(text='')
   list_tab4.delete(0,END)
   image_label_tab4.image=""




def fn_tab4_CW():

   global tab4_images_array
   global tab4_images

   pno = lb_tab4_PNO.cget("text")

   #window.update()
   lbx = image_label_tab4.winfo_width()
   lby = image_label_tab4.winfo_height()

   if pno !="":
      
      idx = int(pno)-1
      
      tab4_images[idx] = tab4_images[idx].transpose(method=Image.Transpose.ROTATE_270)
      
      img = tab4_images[idx]
      
      width, height = img.size

      x = 0
      y = 0

      if lbx < 200:
         return
      if lby < 100:
         return

      x = lbx - 200
      y = lby - 100
   
      if width < height:
         y = int(x * 1.4)

         if y > lby - 100:
            y = lby - 100
            x = int(y/1.4)
      else:
         x = int(y * 1.4)

         if x > lbx - 200:
            x = lbx - 200
            y = int(x/1.4)


      img = img.resize((x,y))

      image_tab4 = ImageTk.PhotoImage(img)
      image_label_tab4.configure(image=image_tab4, width=375, height=335)
      image_label_tab4.image=image_tab4

      temp = tab4_images_array[idx] + 1
      tab4_images_array[idx] = temp%4


def fn_tab4_CCW():
   
   global tab4_images_array
   global tab4_images
   
   pno = lb_tab4_PNO.cget("text")

   #window.update()
   lbx = image_label_tab4.winfo_width()
   lby = image_label_tab4.winfo_height()


   if pno !="":

      idx = int(pno)-1
      
      tab4_images[idx] = tab4_images[idx].transpose(method=Image.Transpose.ROTATE_90)
      
      img = tab4_images[idx]
      
      width, height = img.size

      x = 0
      y = 0

      if lbx < 200:
         return
      if lby < 100:
         return

      x = lbx - 200
      y = lby - 100
   
      if width < height:
         y = int(x * 1.4)

         if y > lby - 100:
            y = lby - 100
            x = int(y/1.4)
      else:
         x = int(y * 1.4)

         if x > lbx - 200:
            x = lbx - 200
            y = int(x/1.4)


      img = img.resize((x,y))

      image_tab4 = ImageTk.PhotoImage(img)
      image_label_tab4.configure(image=image_tab4, width=375, height=335)
      image_label_tab4.image=image_tab4

      if tab4_images_array[idx] == 0:
         tab4_images_array[idx] = 3
      else:
         tab4_images_array[idx] -= 1



def fn_tab5_setPDFFile():

   global tab5_images_array
   global tab5_images

   global glb_open_file_path
   list_file = []
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])

   if file == "" : return
   glb_open_file_path = os.path.dirname(file)

   
   try:
      
      fn_pb_init(lb_tab5_filename)
      fn_pb_set(10)
   
      fn_tab5_clear()
         
      lb_tab5_filename.config(text=str(file))
      
      tab5_images = convert_from_path(file, fmt="jpg", poppler_path=resource_path(cfp_lib_path)) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

      list_tab5.delete(0,END)

      tab5_images_array = [0 for i in range(len(tab5_images))]

      fn_pb_set(10)

      temp = (100-vb_pb.get())/len(tab5_images)
         
      for i in range(len(tab5_images)):
         imgName = str(i+1) #+ " page"
         list_tab5.insert(END, imgName)

         fn_pb_set(temp)
            
      list_tab5.selection_set(0)
      fn_tab5_showImage(list_tab5)

      fn_pb_exit()
         
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      fn_pb_exit()
      return



def fn_tab5_Run():

   filename = lb_tab5_filename.cget("text")

   if not(filename!=""):
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Open PDF file.\n" +
                                  "Step 2. Reorder pages.\n" +
                                  "Step 3. Save!(Anyway you can set file password.)\n" +
                                  "Step 4. Check the file.")
      return

   if list_R_tab5.size() == 0:
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Open PDF file.\n" +
                                  "Step 2. Reorder pages.\n" +
                                  "Step 3. Save!(Anyway you can set file password.)\n" +
                                  "Step 4. Check the file.")
      return


   
   pdfReader = PdfReader(filename,"rb")
   pdfWriter = PdfWriter()

   try:
      for pageNo in range(list_R_tab5.size()):
         page = pdfReader.pages[int(list_R_tab5.get(pageNo))-1]
         pdfWriter.add_page(page)

   
      global glb_open_file_path
      savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='reorder.pdf')

      if savefile=="":
         return
   

      if savefile[-3:].upper() != "PDF":
         savefile += ".pdf"
          
      if myCHK.get()==1:
         if len(myPWD.get()) > 0 :
            pdfWriter.encrypt(myPWD.get())
            
      pdfWriter.write(savefile)
      lb_tab5_savefile.config(text=savefile)
      messagebox.showinfo("Reorder pages","Successfully done.")

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return
   

'''
 1. 이미지 라벨 크기 가져오기
 2. 이미지 라벨 크기에 따른 이미지 크기 resize
 3. (tab2) [초기]  386 * 336 [최대] 956 * 837
 4. (tab5) [초기]  573 * 342 [최대] 1428 * 843

       window.update()
      print(image_label_tab5.winfo_width())
      print(image_label_tab5.winfo_height())
'''
def fn_tab5_showImage(self):
   # 이미지 불러오기
   global tab5_images

   if list_tab5.size() == 0:
      return

   #window.update()
   lbx = image_label_tab5.winfo_width()
   lby = image_label_tab5.winfo_height()

   
   idx=int(list_tab5.curselection()[0])
   lb_tab5_PNO.config(text=idx+1)
   lb_tab5_PLR.config(text='L')
   img=tab5_images[idx]

   width, height = img.size

   x = 0
   y = 0

   if lbx < 200:
      return
   if lby < 100:
      return

   x = lbx - 200
   y = lby - 100
   
   if width < height:
      y = int(x * 1.4)

      if y > lby - 100:
         y = lby - 100
         x = int(y/1.4)
   else:
      x = int(y * 1.4)

      if x > lbx - 200:
         x = lbx - 200
         y = int(x/1.4)


   img = img.resize((x,y))


   image_tab5 = ImageTk.PhotoImage(img)
   image_label_tab5.configure(image=image_tab5, width=375, height=335)
   image_label_tab5.image=image_tab5


def fn_R_tab5_showImage(self):
   # 이미지 불러오기
   
   global tab5_images

   if list_R_tab5.size() == 0:
      image_label_tab5.image=""
      lb_tab5_PLR.config(text='')
      lb_tab5_PNO.config(text='')
      return

   #window.update()
   lbx = image_label_tab5.winfo_width()
   lby = image_label_tab5.winfo_height()

   
   idx=int(list_R_tab5.curselection()[0])
   idx_imag=int(list_R_tab5.get(idx))-1
   
   lb_tab5_PNO.config(text=idx+1)
   lb_tab5_PLR.config(text='R')
   img=tab5_images[idx_imag]

   width, height = img.size

   x = 0
   y = 0

   if lbx < 200:
      return
   if lby < 100:
      return

   x = lbx - 200
   y = lby - 100
   
   if width < height:
      y = int(x * 1.4)

      if y > lby - 100:
         y = lby - 100
         x = int(y/1.4)
   else:
      x = int(y * 1.4)

      if x > lbx - 200:
         x = lbx - 200
         y = int(x/1.4)


   img = img.resize((x,y))


   image_tab5 = ImageTk.PhotoImage(img)
   image_label_tab5.configure(image=image_tab5, width=375, height=335)
   image_label_tab5.image=image_tab5

   
def fn_tab5_folderOpen():

   filename=str(lb_tab5_savefile.cget("text"))
   
   if filename == "":
      return

   path = os.path.dirname(filename)
   os.startfile(path)


def fn_tab5_fileOpen():

   filename=str(lb_tab5_savefile.cget("text"))
   
   if filename=="":
      return
   
   path = os.path.realpath(filename)
   os.startfile(path)


def fn_tab5_clear():
   lb_tab5_filename.config(text='')
   lb_tab5_savefile.config(text='')
   lb_tab5_PLR.config(text='')
   lb_tab5_PNO.config(text='')
   list_tab5.delete(0,END)
   list_R_tab5.delete(0,END)
   text_tab5.delete(0,END)
   image_label_tab5.image=""





def fn_tab5_chk():
   if myCHK.get() == 1:
      text_tab5.configure(state="normal")
   else:
      text_tab5.delete(0,END)
      text_tab5.configure(state="disabled")



def on_window_resize(event):
   pass
         
def closing():
    window.destroy()



def fn_tab5_mol():
   selectionR = list_R_tab5.curselection()
   if(len(selectionR) == 0):
      return
   idxR = selectionR[0]
   list_R_tab5.delete(idxR,idxR)

   if list_R_tab5.size() == idxR:
      list_R_tab5.selection_set(END)
   else:
      list_R_tab5.selection_set(idxR)

   fn_R_tab5_showImage(list_R_tab5)

def fn_tab5_mal():
   list_R_tab5.delete(0,END)
   fn_R_tab5_showImage(list_R_tab5)

   

def fn_tab5_mor():
   selectionL = list_tab5.curselection()

   if(len(selectionL) == 0):
      return
   idxL = selectionL[0] + 1
   
   selectionR = list_R_tab5.curselection()
   
   if(len(selectionR) == 0):
      list_R_tab5.insert(END, idxL)

   else:
      idxR = selectionR[0] + 1
      list_R_tab5.insert(idxR, idxL)
      list_R_tab5.selection_clear(0, END)
      list_R_tab5.selection_set(idxR)



def fn_tab5_mar():
   list_R_tab5.delete(0,END)
   for R in range(list_tab5.size()):
      list_R_tab5.insert(END, list_tab5.get(R))


#################################################


def fn_tab6_Run():

   global tab6_images
   global tab6_images_array
   
   pdf_file = lb_tab6_filename.cget("text")
   watermark_file = lb_tab6_watermarkfilename.cget("text")

   temp_dir = tempfile.TemporaryDirectory()

   merged = str(temp_dir.name) + "_jwh_18_gsk_.pdf"
   
   try:
      
      if pdf_file !="":
         if watermark_file != "":

            with open(pdf_file,"rb") as input_file, open(watermark_file,"rb") as watermark_file:
               input_pdf = PdfReader(input_file)
               watermark_pdf = PdfReader(watermark_file)
               watermark_page = watermark_pdf.pages[0]
               
               output = PdfWriter()
             
               for i in range(len(input_pdf.pages)):
                  pdf_page = input_pdf.pages[i]
                  pdf_page.merge_page(watermark_page)
                  output.add_page(pdf_page)

                  
               with open(merged, "wb") as merged_file:
                  output.write(merged_file)
               tab6_images = convert_from_path(merged, fmt="jpg", poppler_path=resource_path(cfp_lib_path)) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

               list_tab6.delete(0,END)

               tab6_images_array = [0 for i in range(len(tab6_images))]

               for i in range(len(tab6_images)):
                  imgName = str(i+1) #+ " page"
                  list_tab6.insert(END, imgName)

                  
               os.remove(merged)
         else:


            tab6_images = convert_from_path(pdf_file, fmt="jpg", poppler_path=resource_path(cfp_lib_path)) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

            list_tab6.delete(0,END)

            tab6_images_array = [0 for i in range(len(tab6_images))]
         
            for i in range(len(tab6_images)):
               imgName = str(i+1) #+ " page"
               list_tab6.insert(END, imgName)

               
            list_tab6.selection_set(0)
            fn_tab6_showImage(list_tab6)

            
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return




def fn_tab6_showImage(self, isClicked=True, pageNo=0):

   global tab6_sum_images
   global tab6_pdf_images
   global tab6_watermark_image
   
   
   pdfFileName = lb_tab6_filename.cget("text")
   waterMarkFileName = lb_tab6_watermarkfilename.cget("text")

   if waterMarkFileName =="": # only pdfFile
      list_tab6.selection_set(0)
      img = tab6_pdf_images[pageNo]
      
   elif pdfFileName =="":     # only watermarkFile
      img = convert_from_path(waterMarkFileName, fmt="png", poppler_path=resource_path(cfp_lib_path))[0] #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))[0]
#      img = tab6_watermark_image
      
   else:
      if isClicked==False:
         tab6_sum_images = convert_from_path(pdfFileName, fmt="jpg", poppler_path=resource_path(cfp_lib_path), thread_count=1) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))

         temp =(100-vb_pb.get())/len(tab6_pdf_images)

         for i in range(len(tab6_pdf_images)):

            
            fn_pb_set(temp)

            tab6_sum_images[i] = tab6_sum_images[i].convert('RGBA')
            #tab6_sum_images[i] = layer_combine(tab6_sum_images[i], tab6_watermark_image)
            tab6_watermark_image = tab6_watermark_image.resize((tab6_sum_images[i].size[0], tab6_sum_images[i].size[1]))
            #tab6_sum_images[i] = layer_combine(tab6_watermark_image,tab6_sum_images[i])            
            tab6_sum_images[i] = Image.alpha_composite(tab6_sum_images[i], tab6_watermark_image)
            #tab6_sum_images[i] = Image.alpha_composite(tab6_watermark_image, tab6_sum_images[i])

           
      img = tab6_sum_images[pageNo]

      
   
   # check app image_label size 
   lbx = image_label_tab6.winfo_width()
   lby = image_label_tab6.winfo_height()

   lb_tab6_PNO.config(text=pageNo+1)

   width, height = img.size

   x = 0
   y = 0

   if lbx < 200:      return
   if lby < 100:      return

   x = lbx - 200
   y = lby - 100
   
   if width < height:
      y = int(x * 1.4)

      if y > lby - 100:
         y = lby - 100
         x = int(y/1.4)
   else:
      x = int(y * 1.4)

      if x > lbx - 200:
         x = lbx - 200
         y = int(x/1.4)


   img = img.resize((x,y))


   image_tab6 = ImageTk.PhotoImage(img)
   image_label_tab6.configure(image=image_tab6, width=375, height=335)
   image_label_tab6.image=image_tab6


def fn_tab6_listPageNo(self):
   if list_tab6.size() == 0: return
   idx = int(list_tab6.curselection()[0])
   fn_tab6_showImage(self, True, idx)
   

def fn_tab6_setWaterMarkFile():

   global tab6_watermark_image

   global glb_open_file_path
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])

   if file == "" : return
   glb_open_file_path = os.path.dirname(file)



   #----------------------------------------------------
   # set label and global variable tab6_watermark_image
   #----------------------------------------------------
   lb_tab6_watermarkfilename.config(text=str(file))
   #----------------------------------------------------

   fn_pb_init(lb_tab6_watermarkfilename)
   fn_pb_set(10)
   
   watermark_images = convert_from_path(file, fmt="png", poppler_path=resource_path(cfp_lib_path), first_page=1, last_page=1, thread_count=1) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))
   img = watermark_images[0]
   img = img.convert('RGBA')

   datas = img.getdata()
   newData = []
   cutOff = 50

   '''
   for item in datas:
      if item[0] < cutOff and item[1] < cutOff and item[2] < cutOff:
         newData.append((0,0,0,0))
      else:
         newData.append(item)

   img.putdata(newData)
   '''
   
   for item in datas:
      
      if item[0] > 200 and item[1] > 200 and item[2] > 200:
         newData.append((item[0], item[1], item[2], 0))
      else:
         newData.append((item[0], item[1], item[2], 100))  # 100 : watermark 진하기 조정 ex) 0:진함

   img.putdata(newData)
         
   '''
   alpha = img.split()[3]
   alpha = ImageEnhance.Brightness(alpha).enhance(0.5)
   img.putalpha(alpha)
   '''
   #----------------------------------------------------
   tab6_watermark_image = img
   #----------------------------------------------------

   #--------------------------------
   fn_tab6_showImage(list_tab6, False)
   #--------------------------------

   fn_pb_exit()


def fn_tab6_setPdfFile():
   
   global tab6_images_array
   global tab6_pdf_images
   
   global glb_open_file_path
   
   file = filedialog.askopenfilename(initialdir=glb_open_file_path, title="select PDF file", filetypes=[("pdf file","*.pdf")])

   if file == "" : return
   glb_open_file_path = os.path.dirname(file)

   
   
   lb_tab6_filename.config(text=str(file))

   fn_pb_init(lb_tab6_filename)
   fn_pb_set(10)
   
   try:

      tab6_pdf_images = convert_from_path(file, fmt="png", poppler_path=resource_path(cfp_lib_path)) #, thread_count=10) #, poppler_path=resource_path("./lib/poppler-23.11.0/Library/bin"))
      list_tab6.delete(0,END)
      tab6_images_array = [0 for i in range(len(tab6_pdf_images))]

      fn_pb_set(10)
      
      for i in range(len(tab6_pdf_images)):
         imgName = str(i+1)
         list_tab6.insert(END, imgName)
         
      fn_pb_set(10)
      
      #--------------------------------
      fn_tab6_showImage(list_tab6, False)
      #--------------------------------
      

      fn_pb_exit()
      
   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      fn_pb_exit()
      return

   

   
def fn_tab6_Save():
   global tab6_sum_images
   
   pdfFile = lb_tab6_filename.cget("text")
   watermarkFile = lb_tab6_watermarkfilename.cget("text")
                                                  
   if not(pdfFile!="" and watermarkFile!=""):
      messagebox.showinfo(VERSION,"Usage\n\n" +
                                  "Step 1. Set source PDF file.\n" +
                                  "Step 2. Set watermark PDF file(FIRST PAGE will be watermark).\n" +
                                  "Step 3. Save!\n" +
                                  "Step 4. Check the result file.")
      return

   global glb_open_file_path
   savefile = tk.filedialog.asksaveasfilename(initialdir=glb_open_file_path, title="save PDF file", filetypes=[("pdf files","*.pdf")], initialfile='watermark.pdf')

   if savefile=="": return
   if savefile[-3:].upper() != "PDF": savefile += ".pdf"

   merger = PdfMerger()

   list_file = []
      
   try:

      temp_dir = tempfile.TemporaryDirectory()

      for i in range(len(tab6_sum_images)):
         temp_img_filename = str(temp_dir.name) + str(i) + ".jpg"
         temp_pdf_filename = str(temp_dir.name) + str(i) + ".pdf"
         tab6_sum_images[i]=tab6_sum_images[i].convert("RGB")
         tab6_sum_images[i].save(temp_img_filename)

         with open(temp_pdf_filename, "wb") as ff:
            ff.write(img2pdf.convert(temp_img_filename))
            list_file.append(temp_pdf_filename)
            
         merger.append(temp_pdf_filename)         
         os.remove(temp_img_filename)

      ff.close()
      
      merger.write(savefile)
      merger.close()

      for i in range(len(list_file)):
         os.remove(list_file[i])
         
      lb_tab6_savefile.config(text=savefile)
      
      messagebox.showinfo("Set Watermark","Successfully done.")

   except Exception as e:
      err_msg = traceback.format_exc()
      writeLog(err_msg)
      messagebox.showinfo("error", e)
      return



def fn_tab6_folderOpen():
   filename=str(lb_tab6_savefile.cget("text"))
   
   if filename == "":
      return

   path = os.path.dirname(filename)
   os.startfile(path)

def fn_tab6_fileOpen():

   filename=str(lb_tab6_savefile.cget("text"))
   
   if filename=="":
      return
   
   path = os.path.realpath(filename)
   os.startfile(path)
   


def fn_tab6_clear():
   lb_tab6_filename.config(text='')
   lb_tab6_watermarkfilename.config(text='')
   list_tab6.delete(0,END)
   image_label_tab6.image=""
   lb_tab6_PNO.config(text='')
   lb_tab6_savefile.config(text='')




#################################################
menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
#filemenu.add_command(label="Merge files", command=donothing)
#filemenu.add_command(label="Extract pages", command=donothing)
#filemenu.add_command(label="Convert to text", command=donothing)
#filemenu.add_separator()
#filemenu.add_command(label="Exit", command=window.quit)
#menubar.add_cascade(label="Function", menu=filemenu)
#menubar.add_command(label="Merge", command=donothing)
#menubar.add_command(label="Extract", command=donothing)
#menubar.add_command(label="Convert", command=donothing)
#menubar.add_command(label="Rotate", command=donothing)


helpmenu = Menu(menubar, tearoff=0)
'''
helpmenu.add_command(label="about", command=donothing)
helpmenu.add_separator()
helpmenu.add_command(label="exit", command=closing) # command=window.quit)
menubar.add_cascade(label="About", menu=helpmenu)
'''
menubar.add_command(label="About", command=donothing)
menubar.add_command(label="Message", command=showSystemMessage)

##################################################
window.config(menu=menubar)
#################################################
style = tkinter.ttk.Style(window)
style.theme_use('default')
style.configure('TNotebook.Tab', foreground="white", background="gray", width=window.winfo_screenwidth(), font=('Calibri','15','bold'), anchor="c")
style.map("TNotebook.Tab", foreground=[("selected", "gray")], 
                           background=[("selected", "white")],
                           font=[("selected",("Calibri","15", "bold"))])

tabs=tkinter.ttk.Notebook() #window) #, width=776, height=466)
tabs.grid(row=0,column=0, sticky='nsew')

#tabs.pack() #expand=True, fill=tk.BOTH)

#################################################

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

################### progressbar #################
style = tkinter.ttk.Style(window)
# add label in the layout
style.layout('text.Horizontal.TProgressbar', 
             [('Horizontal.Progressbar.trough',
               {'children': [('Horizontal.Progressbar.pbar',
                              {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'}), 
              ('Horizontal.Progressbar.label', {'sticky': 'nswe'})])
# set initial text
style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')


vb_pb = DoubleVar()
pb = tkinter.ttk.Progressbar(tabs, maximum = 100, variable=vb_pb, mode="determinate", style="text.Horizontal.TProgressbar")
pb.config(length=0)


#################################################
##    TAB1
#################################################
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
style.configure("mystyle.Treeview", font=('맑은 고딕', 11,'normal')) # Modify the font of the headings
style.configure("mystyle.Treeview.Heading", font=('Calibri', 12,'normal'), relief='ridge') # Modify the font of the headings


tab1_tree = tkinter.ttk.Treeview(tab1, style="mystyle.Treeview", selectmode = "browse", show="headings")
tab1_tree.grid(row=1, column=0, columnspan=5, padx=2, pady=2, sticky="nsew")

tab1_tree['columns'] = ("Name", "Size", "Update", "FileType")

#tab1_tree.column("#0", width=0, stretch=NO)
tab1_tree.column("Name", anchor = W, width=480, minwidth = 100)
tab1_tree.column("Size", anchor = E, width=40, minwidth = 20)
tab1_tree.column("Update", anchor = CENTER, width=40, minwidth = 20)
tab1_tree.column("FileType", anchor = CENTER, width=0) #, stretch = NO)


#tab1_tree.heading("#0", text="", anchor=W)
tab1_tree.heading("Name", text="File Name", anchor=CENTER)
tab1_tree.heading("Size", text="File Size", anchor = CENTER)
tab1_tree.heading("Update", text="Update date", anchor = CENTER)
tab1_tree.heading("FileType", text="File Type", anchor = CENTER)


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


Grid.rowconfigure(tab1, 0, weight=0)
Grid.rowconfigure(tab1, 1, weight=1)
Grid.rowconfigure(tab1, 2, weight=0)
Grid.rowconfigure(tab1, 3, weight=0)
Grid.rowconfigure(tab1, 4, weight=0)

Grid.columnconfigure(tab1, 0, weight=1)
Grid.columnconfigure(tab1, 1, weight=1)
Grid.columnconfigure(tab1, 2, weight=1)
Grid.columnconfigure(tab1, 3, weight=1)
Grid.columnconfigure(tab1, 4, weight=1)

#################################################
##    TAB2
#################################################
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

list_tab2 = Listbox(tab2, width=30, height=21, activestyle="none", exportselection=False) ##, font=('consolas',11,'normal'))
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


Grid.rowconfigure(tab2, 0, weight=0)
Grid.rowconfigure(tab2, 1, weight=0)
Grid.rowconfigure(tab2, 2, weight=0)
Grid.rowconfigure(tab2, 3, weight=1)
Grid.rowconfigure(tab2, 4, weight=0)

Grid.columnconfigure(tab2, 0, weight=0)
Grid.columnconfigure(tab2, 1, weight=0)
Grid.columnconfigure(tab2, 2, weight=1)
Grid.columnconfigure(tab2, 3, weight=1)


#################################################
##    TAB3
#################################################
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

list_tab3 = Listbox(tab3, width=30, height=21, activestyle="none", exportselection=False) ##, font=('consolas',11,'normal'))
list_tab3.grid(row=3, column=0, padx=2, pady=2, sticky=W+E+S+N)

list_tab3.bind('<<ListboxSelect>>', fn_tab3_showText)

list_tab3_sb = tk.Scrollbar(tab3, orient="vertical", command=list_tab3.yview)
list_tab3_sb.grid(row=3, column=0, padx=4, pady=4, sticky=N+S+E)

list_tab3.configure(yscrollcommand=list_tab3_sb.set)

text_tab3 = scrolledtext.ScrolledText(tab3, wrap=tk.WORD, width=52)
text_tab3.grid(row=3, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)
#text_tab3.configure(state="disabled")
text_tab3.config(font=("'Malgun Gothic', Consolas, 'Courier New', monospace", 11, 'normal'), spacing1=3, spacing2=3, spacing3=3) #, bg="#222222", fg="#DDDDDD")

bt_tab3_fileOpen = tk.Button(tab3, text='Open File', relief="groove", overrelief="solid", command=fn_tab3_fileOpen, width=30)
bt_tab3_fileOpen.grid(row=4, column=0, padx=1, pady=2, sticky=W+E+N+S)

bt_tab3_folderOpen = tk.Button(tab3, text='Open Folder', relief="groove", overrelief="solid", command=fn_tab3_folderOpen, width=30)
bt_tab3_folderOpen.grid(row=4, column=1, padx=1, pady=2, sticky=W+E+N+S)

bt_tab3_clear = tk.Button(tab3, text='Clear Screen', relief="groove", overrelief="solid", command=fn_tab3_clear, width=54)
bt_tab3_clear.grid(row=4, column=2, columnspan=2, padx=1, pady=2, sticky=W+E+N+S)


Grid.rowconfigure(tab3, 0, weight=0)
Grid.rowconfigure(tab3, 1, weight=0)
Grid.rowconfigure(tab3, 2, weight=0)
Grid.rowconfigure(tab3, 3, weight=1)
Grid.rowconfigure(tab3, 4, weight=0)

Grid.columnconfigure(tab3, 0, weight=0)
Grid.columnconfigure(tab3, 1, weight=0)
Grid.columnconfigure(tab3, 2, weight=1)
Grid.columnconfigure(tab3, 3, weight=1)

#################################################
##    TAB4
#################################################
bt_tab4_setPDFFile = tk.Button(tab4, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab4_setPDFFile)
bt_tab4_setPDFFile.grid(row=0, column=0, pady=4, sticky=W+E+N+S)

lb_tab4_filename = tk.Label(tab4, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab4_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=4, sticky=W+E+N+S)

list_tab4 = Listbox(tab4, width=30, height=21, activestyle="none", exportselection=False) ##, font=('consolas',11,'normal'))
list_tab4.grid(row=1, column=0, padx=2, pady=2, sticky=W+E+S+N)

list_tab4.bind('<<ListboxSelect>>', fn_tab4_showImage)

list_tab4_sb = tk.Scrollbar(tab4, orient="vertical", command=list_tab4.yview)
list_tab4_sb.grid(row=1, column=0, padx=4, pady=4, sticky=N+S+E)

list_tab4.configure(yscrollcommand=list_tab4_sb.set)


image_label_tab4 = tk.Label(tab4, bg="gray")
image_label_tab4.grid(row=1, column=1, columnspan=3, padx=2, pady=2, sticky=W+E+S+N)

image_label_tab4.bind("<Configure>", on_window_resize)

#--
bt_tab4_CW = tk.Button(tab4, text='CW', fg="white", bg="gray", font=('consolas',10,'bold'), relief="groove", overrelief="solid", width=5, height=2, command=fn_tab4_CW)
bt_tab4_CW.grid(row=1, column=1, padx=10, pady=2, sticky=W)
#--
#--
bt_tab4_CCW = tk.Button(tab4, text='CCW', fg="white", bg="gray", font=('consolas',10,'bold'), relief="groove", overrelief="solid", width=5, height=2, command=fn_tab4_CCW)
bt_tab4_CCW.grid(row=1, column=3, padx=10, pady=2, sticky=E)
#--


lb_tab4_PNO = tk.Label(tab4, height=1, bg="gray", font=('consolas',40,'bold'), fg="black", anchor="w")
lb_tab4_PNO.grid(row=1, column=3, padx=10, pady=10, sticky=E+N)


#frm_tab4 = tk.Frame(tab4, width=10)
#frm_tab4.grid(row=2, column=0, padx=1, pady=2, sticky=W+E+N+S)


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

Grid.rowconfigure(tab4, 0, weight=0)
Grid.rowconfigure(tab4, 1, weight=1)
Grid.rowconfigure(tab4, 2, weight=0)
Grid.rowconfigure(tab4, 3, weight=0)
Grid.rowconfigure(tab4, 4, weight=0)

Grid.columnconfigure(tab4, 0, weight=0)
Grid.columnconfigure(tab4, 1, weight=0)
Grid.columnconfigure(tab4, 2, weight=1)
Grid.columnconfigure(tab4, 3, weight=1)

#################################################
##    TAB5
#################################################
bt_tab5_setPDFFile = tk.Button(tab5, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab5_setPDFFile, width=30)
bt_tab5_setPDFFile.grid(row=0, column=0, pady=4, sticky=W+E+N+S)

lb_tab5_filename = tk.Label(tab5, height=1, bg="white", font=('consolas',9,'normal'), fg="black", width=81, anchor="w")
lb_tab5_filename.grid(row=0, column=1, columnspan=3, padx=2, pady=4, sticky=W+E+N+S)


#---------------------------------------------------------------------
frm_left_tab5 = tk.Frame(tab5, width=30)
frm_left_tab5.grid(row=1, column=0, padx=0, pady=0, sticky=W+E+N+S)

list_tab5 = Listbox(frm_left_tab5, width=12, height=21, activestyle="none", exportselection=False, justify="center") ##, font=('consolas',11,'normal'))
list_tab5.grid(row=0, column=0, rowspan=4, padx=2, pady=2, sticky=W+E+S+N)
list_tab5.bind('<<ListboxSelect>>', fn_tab5_showImage)
list_tab5_sb = tk.Scrollbar(frm_left_tab5, orient="vertical", command=list_tab5.yview)
list_tab5_sb.grid(row=0, column=0, rowspan=4, padx=4, pady=4, sticky=N+S+E)
list_tab5.configure(yscrollcommand=list_tab5_sb.set)

bt_tab5_MOR = tk.Button(frm_left_tab5, text='>', relief="groove", overrelief="solid", command=fn_tab5_mor) ##, width=2)
bt_tab5_MOR.grid(row=0, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)

bt_tab5_MAR = tk.Button(frm_left_tab5, text='>>', relief="groove", overrelief="solid", command=fn_tab5_mar)
bt_tab5_MAR.grid(row=1, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)

bt_tab5_MOL = tk.Button(frm_left_tab5, text='<', relief="groove", overrelief="solid", command=fn_tab5_mol)
bt_tab5_MOL.grid(row=2, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)

bt_tab5_MAL = tk.Button(frm_left_tab5, text='<<', relief="groove", overrelief="solid", command=fn_tab5_mal)
bt_tab5_MAL.grid(row=3, column=1, columnspan=1, padx=1, pady=2, sticky=W+E+S+N)


list_R_tab5 = Listbox(frm_left_tab5, width=12, height=21, activestyle="none", exportselection=False, justify="center") ##, font=('consolas',11,'normal'))
list_R_tab5.grid(row=0, column=2, rowspan=4, padx=2, pady=2, sticky=W+E+S+N)
list_R_tab5.bind('<<ListboxSelect>>', fn_R_tab5_showImage)
list_R_tab5_sb = tk.Scrollbar(frm_left_tab5, orient="vertical", command=list_R_tab5.yview)
list_R_tab5_sb.grid(row=0, column=2, rowspan=4, padx=4, pady=4, sticky=N+S+E)
list_R_tab5.configure(yscrollcommand=list_R_tab5_sb.set)


Grid.rowconfigure(frm_left_tab5, 0, weight=1)
Grid.rowconfigure(frm_left_tab5, 1, weight=1)
Grid.rowconfigure(frm_left_tab5, 2, weight=1)
Grid.rowconfigure(frm_left_tab5, 3, weight=1)

Grid.columnconfigure(frm_left_tab5, 0, weight=1)
Grid.columnconfigure(frm_left_tab5, 1, weight=0)
Grid.columnconfigure(frm_left_tab5, 2, weight=1)
#---------------------------------------------------------------------

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

Grid.rowconfigure(frm_tab5, 0, weight=1)
Grid.columnconfigure(frm_tab5, 0, weight=0)
Grid.columnconfigure(frm_tab5, 1, weight=1)


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

Grid.rowconfigure(tab5, 0, weight=0)
Grid.rowconfigure(tab5, 1, weight=1)
Grid.rowconfigure(tab5, 2, weight=0)
Grid.rowconfigure(tab5, 3, weight=0)
Grid.rowconfigure(tab5, 4, weight=0)

Grid.columnconfigure(tab5, 0, weight=0)
Grid.columnconfigure(tab5, 1, weight=0)
Grid.columnconfigure(tab5, 2, weight=1)
Grid.columnconfigure(tab5, 3, weight=1)

#################################################
##    TAB6
#################################################

bt_tab6_watermarkfilename = tk.Button(tab6, text='Set Watermark PDF File', relief="groove", overrelief="solid", command=fn_tab6_setWaterMarkFile)
bt_tab6_watermarkfilename.grid(row=0, column=0, pady=2, sticky=W+E+N+S)

lb_tab6_watermarkfilename = tk.Label(tab6, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab6_watermarkfilename.grid(row=0, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)

bt_tab6_setPDFFile = tk.Button(tab6, text='Set PDF File', relief="groove", overrelief="solid", command=fn_tab6_setPdfFile) #fn_tab6_setPDFFile)
bt_tab6_setPDFFile.grid(row=1, column=0, pady=2, sticky=W+E+N+S)

lb_tab6_filename = tk.Label(tab6, height=1, bg="white", font=('consolas',9,'normal'), fg="black", anchor="w")
lb_tab6_filename.grid(row=1, column=1, columnspan=3, padx=2, pady=3, sticky=W+E+N+S)

##bt_tab6_Run = tk.Button(tab6, text='Run (Set Watermark)', relief="groove", overrelief="solid", command=fn_tab6_Run)
##bt_tab6_Run.grid(row=2, column=0, columnspan=4, padx=1, pady=2, sticky=W+E+N+S)

list_tab6 = Listbox(tab6, width=30, height=21, activestyle="none", exportselection=False, justify="center") ##, font=('consolas',11,'normal'))
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


Grid.rowconfigure(tab6, 0, weight=0)
Grid.rowconfigure(tab6, 1, weight=0)
Grid.rowconfigure(tab6, 2, weight=1)
Grid.rowconfigure(tab6, 3, weight=0)
Grid.rowconfigure(tab6, 4, weight=0)
Grid.rowconfigure(tab6, 5, weight=0)

Grid.columnconfigure(tab6, 0, weight=0)
Grid.columnconfigure(tab6, 1, weight=0)
Grid.columnconfigure(tab6, 2, weight=0)
Grid.columnconfigure(tab6, 3, weight=1)

#################################################
##    TAB7
#################################################

text_tab7 = scrolledtext.ScrolledText(tab7, wrap=tk.WORD)
text_tab7.grid(row=0, column=0, padx=2, pady=2, sticky=W+E+S+N)
text_tab7.config(font=("Consolas, 'Courier New', monospace", 12, 'bold'), bg="#222222", fg="#DDDDDD") #fg='#55FF55') 
#text_tab7.configure(state="disabled")
#text_tab7.tag_config("important", background="black", foreground="green")

Grid.rowconfigure(tab7, 0, weight=1)
Grid.columnconfigure(tab7, 0, weight=1)
#################################################

window.mainloop()
