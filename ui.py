import tkinter as tk
import threading
from tkinter import ttk
from tkinter import *
from tkinter import messagebox

from task import *
from screen import *
from mode import *

class UI:
  def __init__(self):
    self.window = tk.Tk()

    self.bg_task = Task()

    # let the window on top
    self.window.title('Dice Bot')

    # tab
    self.tabControl = ttk.Notebook(self.window)
    self.tab_detect = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_detect, text='Detect')
    self.tab_setting = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_setting, text='Setting')
    self.tabControl.pack(expand=1, fill="both")

    self.frame_board = tk.Frame(self.tab_detect, width=200, height=400, pady=10, padx=10)
    self.frame_board.grid(column=0, row=0, columnspan=2)
    self.frame_screenshot = tk.Frame(self.tab_detect, width=200, height=400)
    self.frame_screenshot.grid(column=2, row=0, columnspan=2)
    self.frame_select_dice = tk.Frame(self.tab_detect, padx=20)
    self.frame_select_dice.grid(column=0, row=1, columnspan=4)
    self.frame_log = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_log.grid(column=0, row=2, columnspan=6)
    self.frame_detect_btn = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_detect_btn.grid(column=5, row=0, rowspan=2)
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
      tk.Label(self.frame_setting, text=text, anchor='e', width=32, font=('Arial', 10)).grid(row=row, column=0)
      input_str = StringVar(None)
      input_field = Entry(self.frame_setting, textvariable=input_str, width=20)
      input_field.grid(row=row, column=1)
      self.setting_stringVar.append(input_str)
    SettingLabelList = [
      'Control Mode',
      'Emulator',
      'Detect Dice Mode',
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
      'Battle XY',
      'AD Close XY',
      'Extract Dice Size WH',
      'Extract Dice Luminance Size WH',
      'Extract SP Luminance Size WH',
      'Extract Summon Luminance Size WH',
      'Extract Level Dice Luminance Size WH',
      'Emoji Dialog WH',
      'Zoom Ratio'
    ]
    for i, label in enumerate(SettingLabelList):
      getSettingLabel(f'{label}: ', i)
    btn_save_config = tk.Button(self.frame_setting_btn, text='Save', width=10, height=2, font=('Arial', 12))
    btn_save_config.config(command=self.btn_save_config_event)
    btn_save_config.grid(row=0, column=0)
    btn_load_config = tk.Button(self.frame_setting_btn, text='Load', width=10, height=2, font=('Arial', 12))
    btn_load_config.config(command=self.btn_load_config_event)
    btn_load_config.grid(row=0, column=1)
    self.btn_screenshot = tk.Button(self.frame_setting_btn, text='ScreenShot', width=10, height=2, font=('Arial', 12))
    self.btn_screenshot.config(command=self.btn_screenshot_event, state=DISABLED)
    self.btn_screenshot.grid(row=1, column=0)
    self.btn_draw = tk.Button(self.frame_setting_btn, text='Draw', width=10, height=2, font=('Arial', 12))
    self.btn_draw.config(command=self.btn_draw_event, state=DISABLED)
    self.btn_draw.grid(row=1, column=1)
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

    # log
    scrollbar_log = tk.Scrollbar(self.frame_log)
    self.text_log = tk.Text(self.frame_log, font=('Arial', 12), height=18)
    scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
    self.text_log.pack(side=tk.LEFT, fill=tk.Y)
    scrollbar_log.config(command=self.text_log.yview)
    self.text_log.config(yscrollcommand=scrollbar_log.set)

    # 1v1 2v2
    battle_mode = [
      "1v1",
      "2v2"
    ]
    self.battle_stringVar = StringVar()
    self.battle_stringVar.set(battle_mode[1]) # default value
    optionMenu_battle = OptionMenu(self.frame_detect_btn, self.battle_stringVar, *battle_mode)
    optionMenu_battle.pack(fill=BOTH, expand=True)

    # detect button
    self.btn_save_extract_images = tk.Button(self.frame_detect_btn, text='Save Extract Images', width=15, height=2, font=('Arial', 10))
    self.btn_save_extract_images.config(command=self.btn_save_extract_images_event, state=DISABLED)
    self.btn_save_extract_images.pack(fill=BOTH, expand=True)
    self.btn_BM = tk.Button(self.frame_detect_btn, text='BM', width=15, height=2, font=('Arial', 10))
    self.btn_BM.config(command=self.btn_bm_event, state=DISABLED)
    self.btn_BM.pack(fill=BOTH, expand=True)

    # auto play
    self.autoPlay_booleanVar = tk.BooleanVar() 
    self.autoPlay_booleanVar.set(False)
    checkBtn_autoPlay = tk.Checkbutton(self.frame_detect_btn, text='Auto Play', var=self.autoPlay_booleanVar, pady=5) 
    checkBtn_autoPlay.pack(fill=BOTH, expand=True)

    # top Window
    self.topWindow_booleanVar = tk.BooleanVar() 
    self.topWindow_booleanVar.set(False)
    checkBtn_topWindow = tk.Checkbutton(self.frame_detect_btn, text='Top Window', var=self.topWindow_booleanVar, command=self.checkBtn_topWindow, pady=5) 
    checkBtn_topWindow.pack(fill=BOTH, expand=True)
    
    # watch AD
    self.watchAD_booleanVar = tk.BooleanVar() 
    self.watchAD_booleanVar.set(False)
    self.checkBtn_watchAD = tk.Checkbutton(self.frame_detect_btn, text='Watch AD', var=self.watchAD_booleanVar, pady=5) 
    self.checkBtn_watchAD.pack(fill=BOTH, expand=True)
    self.checkBtn_watchAD.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))
    
    # Status Label
    self.status_StringVar = StringVar()
    self.status_StringVar.set('Lobby')
    label_status = tk.Label(self.frame_detect_btn, padx=5, pady=5, textvariable=self.status_StringVar)
    label_status.pack(fill=BOTH, expand=True)

    # button
    self.btn_run = tk.Button(self.frame_btn, text='Start', width=15, height=3, font=('Arial', 12))
    self.btn_run.pack(fill=BOTH, side=LEFT, expand=True)
    self.btn_run.config(command=self.btn_run_event, state=DISABLED)
    self.isRunning = False
    self.thread_bg_task = None
    self.btn_connect = tk.Button(self.frame_btn, text='Connect', width=15, height=2, font=('Arial', 12))
    self.btn_connect.config(command=self.btn_ADB_connect_event)
    self.btn_connect.pack(fill=BOTH, side=RIGHT, expand=True)
    self.btn_init = tk.Button(self.frame_btn, text='Init', width=15, height=3, font=('Arial', 12))
    self.btn_init.config(command=self.btn_init_event, state=DISABLED)
    self.btn_init.pack(fill=BOTH, side=RIGHT, expand=True)

    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

    self.initAll()

  def initAll(self):
    self.setSettingInputField()
    self.btn_load_config_event()
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
      self.setting_stringVar[2].set(dealString(int(self.bg_task.variable.getDetectDiceMode())))
      self.setting_stringVar[3].set(dealString(self.bg_task.variable.getADBPort()))
      self.setting_stringVar[4].set(dealString(self.bg_task.variable.getBoardDiceLeftTopXY()))
      self.setting_stringVar[5].set(dealString(self.bg_task.variable.getBoardDiceOffsetXY()))
      self.setting_stringVar[6].set(dealString(self.bg_task.variable.getLevelDiceLeftXY()))
      self.setting_stringVar[7].set(dealString(self.bg_task.variable.getLevelDiceOffsetX()))
      self.setting_stringVar[8].set(dealString(self.bg_task.variable.getEmojiDialogXY()))
      self.setting_stringVar[9].set(dealString(self.bg_task.variable.getEmojiLeftXY()))
      self.setting_stringVar[10].set(dealString(self.bg_task.variable.getEmojiOffsetX()))
      self.setting_stringVar[11].set(dealString(self.bg_task.variable.getSummonDiceXY()))
      self.setting_stringVar[12].set(dealString(self.bg_task.variable.getLevelSpXY()))
      self.setting_stringVar[13].set(dealString(self.bg_task.variable.getMergeFloatLocationXY()))
      self.setting_stringVar[14].set(dealString(self.bg_task.variable.getBattleXY()))
      self.setting_stringVar[15].set(dealString(self.bg_task.variable.getADCloseXY()))
      self.setting_stringVar[16].set(dealString(self.bg_task.variable.getExtractDiceSizeWH()))
      self.setting_stringVar[17].set(dealString(self.bg_task.variable.getExtractDiceLuSizeWH()))
      self.setting_stringVar[18].set(dealString(self.bg_task.variable.getExtractSpLuSizeWH()))
      self.setting_stringVar[19].set(dealString(self.bg_task.variable.getExtractSummonLuSizeWH()))
      self.setting_stringVar[20].set(dealString(self.bg_task.variable.getExtractLevelDiceLuSizeWH()))
      self.setting_stringVar[21].set(dealString(self.bg_task.variable.getEmojiDialogWH()))
      self.setting_stringVar[22].set(dealString(self.bg_task.variable.getZoomRatio()))

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
      self.bg_task.variable.setDetectDiceMode(DetectDiceMode(dealString(self.setting_stringVar[2].get())))
      self.bg_task.variable.setADBPort(dealString(self.setting_stringVar[3].get()))
      self.bg_task.variable.setBoardDiceLeftTopXY(dealString(self.setting_stringVar[4].get()))
      self.bg_task.variable.setBoardDiceOffsetXY(dealString(self.setting_stringVar[5].get()))
      self.bg_task.variable.setLevelDiceLeftXY(dealString(self.setting_stringVar[6].get()))
      self.bg_task.variable.setLevelDiceOffsetX(dealString(self.setting_stringVar[7].get()))
      self.bg_task.variable.setEmojiDialogXY(dealString(self.setting_stringVar[8].get()))
      self.bg_task.variable.setEmojiLeftXY(dealString(self.setting_stringVar[9].get()))
      self.bg_task.variable.setEmojiOffsetX(dealString(self.setting_stringVar[10].get()))
      self.bg_task.variable.setSummonDiceXY(dealString(self.setting_stringVar[11].get()))
      self.bg_task.variable.setLevelSpXY(dealString(self.setting_stringVar[12].get()))
      self.bg_task.variable.setMergeFloatLocationXY(dealString(self.setting_stringVar[13].get()))
      self.bg_task.variable.setBattleXY(dealString(self.setting_stringVar[14].get()))
      self.bg_task.variable.setADCloseXY(dealString(self.setting_stringVar[15].get()))
      self.bg_task.variable.setExtractDiceSizeWH(dealString(self.setting_stringVar[16].get()))
      self.bg_task.variable.setExtractDiceLuSizeWH(dealString(self.setting_stringVar[17].get()))
      self.bg_task.variable.setExtractSpLuSizeWH(dealString(self.setting_stringVar[18].get()))
      self.bg_task.variable.setExtractSummonLuSizeWH(dealString(self.setting_stringVar[19].get()))
      self.bg_task.variable.setExtractLevelDiceLuSizeWH(dealString(self.setting_stringVar[20].get()))
      self.bg_task.variable.setEmojiDialogWH(dealString(self.setting_stringVar[21].get()))
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar[22].get(), float))
    
  def btn_run_event(self):
    if self.isRunning == False: # enable
      if self.bg_task is not None:
        if self.thread_bg_task is None or not self.thread_bg_task.is_alive():
          self.getSettingInputField()
          self.isRunning = True
          self.thread_bg_task = threading.Thread(target = self.run_bg_task)
          self.thread_bg_task.start()
          self.btn_run.config(text='Stop')
          self.log('=== Start Detecting ===\n')
    else: # disable
      self.btn_run.config(state=DISABLED, text='Stop...')
      self.isRunning = False
      self.log('=== Stop Detecting ===\n')

  def btn_init_event(self):
    self.log('=== Init ===\n')
    MyAction.init()

  def btn_bm_event(self):
    def bm_function():
      self.btn_BM.config(state=DISABLED, text='BM ing...')
      self.bg_task.diceControl.BMOpponent()
      self.btn_BM.config(state=NORMAL, text='BM')
    t = threading.Thread(target = bm_function)
    t.start()

  def limitImageSize(self, img):
    h,w,_ = img.shape
    height_limit = 600
    if h > height_limit:
      return cv2.resize(img, (int((height_limit/h)*w), height_limit))
    else:
      return img.copy()

  def btn_screenshot_event(self):
    self.log('=== ScreenShot ===\n')
    success, im = self.bg_task.screen.getScreenShot(self.bg_task.variable.getZoomRatio())
    if success:
      self.screenshot_image = self.bg_task.detect.Image2OpenCV(im)
      # limit
      self.screenshot_image_limit = self.limitImageSize(self.screenshot_image)
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(self.screenshot_image_limit))
  
  def btn_draw_event(self):
    self.getSettingInputField()
    labeled_screenshot = self.bg_task.detect.drawTestImage(self.screenshot_image.copy())
    # limit
    labeled_screenshot_limit = self.limitImageSize(labeled_screenshot)
    self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(labeled_screenshot_limit))

  def btn_save_config_event(self):
    self.log('=== Save Config ===\n')
    self.getSettingInputField()
    self.bg_task.variable.saveToConfigFile()
    self.checkBtn_watchAD.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))

  def btn_load_config_event(self):
    self.log('=== Load Config ===\n')
    self.bg_task.variable.loadFromConfigFile()
    self.setSettingInputField()

  def btn_save_extract_images_event(self):
    self.log('=== Save Extract Images ===\n')
    def event():
      self.btn_save_extract_images.config(state=DISABLED, text='saving...')
      if not os.path.exists('extract'):
        os.mkdir('extract')
      for i, img in enumerate(self.bg_task.detect_board_dice_img):
        self.bg_task.detect.save(img, os.path.join('extract', f'{i}.png'))
      self.btn_save_extract_images.config(state=NORMAL, text='Save Extract Images')
    threading.Thread(target = event).start()

  def changeImage(self, label: tk.Label, img):
    label.configure(image=img)
    label.image = img

  def ckeckBtn_select_dice_event(self):
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

  def checkBtn_topWindow(self):
    self.window.call('wm', 'attributes', '.', '-topmost', self.topWindow_booleanVar.get())

  def btn_ADB_connect_event(self):
    if self.bg_task.variable.getControlMode() == ControlMode.WIN32API:
      self.bg_task.getWindowID()
      self.log(f'WindowID: {self.bg_task.windowID}\n')
      self.bg_task.init()
      self.enableButton()
    elif self.bg_task.variable.getControlMode() == ControlMode.ADB:
      self.log('=== Start Connecting ===\n')
      # connect to device
      def adb_connect():
        self.btn_connect.config(state=DISABLED, text='Connecting...')
        s, r = ADB.connect(self.bg_task.variable.getADBIP(), self.bg_task.variable.getADBPort())
        self.log(s)
        self.bg_task.init()
        if r:
          self.enableButton()
          self.btn_connect.config(state=DISABLED, text='Connected')
        else:
          messagebox.showerror('Connect Error', s, parent=self.window)
          self.btn_connect.config(state=NORMAL, text='Connect')

      t = threading.Thread(target = adb_connect)
      t.start()

  def enableButton(self):
    self.btn_run.config(state=NORMAL)
    self.btn_init.config(state=NORMAL)
    self.btn_screenshot.config(state=NORMAL)
    self.btn_BM.config(state=NORMAL)
    self.btn_draw.config(state=NORMAL)
    self.btn_save_extract_images.config(state=NORMAL)

  def log(self, text):
    print(text)
    self.text_log.insert(tk.END, text)
    self.text_log.see(tk.END)  

  def run_bg_task(self):
    def stopDetect():
      self.isRunning = False
      self.btn_run.config(text='Start')
      self.log('=== Stop Detecting ===\n')

    while self.isRunning:
      # detect dice war app
      if self.bg_task.variable.getControlMode() == ControlMode.ADB:
        if not ADB.detectDiceWar(self.bg_task.variable.getADBIP(), self.bg_task.variable.getADBPort()):
          self.log("Error: Focus app is not Dice War App\n")
          stopDetect()
          break

      status_str = ['Lobby', 'Wait', 'Game', 'Finish']
      # run
      previous_status = self.bg_task.status
      
      battleMode = BattleMode.BATTLE_1V1 if self.battle_stringVar.get() == '1v1' else BattleMode.BATTLE_2V2
      self.bg_task.task(self.log, 
        self.autoPlay_booleanVar.get(), 
        self.watchAD_booleanVar.get(),
        battleMode)
      
      if previous_status != self.bg_task.status:
        self.log(f'=== Detect {status_str[int(self.bg_task.status)]} ===\n')
        self.status_StringVar.set(status_str[int(self.bg_task.status)])
      
      if self.bg_task.status == Status.LOBBY:
        if previous_status == Status.LOBBY:
          self.bg_task.diceControl.battle(battleMode)
        else:
          if not self.autoPlay_booleanVar.get():
            self.log('Detect lobby, stop detecting\n')
            stopDetect()
            break
      # update ui
      for i, name in enumerate(self.bg_task.board_dice):
        idx = self.bg_task.detect.dice_name_idx_dict[name]
        img = self.bg_task.detect.dice_image_tk_resize[idx]
        self.changeImage(self.label_board_dice[i], img)
      for i, star in enumerate(self.bg_task.board_dice_star):
        self.label_board_star[i].config(text=str(star))
      for i, img in enumerate(self.bg_task.detect_board_dice_img):
        img = self.bg_task.detect.OpenCV2TK(img)
        self.changeImage(self.label_detect_board_dice[i], img)
      self.window.update()

    # recover the text and state
    self.btn_run.config(state=NORMAL, text='Start')

  def onClosing(self):
    self.log('Closing...\n')
    self.close()
    self.window.destroy()

  def close(self):
    self.isRunning = False
    if self.bg_task.variable.getControlMode() == ControlMode.ADB:
      ADB.disconnect()

  def RUN(self):
    self.log('=== Finish Initial ===\n')
    self.window.mainloop()