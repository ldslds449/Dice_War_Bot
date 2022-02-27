import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
import cv2

class UI:
  def __init__(self):
    self.bg_task = None

    self.window = tk.Tk()
    self.window.title('Dice Bot')
    self.window.lift()
    self.window.call('wm', 'attributes', '.', '-topmost', True)

    self.frame_board = tk.Frame(self.window, width=400, height=170)
    self.frame_label = tk.Frame(self.window, width=200, height=170, bg='blue')
    self.frame_btn = tk.Frame(self.window, width=600, height=80, bg='green')
    self.frame_board.grid(column=0, row=0)
    self.frame_label.grid(column=1, row=0)
    self.frame_btn.grid(column=0, row=1, columnspan=2)

    # board
    self.label_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_board, padx=5, pady=5)
      label.grid(row=i//5, column=i%5)
      self.label_board_dice.append(label)

    # label
    self.label_detect_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_label, padx=5, pady=5)
      label.grid(row=i//5, column=i%5)
      self.label_detect_board_dice.append(label)

    # button
    self.btn_run = tk.Button(self.frame_btn, text='Start', width=15, height=3, font=('Arial', 12))
    self.btn_run.bind('<Button>', self.btn_run_event)
    self.btn_run.grid(column=0, row=0)
    self.isRunning = False

    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

  def setTask(self, bg_task):
    self.bg_task = bg_task
    
  def btn_run_event(self, event):
    if self.isRunning == False: # enable
      if self.bg_task is not None:
        self.isRunning = True
        self.thread_bg_task = threading.Thread(target = self.run_bg_task)
        self.thread_bg_task.start()
        self.btn_run.config(text='Stop')
    else: # disable
      self.isRunning = False
      self.btn_run.config(text='Start')

  def run_bg_task(self):
    while self.isRunning:
      # run
      self.bg_task.task()
      # update ui
      for i, name in enumerate(self.bg_task.board_dice):
        idx = self.bg_task.detect.dice_name_idx_dict[name]
        img = self.bg_task.detect.dice_image_tk_resize[idx]
        self.label_board_dice[i].configure(image=img)
        self.label_board_dice[i].image = img
      for i, img in enumerate(self.bg_task.detect_board_dice_img):
        img = ImageTk.PhotoImage(self.bg_task.detect.OpenCV2Image(img))
        self.label_detect_board_dice[i].configure(image=img)
        self.label_detect_board_dice[i].image = img
      # wait for delay
      time.sleep(1)

  def onClosing(self):
    if self.isRunning:
      self.isRunning = False
    self.window.destroy()

  def RUN(self):
    self.window.mainloop()