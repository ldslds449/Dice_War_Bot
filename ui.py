import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import *


class UI:
  def __init__(self):
    self.bg_task = None

    self.window = tk.Tk()
    # let the window on top
    self.window.title('Dice Bot')
    self.window.lift()
    self.window.call('wm', 'attributes', '.', '-topmost', True)

    # tab
    self.tabControl = ttk.Notebook(self.window)
    self.tab_detect = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_detect, text='Detect')
    self.tab_setting = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_setting, text='Setting')
    self.tabControl.pack(expand=1, fill="both")

    self.frame_board = tk.Frame(self.tab_detect, width=400, height=170)
    self.frame_board.grid(column=0, row=0)
    self.frame_screenshot = tk.Frame(self.tab_detect, width=200, height=170)
    self.frame_screenshot.grid(column=1, row=0)
    self.frame_btn = tk.Frame(self.window, height=240, bg='green')
    self.frame_btn.pack(expand=1, fill="x")

    self.setting_stringVar = []
    def getSettingLabel(text, row):
      tk.Label(self.tab_setting, text=text, anchor='e', width=32, font=('Arial', 12)).grid(row=row, column=0)
      input_str = StringVar(None)
      input_field = Entry(self.tab_setting, textvariable=input_str, width=20)
      input_field.grid(row=row, column=1)
      self.setting_stringVar.append(input_str)
    getSettingLabel('Board Left Top XY: ', 0)
    getSettingLabel('Board Dice Offset XY: ', 1)
    getSettingLabel('Level Dice Left XY: ', 2)
    getSettingLabel('Level Dice Offset X: ', 3)
    getSettingLabel('Emoji Dialog XY: ', 4)
    getSettingLabel('Emoji Left XY: ', 5)
    getSettingLabel('Emoji Offset X: ', 6)
    getSettingLabel('Summon Dice XY: ', 7)
    getSettingLabel('Level SP XY: ', 8)
    getSettingLabel('Merge Float Location XY: ', 9)
    getSettingLabel('Extract Dice Size WH: ', 10)
    getSettingLabel('Extract Dice Luminance Size WH: ', 11)
    getSettingLabel('Extract SP Luminance Size WH: ', 12)
    getSettingLabel('Extract Summon Luminance Size WH: ', 13)
    getSettingLabel('Extract Level Dice Luminance Size WH: ', 14)
    getSettingLabel('Zoom Ratio: ', 15)

    # board
    self.label_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_board, padx=5, pady=5)
      label.grid(row=i//5, column=i%5)
      self.label_board_dice.append(label)

    # label
    self.label_detect_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_screenshot, padx=5, pady=5)
      label.grid(row=i//5, column=i%5)
      self.label_detect_board_dice.append(label)

    # button
    self.btn_run = tk.Button(self.frame_btn, text='Start', width=15, height=3, font=('Arial', 12))
    self.btn_run.bind('<Button>', self.btn_run_event)
    self.btn_run.pack(fill='both')
    self.isRunning = False

    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

  def setSettingInputField(self):
    if self.bg_task is None:
      raise Exception('setSettingInputField:: Need to set task variable first')
    else:
      def dealString(s):
        if type(s) is tuple:
          int_list = list(s)
          return ' '.join([str(x) for x in int_list])
        elif type(s) is int:
          return str(s)
      self.setting_stringVar[0].set(dealString(self.bg_task.variable.getBoardDiceLeftTopXY()))
      self.setting_stringVar[1].set(dealString(self.bg_task.variable.getBoardDiceOffsetXY()))
      self.setting_stringVar[2].set(dealString(self.bg_task.variable.getLevelDiceLeftXY()))
      self.setting_stringVar[3].set(dealString(self.bg_task.variable.getLevelDiceOffsetX()))
      self.setting_stringVar[4].set(dealString(self.bg_task.variable.getEmojiDialogXY()))
      self.setting_stringVar[5].set(dealString(self.bg_task.variable.getEmojiLeftXY()))
      self.setting_stringVar[6].set(dealString(self.bg_task.variable.getEmojiOffsetX()))
      self.setting_stringVar[7].set(dealString(self.bg_task.variable.getSummonDiceXY()))
      self.setting_stringVar[8].set(dealString(self.bg_task.variable.getLevelSpXY()))
      self.setting_stringVar[9].set(dealString(self.bg_task.variable.getMergeFloatLocationXY()))
      self.setting_stringVar[10].set(dealString(self.bg_task.variable.getExtractDiceSizeWH()))
      self.setting_stringVar[11].set(dealString(self.bg_task.variable.getExtractDiceLuSizeWH()))
      self.setting_stringVar[12].set(dealString(self.bg_task.variable.getExtractSpLuSizeWH()))
      self.setting_stringVar[13].set(dealString(self.bg_task.variable.getExtractSummonLuSizeWH()))
      self.setting_stringVar[14].set(dealString(self.bg_task.variable.getExtractLevelDiceLuSizeWH()))
      self.setting_stringVar[15].set(dealString(self.bg_task.variable.getZoomRatio()))

  def getSettingInputField(self):
    if self.bg_task is None:
      raise Exception('getSettingInputField:: Need to set task variable first')
    else:
      def dealString(s):
        s_split = s.split(' ')
        int_list = [int(x) for x in s_split]
        return int_list[0] if len(int_list) == 1 else tuple(int_list)
      self.bg_task.variable.setBoardDiceLeftTopXY(dealString(self.setting_stringVar[0].get()))
      self.bg_task.variable.setBoardDiceOffsetXY(dealString(self.setting_stringVar[1].get()))
      self.bg_task.variable.setLevelDiceLeftXY(dealString(self.setting_stringVar[2].get()))
      self.bg_task.variable.setLevelDiceOffsetX(dealString(self.setting_stringVar[3].get()))
      self.bg_task.variable.setEmojiDialogXY(dealString(self.setting_stringVar[4].get()))
      self.bg_task.variable.setEmojiLeftXY(dealString(self.setting_stringVar[5].get()))
      self.bg_task.variable.setEmojiOffsetX(dealString(self.setting_stringVar[6].get()))
      self.bg_task.variable.setSummonDiceXY(dealString(self.setting_stringVar[7].get()))
      self.bg_task.variable.setLevelSpXY(dealString(self.setting_stringVar[8].get()))
      self.bg_task.variable.setMergeFloatLocationXY(dealString(self.setting_stringVar[9].get()))
      self.bg_task.variable.setExtractDiceSizeWH(dealString(self.setting_stringVar[10].get()))
      self.bg_task.variable.setExtractDiceLuSizeWH(dealString(self.setting_stringVar[11].get()))
      self.bg_task.variable.setExtractSpLuSizeWH(dealString(self.setting_stringVar[12].get()))
      self.bg_task.variable.setExtractSummonLuSizeWH(dealString(self.setting_stringVar[13].get()))
      self.bg_task.variable.setExtractLevelDiceLuSizeWH(dealString(self.setting_stringVar[14].get()))
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar[15].get()))

  def setTask(self, bg_task):
    self.bg_task = bg_task
    self.setSettingInputField()
    
  def btn_run_event(self, event):
    if self.isRunning == False: # enable
      if self.bg_task is not None:
        self.getSettingInputField()
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