import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import *

from task import *
from screen import *
from mode import *
from action import *

class UI:
  def __init__(self, emu_mode = Emulator.BLUESTACKS):
    self.window = tk.Tk()

    self.bg_task = Task(MyAction())

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

    self.frame_board = tk.Frame(self.tab_detect, width=200, height=400)
    self.frame_board.grid(column=0, row=0)
    self.frame_screenshot = tk.Frame(self.tab_detect, width=200, height=400)
    self.frame_screenshot.grid(column=1, row=0)
    self.frame_select_dice = tk.Frame(self.tab_detect)
    self.frame_select_dice.grid(column=0, row=1, columnspan=2)
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
    SettingLabelList = [
      'Control Mode',
      'Emulator',
      'ADB Port',
      'Board Left Top XY',
      'Board Dice Offset XY',
      'Level Dice Left XY',
      'Level Dice Offset X',
      'Emoji Dialog XY',
      'Emoji Left XY',
      'Emoji Offset X',
      'Summon Dice XY',
      'Level SP XY',
      'Merge Float Location XY',
      'Extract Dice Size WH',
      'Extract Dice Luminance Size WH',
      'Extract SP Luminance Size WH',
      'Extract Summon Luminance Size WH',
      'Extract Level Dice Luminance Size WH',
      'Zoom Ratio'
    ]
    for i, label in enumerate(SettingLabelList):
      getSettingLabel(f'{label}: ', i)
    btn_save_config = tk.Button(self.frame_setting_btn, text='Save', width=15, height=2, font=('Arial', 12))
    btn_save_config.bind('<Button>', self.btn_save_config_event)
    btn_save_config.grid(row=0, column=0)
    btn_load_config = tk.Button(self.frame_setting_btn, text='Load', width=15, height=2, font=('Arial', 12))
    btn_load_config.bind('<Button>', self.btn_load_config_event)
    btn_load_config.grid(row=0, column=1)
    btn_screenshot = tk.Button(self.frame_setting_btn, text='ScreenShot', width=15, height=2, font=('Arial', 12))
    btn_screenshot.bind('<Button>', self.btn_screenshot_event)
    btn_screenshot.grid(row=0, column=2)
    btn_draw = tk.Button(self.frame_setting_btn, text='Draw', width=15, height=2, font=('Arial', 12))
    btn_draw.bind('<Button>', self.btn_draw)
    btn_draw.grid(row=1, column=0)
    btn_connect = tk.Button(self.frame_setting_btn, text='Connect', width=15, height=2, font=('Arial', 12))
    btn_connect.bind('<Button>', self.btn_ADB_connect_event)
    btn_connect.grid(row=1, column=1)
    self.label_screenshot = tk.Label(self.frame_setting_view)
    self.label_screenshot.pack(fill=BOTH)

    # board
    self.label_board_dice = []
    self.label_board_star = []
    for i in range(15):
      label = tk.Label(self.frame_board, padx=5, pady=5)
      label.grid(row=i//5, column=(i%5)*2)
      self.label_board_dice.append(label)
      label = tk.Label(self.frame_board, padx=5, pady=5)
      label.grid(row=i//5, column=(i%5)*2+1)
      self.label_board_star.append(label)

    # screenshot
    self.label_detect_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_screenshot, padx=5, pady=5)
      label.grid(row=i//5, column=i%5)
      self.label_detect_board_dice.append(label)

    # select dice
    self.select_dice_booleanVar = []
    for i, name in enumerate(self.bg_task.detect.dice_name):
      chkValue = tk.BooleanVar() 
      chkValue.set(False)
      checkBtn = tk.Checkbutton(self.frame_select_dice, text=name, var=chkValue, command=self.ckeckBtn_select_dice_event) 
      checkBtn.grid(row=i//8, column=i%8, sticky="W")
      self.select_dice_booleanVar.append(chkValue)

    # button
    self.btn_run = tk.Button(self.frame_btn, text='Start', width=15, height=3, font=('Arial', 12))
    self.btn_run.bind('<Button>', self.btn_run_event)
    self.btn_run.pack(fill=BOTH)
    self.isRunning = False

    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

    self.initAll()

  def initAll(self):
    self.setSettingInputField()
    self.btn_load_config_event(None)
    self.setSelectDiceField()

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
      self.setting_stringVar[0].set(dealString(int(self.bg_task.variable.getControlMode())))
      self.setting_stringVar[1].set(dealString(int(self.bg_task.variable.getEmulatorMode())))
      self.setting_stringVar[2].set(dealString(self.bg_task.variable.getADBPort()))
      self.setting_stringVar[3].set(dealString(self.bg_task.variable.getBoardDiceLeftTopXY()))
      self.setting_stringVar[4].set(dealString(self.bg_task.variable.getBoardDiceOffsetXY()))
      self.setting_stringVar[5].set(dealString(self.bg_task.variable.getLevelDiceLeftXY()))
      self.setting_stringVar[6].set(dealString(self.bg_task.variable.getLevelDiceOffsetX()))
      self.setting_stringVar[7].set(dealString(self.bg_task.variable.getEmojiDialogXY()))
      self.setting_stringVar[8].set(dealString(self.bg_task.variable.getEmojiLeftXY()))
      self.setting_stringVar[9].set(dealString(self.bg_task.variable.getEmojiOffsetX()))
      self.setting_stringVar[10].set(dealString(self.bg_task.variable.getSummonDiceXY()))
      self.setting_stringVar[11].set(dealString(self.bg_task.variable.getLevelSpXY()))
      self.setting_stringVar[12].set(dealString(self.bg_task.variable.getMergeFloatLocationXY()))
      self.setting_stringVar[13].set(dealString(self.bg_task.variable.getExtractDiceSizeWH()))
      self.setting_stringVar[14].set(dealString(self.bg_task.variable.getExtractDiceLuSizeWH()))
      self.setting_stringVar[15].set(dealString(self.bg_task.variable.getExtractSpLuSizeWH()))
      self.setting_stringVar[16].set(dealString(self.bg_task.variable.getExtractSummonLuSizeWH()))
      self.setting_stringVar[17].set(dealString(self.bg_task.variable.getExtractLevelDiceLuSizeWH()))
      self.setting_stringVar[18].set(dealString(self.bg_task.variable.getZoomRatio()))

  def getSettingInputField(self):
    if self.bg_task is None:
      raise Exception('getSettingInputField:: Need to set task variable first')
    else:
      def dealString(s, type = int):
        s_split = s.split(' ')
        int_list = [type(x) for x in s_split]
        return int_list[0] if len(int_list) == 1 else tuple(int_list)
      self.bg_task.variable.setControlMode(ControlMode(dealString(self.setting_stringVar[0].get())))
      self.bg_task.variable.setEmulatorMode(Emulator(dealString(self.setting_stringVar[1].get())))
      self.bg_task.variable.setADBPort(dealString(self.setting_stringVar[2].get()))
      self.bg_task.variable.setBoardDiceLeftTopXY(dealString(self.setting_stringVar[3].get()))
      self.bg_task.variable.setBoardDiceOffsetXY(dealString(self.setting_stringVar[4].get()))
      self.bg_task.variable.setLevelDiceLeftXY(dealString(self.setting_stringVar[5].get()))
      self.bg_task.variable.setLevelDiceOffsetX(dealString(self.setting_stringVar[6].get()))
      self.bg_task.variable.setEmojiDialogXY(dealString(self.setting_stringVar[7].get()))
      self.bg_task.variable.setEmojiLeftXY(dealString(self.setting_stringVar[8].get()))
      self.bg_task.variable.setEmojiOffsetX(dealString(self.setting_stringVar[9].get()))
      self.bg_task.variable.setSummonDiceXY(dealString(self.setting_stringVar[10].get()))
      self.bg_task.variable.setLevelSpXY(dealString(self.setting_stringVar[11].get()))
      self.bg_task.variable.setMergeFloatLocationXY(dealString(self.setting_stringVar[12].get()))
      self.bg_task.variable.setExtractDiceSizeWH(dealString(self.setting_stringVar[13].get()))
      self.bg_task.variable.setExtractDiceLuSizeWH(dealString(self.setting_stringVar[14].get()))
      self.bg_task.variable.setExtractSpLuSizeWH(dealString(self.setting_stringVar[15].get()))
      self.bg_task.variable.setExtractSummonLuSizeWH(dealString(self.setting_stringVar[16].get()))
      self.bg_task.variable.setExtractLevelDiceLuSizeWH(dealString(self.setting_stringVar[17].get()))
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar[18].get(), float))
    
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
    success, im = self.bg_task.screen.getScreenShot(self.bg_task.variable.getZoomRatio())
    if success:
      self.screenshot_image = self.bg_task.detect.Image2OpenCV(im)
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(self.screenshot_image))
  
  def btn_draw(self, _):
    self.getSettingInputField()
    labeled_screenshot = self.bg_task.detect.drawTestImage(self.screenshot_image.copy())
    self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(labeled_screenshot))

  def btn_save_config_event(self, _):
    self.getSettingInputField()
    self.bg_task.variable.saveToConfigFile()

  def btn_load_config_event(self, _):
    self.bg_task.variable.loadFromConfigFile()
    self.setSettingInputField()

  def changeImage(self, label: tk.Label, img):
    label.configure(image=img)
    label.image = img

  def ckeckBtn_select_dice_event(self, ):
    self.getSelectDiceField()

  def getSelectDiceField(self):
    select_dice = []
    for var, name in zip(self.select_dice_booleanVar, self.bg_task.detect.dice_name):
      if var.get() == True:
        select_dice.append(name)
    self.bg_task.variable.setDiceParty(select_dice)

  def setSelectDiceField(self):
    for var, name in zip(self.select_dice_booleanVar, self.bg_task.detect.dice_name):
      if name in self.bg_task.variable.getDiceParty():
        var.set(True)

  def btn_ADB_connect_event(self, _):
    if self.bg_task.variable.getControlMode() == ControlMode.WIN32API:
      self.bg_task.getWindowID()
      print(f'WindowID: {self.bg_task.windowID}')
    elif self.bg_task.variable.getControlMode() == ControlMode.ADB:
      # connect to device
      ADB.connect(self.bg_task.variable.getADBIP(), self.bg_task.variable.getADBPort())
    self.bg_task.init()

  def run_bg_task(self):
    while self.isRunning:
      # run
      self.bg_task.task()
      # update ui
      for i, name in enumerate(self.bg_task.board_dice):
        idx = self.bg_task.detect.dice_name_idx_dict[name]
        img = self.bg_task.detect.dice_image_tk_resize[idx]
        self.changeImage(self.label_board_dice[i], img)
      for i, star in enumerate(self.bg_task.board_dice_star):
        self.label_board_star[i].config(text=str(star))
      for i, img in enumerate(self.bg_task.detect_board_dice_img):
        img = ImageTk.PhotoImage(self.bg_task.detect.OpenCV2Image(img))
        self.changeImage(self.label_detect_board_dice[i], img)

  def onClosing(self):
    self.close()
    self.window.destroy()

  def close(self):
    self.isRunning = False
    if self.bg_task.variable.getControlMode() == ControlMode.ADB:
      ADB.disconnect()

  def RUN(self):
    self.window.mainloop()
    self.close()