import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import *
from configparser import ConfigParser

from task import *
from screen import *
from task import *

class UI:
  def __init__(self, emu_mode = Emulator.BLUESTACKS):
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
    self.frame_btn = tk.Frame(self.window, height=240)
    self.frame_btn.pack(expand=1, fill="x")
    self.frame_setting = tk.Frame(self.tab_setting)
    self.frame_setting.grid(column=0, row=0)
    self.frame_setting_btn = tk.Frame(self.tab_setting, pady=10)
    self.frame_setting_btn.grid(column=0, row=1)
    self.frame_setting_view = tk.Frame(self.tab_setting, padx=20)
    self.frame_setting_view.grid(column=1, row=0, rowspan=2)

    self.setting_stringVar = []
    def getSettingLabel(text, row):
      tk.Label(self.frame_setting, text=text, anchor='e', width=32, font=('Arial', 12)).grid(row=row, column=0)
      input_str = StringVar(None)
      input_field = Entry(self.frame_setting, textvariable=input_str, width=20)
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
    btn_screenshot = tk.Button(self.frame_setting_btn, text='ScreenShot', width=15, height=2, font=('Arial', 12))
    btn_screenshot.bind('<Button>', self.btn_screenshot_event)
    btn_screenshot.pack(fill='both', side=RIGHT)
    btn_save_config = tk.Button(self.frame_setting_btn, text='Save', width=15, height=2, font=('Arial', 12))
    btn_save_config.bind('<Button>', self.btn_save_config_event)
    btn_save_config.pack(fill='both', side=RIGHT)
    btn_load_config = tk.Button(self.frame_setting_btn, text='Load', width=15, height=2, font=('Arial', 12))
    btn_load_config.bind('<Button>', self.btn_load_config_event)
    btn_load_config.pack(fill='both', side=RIGHT)
    self.label_screenshot = tk.Label(self.frame_setting_view)
    self.label_screenshot.pack(fill='both')

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

    self.bg_task = Task(emu_mode)
    self.initAll()

  def initAll(self):
    self.setSettingInputField()

  def setSettingInputField(self):
    if self.bg_task is None:
      raise Exception('setSettingInputField:: Need to set task variable first')
    else:
      def dealString(s):
        if type(s) is tuple:
          int_list = list(s)
          return ' '.join([str(x) for x in int_list])
        else:
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
      def dealString(s, type = int):
        s_split = s.split(' ')
        int_list = [type(x) for x in s_split]
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
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar[15].get(), float))
    
  def btn_run_event(self, _):
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

  def btn_screenshot_event(self, _):
    success, im = getScreenShot(self.bg_task.windowID, self.bg_task.variable.getZoomRatio())
    if success:
      self.screenshot_image = self.bg_task.detect.Image2OpenCV(im)
      labeled_screenshot = self.bg_task.detect.drawTestImage(self.screenshot_image.copy())
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(labeled_screenshot))
      # draw label
  def btn_save_config_event(self, _):
    config = ConfigParser()
    config.add_section('Coordinate')
    config.set('Coordinate', 'BoardDiceLeftTopXY', self.setting_stringVar[0].get())
    config.set('Coordinate', 'BoardDiceOffsetXY', self.setting_stringVar[1].get())
    config.set('Coordinate', 'LevelDiceLeftXY', self.setting_stringVar[2].get())
    config.set('Coordinate', 'LevelDiceOffsetX', self.setting_stringVar[3].get())
    config.set('Coordinate', 'EmojiDialogXY', self.setting_stringVar[4].get())
    config.set('Coordinate', 'EmojiLeftXY', self.setting_stringVar[5].get())
    config.set('Coordinate', 'EmojiOffsetX', self.setting_stringVar[6].get())
    config.set('Coordinate', 'SummonDiceXY', self.setting_stringVar[7].get())
    config.set('Coordinate', 'LevelSpXY', self.setting_stringVar[8].get())
    config.set('Coordinate', 'MergeFloatLocationXY', self.setting_stringVar[9].get())
    config.set('Coordinate', 'ExtractDiceSizeWH', self.setting_stringVar[10].get())
    config.set('Coordinate', 'ExtractDiceLuSizeWH', self.setting_stringVar[11].get())
    config.set('Coordinate', 'ExtractSpLuSizeWH', self.setting_stringVar[12].get())
    config.set('Coordinate', 'ExtractSummonLuSizeWH', self.setting_stringVar[13].get())
    config.set('Coordinate', 'ExtractLevelDiceLuSizeWH', self.setting_stringVar[14].get())
    config.add_section('Window')
    config.set('Window', 'ZoomRatio', self.setting_stringVar[15].get())

    with open(self.bg_task.variable.getConfigFileName(), 'w') as f:
      config.write(f)

  def btn_load_config_event(self, _):
    config = ConfigParser()
    config.read(self.bg_task.variable.getConfigFileName())

    self.setting_stringVar[0].set(config.get('Coordinate', 'BoardDiceLeftTopXY', fallback='0 0'))
    self.setting_stringVar[1].set(config.get('Coordinate', 'BoardDiceOffsetXY', fallback='0 0'))
    self.setting_stringVar[2].set(config.get('Coordinate', 'LevelDiceLeftXY', fallback='0 0'))
    self.setting_stringVar[3].set(config.get('Coordinate', 'LevelDiceOffsetX', fallback='0'))
    self.setting_stringVar[4].set(config.get('Coordinate', 'EmojiDialogXY', fallback='0 0'))
    self.setting_stringVar[5].set(config.get('Coordinate', 'EmojiLeftXY', fallback='0 0'))
    self.setting_stringVar[6].set(config.get('Coordinate', 'EmojiOffsetX', fallback='0'))
    self.setting_stringVar[7].set(config.get('Coordinate', 'SummonDiceXY', fallback='0 0'))
    self.setting_stringVar[8].set(config.get('Coordinate', 'LevelSpXY', fallback='0 0'))
    self.setting_stringVar[9].set(config.get('Coordinate', 'MergeFloatLocationXY', fallback='0 0'))
    self.setting_stringVar[10].set(config.get('Coordinate', 'ExtractDiceSizeWH', fallback='50 50'))
    self.setting_stringVar[11].set(config.get('Coordinate', 'ExtractDiceLuSizeWH', fallback='40 40'))
    self.setting_stringVar[12].set(config.get('Coordinate', 'ExtractSpLuSizeWH', fallback='5 5'))
    self.setting_stringVar[13].set(config.get('Coordinate', 'ExtractSummonLuSizeWH', fallback='3 3'))
    self.setting_stringVar[14].set(config.get('Coordinate', 'ExtractLevelDiceLuSizeWH', fallback='40 40'))
    self.setting_stringVar[15].set(config.get('Window', 'ZoomRatio', fallback='1'))

  def changeImage(self, label: tk.Label, img):
    label.configure(image=img)
    label.image = img

  def run_bg_task(self):
    while self.isRunning:
      # run
      self.bg_task.task()
      # update ui
      for i, name in enumerate(self.bg_task.board_dice):
        idx = self.bg_task.detect.dice_name_idx_dict[name]
        img = self.bg_task.detect.dice_image_tk_resize[idx]
        self.changeImage(self.label_board_dice[i], img)
      for i, img in enumerate(self.bg_task.detect_board_dice_img):
        img = ImageTk.PhotoImage(self.bg_task.detect.OpenCV2Image(img))
        self.changeImage(self.label_detect_board_dice[i], img)
      # wait for delay
      time.sleep(1)

  def onClosing(self):
    if self.isRunning:
      self.isRunning = False
    self.window.destroy()

  def RUN(self):
    self.window.mainloop()