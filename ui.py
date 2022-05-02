from telnetlib import STATUS
import tkinter as tk
import threading
import traceback
from functools import partial
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd

from task import *
from screen import *
from mode import *
from version import *

class UI:
  Version = '1.2.6'

  def __init__(self):
    self.window = tk.Tk()
    self.window.withdraw()

    self.bg_task = Task()

    # let the window on top
    self.window.title(f'Dice Bot {UI.Version}')

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
    self.frame_log.grid(column=0, row=2, columnspan=4)
    self.frame_detect_btn = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_detect_btn.grid(column=5, row=0, rowspan=3, sticky=N)
    self.frame_btn = tk.Frame(self.window)
    self.frame_btn.pack(expand=1, fill="x")
    self.frame_setting = tk.Frame(self.tab_setting, pady=10, height=500)
    self.frame_setting.grid(column=0, row=0, sticky='nswe')
    self.frame_setting.pack_propagate(0)
    self.frame_setting_page_btn = tk.Frame(self.tab_setting, pady=5)
    self.frame_setting_page_btn.grid(column=0, row=1)
    self.frame_setting_btn = tk.Frame(self.tab_setting, pady=10)
    self.frame_setting_btn.grid(column=0, row=2)
    self.frame_setting_view = tk.Frame(self.tab_setting, padx=20)
    self.frame_setting_view.grid(column=1, row=0, rowspan=3)
    self.tab_setting.columnconfigure(0, weight=1)
    self.tab_setting.columnconfigure(1, weight=2)

    self.setting_page_size = 3
    self.now_page_idx = 0
    self.frame_setting_pages = []
    for i in range(self.setting_page_size):
      frame_page = tk.Frame(self.frame_setting)
      if i == 0:
        frame_page.pack(fill=BOTH, expand=True)
      self.frame_setting_pages.append(frame_page)

    self.btn_previous_page = tk.Button(self.frame_setting_page_btn, text='<', width=10, height=1, font=('Arial', 8))
    self.btn_previous_page.config(command=self.btn_previous_page_event)
    self.btn_previous_page.pack(side=LEFT, padx=(0, 80))
    self.btn_previous_page.config(state=DISABLED)
    self.btn_next_page = tk.Button(self.frame_setting_page_btn, text='>', width=10, height=1, font=('Arial', 8))
    self.btn_next_page.config(command=self.btn_next_page_event)
    self.btn_next_page.pack(side=RIGHT, padx=(80, 0))
    self.btn_next_page.config(state=(DISABLED if self.now_page_idx == self.setting_page_size-1 else NORMAL))

    self.setting_stringVar = {}
    self.setting_entry = {}
    def getSettingLabel(text, row, page):
      tk.Label(self.frame_setting_pages[page], text=f'{text}: ', anchor='e', width=32, font=('Arial', 9)).grid(row=row, column=0)
      input_str = StringVar(None)
      input_field = Entry(self.frame_setting_pages[page], textvariable=input_str, width=20)
      input_field.grid(row=row, column=1)
      self.setting_stringVar[text] = input_str
      self.setting_entry[text] = input_field

    SettingLabelDict = {
      'Control Mode': 0,
      'Emulator': 0,
      'Detect Dice Mode': 0,
      'ADB Mode': 0,
      'ADB IP': 0,
      'ADB Port': 0,
      'ADB ID': 0,
      'Random Offset': 0,
      'Board Left Top XY': 1,
      'Board Dice Offset XY': 1,
      'Level Dice Left XY': 1,
      'Level Dice Offset X': 1,
      'Emoji Dialog XY': 1,
      'Emoji Left XY': 1,
      'Emoji Offset X': 1,
      'Summon Dice XY': 1,
      'Level SP XY': 1,
      'Merge Float Location XY': 1,
      'Battle XY': 1,
      'AD Close XY': 1,
      'Spell XY': 1,
      'Damage List XY': 1,
      'Extract Dice Size WH': 2,
      'Extract Dice Luminance Size WH': 2,
      'Extract SP Luminance Size WH': 2,
      'Extract Summon Luminance Size WH': 2,
      'Extract Level Dice Luminance Size WH': 2,
      'Extract Spell Luminance Size WH': 2,
      'Emoji Dialog WH': 2,
      'Zoom Ratio': 0,
      'Detect Delay': 0,
      'Restart Delay': 0,
    }
    for i,(label,page) in enumerate(SettingLabelDict.items()):
      getSettingLabel(label, i, page)

    # save config
    btn_save_config = tk.Button(self.frame_setting_btn, text='Save', width=10, height=2, font=('Arial', 12))
    btn_save_config.config(command=self.btn_save_config_event)
    btn_save_config.grid(row=0, column=0)
    
    # load config
    btn_load_config = tk.Button(self.frame_setting_btn, text='Load', width=10, height=2, font=('Arial', 12))
    btn_load_config.config(command=self.btn_load_config_event)
    btn_load_config.grid(row=0, column=1)
    
    # screenshot
    self.btn_screenshot = tk.Button(self.frame_setting_btn, text='ScreenShot', width=10, height=2, font=('Arial', 12))
    self.btn_screenshot.config(command=self.btn_screenshot_event, state=DISABLED)
    self.btn_screenshot.grid(row=0, column=2)
    self.label_screenshot = tk.Label(self.frame_setting_view)
    self.label_screenshot.pack(fill=BOTH)
    
    # draw
    self.btn_draw = tk.Button(self.frame_setting_btn, text='Draw', width=10, height=2, font=('Arial', 12))
    self.btn_draw.config(command=self.btn_draw_event, state=DISABLED)
    self.btn_draw.grid(row=0, column=3)
    
    # save screenshot
    self.btn_save_screenshot = tk.Button(self.frame_setting_btn, text='Save\nScreenShot', width=10, height=2, font=('Arial', 12))
    self.btn_save_screenshot.config(command=self.btn_save_screenshot_event, state=DISABLED)
    self.btn_save_screenshot.grid(row=1, column=0)

    # load screenshot
    self.btn_load_screenshot = tk.Button(self.frame_setting_btn, text='Load\nScreenShot', width=10, height=2, font=('Arial', 12))
    self.btn_load_screenshot.config(command=self.btn_load_screenshot_event, state=DISABLED)
    self.btn_load_screenshot.grid(row=1, column=1)
    
    # detect
    self.btn_detect = tk.Button(self.frame_setting_btn, text='Detect', width=10, height=2, font=('Arial', 12))
    self.btn_detect.config(command=self.btn_detect_event, state=DISABLED)
    self.btn_detect.grid(row=1, column=2)

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
    self.select_dice_label = []
    self.select_dice_name = [""] * self.bg_task.variable.getPartyDiceSize()
    for i in range(self.bg_task.variable.getPartyDiceSize()):
      label = tk.Label(self.frame_select_dice, padx=5, pady=10)
      event = partial(self.press_select_dice_event, i)
      label.bind('<Button-1>', event)
      self.changeImage(label, self.bg_task.detect.dice_image_tk_resize[self.bg_task.detect.dice_name_idx_dict['Blank']])
      label.pack(side = LEFT)
      self.select_dice_label.append(label)

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
    optionMenu_battle.pack(fill=BOTH, expand=True, side=TOP)

    # detect button
    self.btn_save_extract_images = tk.Button(self.frame_detect_btn, text='Save Extract Images', width=15, height=2, font=('Arial', 10))
    self.btn_save_extract_images.config(command=self.btn_save_extract_images_event, state=DISABLED)
    self.btn_save_extract_images.pack(fill=BOTH, expand=True)
    self.btn_BM = tk.Button(self.frame_detect_btn, text='BM', width=15, height=2, font=('Arial', 10))
    self.btn_BM.config(command=self.btn_bm_event, state=DISABLED)
    self.btn_BM.pack(fill=BOTH, expand=True, side=TOP)

    # auto play
    self.autoPlay_booleanVar = tk.BooleanVar() 
    self.autoPlay_booleanVar.set(False)
    checkBtn_autoPlay = tk.Checkbutton(self.frame_detect_btn, text='Auto Play', var=self.autoPlay_booleanVar, pady=5) 
    checkBtn_autoPlay.pack(fill=BOTH, expand=True, side=TOP)

    # top Window
    self.topWindow_booleanVar = tk.BooleanVar() 
    self.topWindow_booleanVar.set(False)
    checkBtn_topWindow = tk.Checkbutton(self.frame_detect_btn, text='Top Window', var=self.topWindow_booleanVar, command=self.checkBtn_topWindow, pady=5) 
    checkBtn_topWindow.pack(fill=BOTH, expand=True, side=TOP)
    
    # watch AD
    self.watchAD_booleanVar = tk.BooleanVar() 
    self.watchAD_booleanVar.set(False)
    self.checkBtn_watchAD = tk.Checkbutton(self.frame_detect_btn, text='Watch AD', var=self.watchAD_booleanVar, pady=5) 
    self.checkBtn_watchAD.pack(fill=BOTH, expand=True, side=TOP)
    self.checkBtn_watchAD.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))

    # restart App
    self.restartApp_booleanVar = tk.BooleanVar() 
    self.restartApp_booleanVar.set(False)
    self.checkBtn_restartApp = tk.Checkbutton(self.frame_detect_btn, text='Restart App', var=self.restartApp_booleanVar, pady=5) 
    self.checkBtn_restartApp.pack(fill=BOTH, expand=True, side=TOP)
    self.checkBtn_restartApp.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))
    
    # Status Label
    self.status_StringVar = StringVar()
    self.status_StringVar.set('Lobby')
    label_status = tk.Label(self.frame_detect_btn, padx=5, pady=5, textvariable=self.status_StringVar)
    label_status.pack(fill=BOTH, expand=True, side=TOP)

    # Result Label
    self.result_StringVar = StringVar()
    self.result_StringVar.set('0 / 0')
    label_result = tk.Label(self.frame_detect_btn, padx=5, pady=5, textvariable=self.result_StringVar)
    label_result.pack(fill=BOTH, expand=True, side=TOP)

    # button
    self.btn_run = tk.Button(self.frame_btn, text='Start', width=15, height=3, font=('Arial', 12))
    self.btn_run.pack(fill=BOTH, side=LEFT, expand=True)
    self.btn_run.config(command=self.btn_run_event, state=DISABLED)
    self.isRunning = False
    self.thread_bg_task = None
    self.btn_connect = tk.Button(self.frame_btn, text='Connect', width=15, height=2, font=('Arial', 12))
    self.btn_connect.config(command=self.btn_ADB_connect_event)
    self.btn_connect.pack(fill=BOTH, side=RIGHT, expand=True)
    self.isConnected = False
    self.btn_result = tk.Button(self.frame_btn, text='Reset Result', width=15, height=3, font=('Arial', 12))
    self.btn_result.config(command=self.btn_reset_event, state=DISABLED)
    self.btn_result.pack(fill=BOTH, side=RIGHT, expand=True)

    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

    self.initAll()

  def initAll(self):
    if os.path.exists(self.bg_task.variable.getUpdateFileName()):
      with open(self.bg_task.variable.getUpdateFileName(), 'r') as f:
        lines = f.readlines()
        self.text_log.insert(tk.END, '========================================\n')
        for line in lines:
          if len(line.strip()) != 0:
            self.text_log.insert(tk.END, line)
        self.text_log.insert(tk.END, '========================================\n')
        self.text_log.see(tk.END)  
    self.setSettingInputField()
    self.btn_load_config_event()
    self.setSelectDiceField()

    self.window.deiconify()

    # check version
    try:
      isLatest, latest_version = Version.checkLatest(UI.Version)
      if isLatest == False:
        self.log(f'Find New Version {latest_version} !!!\n')
        messagebox.showinfo('New Version', f'Find New Version {latest_version} !!!', parent=self.window)
    except:
      self.log(f'{traceback.format_exc()}\n')

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
      self.setting_stringVar['Control Mode'].set(dealString(int(self.bg_task.variable.getControlMode())))
      self.setting_stringVar['Emulator'].set(dealString(int(self.bg_task.variable.getEmulatorMode())))
      self.setting_stringVar['Detect Dice Mode'].set(dealString(int(self.bg_task.variable.getDetectDiceMode())))
      self.setting_stringVar['ADB Mode'].set(dealString(int(self.bg_task.variable.getADBMode())))
      self.setting_stringVar['ADB IP'].set(self.bg_task.variable.getADBIP())
      self.setting_stringVar['ADB Port'].set(dealString(self.bg_task.variable.getADBPort()))
      self.setting_stringVar['ADB ID'].set(self.bg_task.variable.getADBID())
      self.setting_stringVar['Random Offset'].set(dealString(self.bg_task.variable.getRandomOffset()))
      self.setting_stringVar['Board Left Top XY'].set(dealString(self.bg_task.variable.getBoardDiceLeftTopXY()))
      self.setting_stringVar['Board Dice Offset XY'].set(dealString(self.bg_task.variable.getBoardDiceOffsetXY()))
      self.setting_stringVar['Level Dice Left XY'].set(dealString(self.bg_task.variable.getLevelDiceLeftXY()))
      self.setting_stringVar['Level Dice Offset X'].set(dealString(self.bg_task.variable.getLevelDiceOffsetX()))
      self.setting_stringVar['Emoji Dialog XY'].set(dealString(self.bg_task.variable.getEmojiDialogXY()))
      self.setting_stringVar['Emoji Left XY'].set(dealString(self.bg_task.variable.getEmojiLeftXY()))
      self.setting_stringVar['Emoji Offset X'].set(dealString(self.bg_task.variable.getEmojiOffsetX()))
      self.setting_stringVar['Summon Dice XY'].set(dealString(self.bg_task.variable.getSummonDiceXY()))
      self.setting_stringVar['Level SP XY'].set(dealString(self.bg_task.variable.getLevelSpXY()))
      self.setting_stringVar['Merge Float Location XY'].set(dealString(self.bg_task.variable.getMergeFloatLocationXY()))
      self.setting_stringVar['Battle XY'].set(dealString(self.bg_task.variable.getBattleXY()))
      self.setting_stringVar['AD Close XY'].set(dealString(self.bg_task.variable.getADCloseXY()))
      self.setting_stringVar['Spell XY'].set(dealString(self.bg_task.variable.getSpellXY()))
      self.setting_stringVar['Damage List XY'].set(dealString(self.bg_task.variable.getDamageListXY()))
      self.setting_stringVar['Extract Dice Size WH'].set(dealString(self.bg_task.variable.getExtractDiceSizeWH()))
      self.setting_stringVar['Extract Dice Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractDiceLuSizeWH()))
      self.setting_stringVar['Extract SP Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractSpLuSizeWH()))
      self.setting_stringVar['Extract Summon Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractSummonLuSizeWH()))
      self.setting_stringVar['Extract Level Dice Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractLevelDiceLuSizeWH()))
      self.setting_stringVar['Extract Spell Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractSpellLuSizeWH()))
      self.setting_stringVar['Emoji Dialog WH'].set(dealString(self.bg_task.variable.getEmojiDialogWH()))
      self.setting_stringVar['Zoom Ratio'].set(dealString(self.bg_task.variable.getZoomRatio()))
      self.setting_stringVar['Detect Delay'].set(dealString(self.bg_task.variable.getDetectDelay()))
      self.setting_stringVar['Restart Delay'].set(dealString(self.bg_task.variable.getRestartDelay()))

  def getSettingInputField(self):
    if self.bg_task is None:
      raise Exception('getSettingInputField:: Need to set task variable first')
    else:
      def dealString(s, type = int):
        s_split = s.split(' ')
        int_list = [type(x) for x in s_split]
        return int_list[0] if len(int_list) == 1 else tuple(int_list)
      self.bg_task.variable.setControlMode(ControlMode(dealString(self.setting_stringVar['Control Mode'].get())))
      self.bg_task.variable.setEmulatorMode(Emulator(dealString(self.setting_stringVar['Emulator'].get())))
      self.bg_task.variable.setDetectDiceMode(DetectDiceMode(dealString(self.setting_stringVar['Detect Dice Mode'].get())))
      self.bg_task.variable.setADBMode(ADBMode(dealString(self.setting_stringVar['ADB Mode'].get())))
      self.bg_task.variable.setADBIP(self.setting_stringVar['ADB IP'].get())
      self.bg_task.variable.setADBPort(dealString(self.setting_stringVar['ADB Port'].get()))
      self.bg_task.variable.setADBID(self.setting_stringVar['ADB ID'].get())
      self.bg_task.variable.setRandomOffset(dealString(self.setting_stringVar['Random Offset'].get()))
      self.bg_task.variable.setBoardDiceLeftTopXY(dealString(self.setting_stringVar['Board Left Top XY'].get()))
      self.bg_task.variable.setBoardDiceOffsetXY(dealString(self.setting_stringVar['Board Dice Offset XY'].get()))
      self.bg_task.variable.setLevelDiceLeftXY(dealString(self.setting_stringVar['Level Dice Left XY'].get()))
      self.bg_task.variable.setLevelDiceOffsetX(dealString(self.setting_stringVar['Level Dice Offset X'].get()))
      self.bg_task.variable.setEmojiDialogXY(dealString(self.setting_stringVar['Emoji Dialog XY'].get()))
      self.bg_task.variable.setEmojiLeftXY(dealString(self.setting_stringVar['Emoji Left XY'].get()))
      self.bg_task.variable.setEmojiOffsetX(dealString(self.setting_stringVar['Emoji Offset X'].get()))
      self.bg_task.variable.setSummonDiceXY(dealString(self.setting_stringVar['Summon Dice XY'].get()))
      self.bg_task.variable.setLevelSpXY(dealString(self.setting_stringVar['Level SP XY'].get()))
      self.bg_task.variable.setMergeFloatLocationXY(dealString(self.setting_stringVar['Merge Float Location XY'].get()))
      self.bg_task.variable.setBattleXY(dealString(self.setting_stringVar['Battle XY'].get()))
      self.bg_task.variable.setADCloseXY(dealString(self.setting_stringVar['AD Close XY'].get()))
      self.bg_task.variable.setSpellXY(dealString(self.setting_stringVar['Spell XY'].get()))
      self.bg_task.variable.setDamageListXY(dealString(self.setting_stringVar['Damage List XY'].get()))
      self.bg_task.variable.setExtractDiceSizeWH(dealString(self.setting_stringVar['Extract Dice Size WH'].get()))
      self.bg_task.variable.setExtractDiceLuSizeWH(dealString(self.setting_stringVar['Extract Dice Luminance Size WH'].get()))
      self.bg_task.variable.setExtractSpLuSizeWH(dealString(self.setting_stringVar['Extract SP Luminance Size WH'].get()))
      self.bg_task.variable.setExtractSummonLuSizeWH(dealString(self.setting_stringVar['Extract Summon Luminance Size WH'].get()))
      self.bg_task.variable.setExtractLevelDiceLuSizeWH(dealString(self.setting_stringVar['Extract Level Dice Luminance Size WH'].get()))
      self.bg_task.variable.setExtractSpellLuSizeWH(dealString(self.setting_stringVar['Extract Spell Luminance Size WH'].get()))
      self.bg_task.variable.setEmojiDialogWH(dealString(self.setting_stringVar['Emoji Dialog WH'].get()))
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar['Zoom Ratio'].get(), float))
      self.bg_task.variable.setDetectDelay(dealString(self.setting_stringVar['Detect Delay'].get(), float))
      self.bg_task.variable.setRestartDelay(dealString(self.setting_stringVar['Restart Delay'].get(), float))
    
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

  def btn_reset_event(self):
    self.log('=== Reset Result ===\n')
    self.result_StringVar.set('0 / 0')

  def btn_bm_event(self):
    def bm_function():
      self.btn_BM.config(state=DISABLED, text='BM ing...')
      self.bg_task.diceControl.BMOpponent()
      self.btn_BM.config(state=NORMAL, text='BM')
    t = threading.Thread(target = bm_function)
    t.start()

  def btn_next_page_event(self):
    self.frame_setting_pages[self.now_page_idx].pack_forget()
    self.now_page_idx += 1
    self.frame_setting_pages[self.now_page_idx].pack(fill=BOTH, expand=True)
    if self.now_page_idx == self.setting_page_size - 1:
      self.btn_next_page.config(state=DISABLED)
    self.btn_previous_page.config(state=NORMAL)

  def btn_previous_page_event(self):
    self.frame_setting_pages[self.now_page_idx].pack_forget()
    self.now_page_idx -= 1
    self.frame_setting_pages[self.now_page_idx].pack(fill=BOTH, expand=True)
    if self.now_page_idx == 0:
      self.btn_previous_page.config(state=DISABLED)
    self.btn_next_page.config(state=NORMAL)

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
    self.checkBtn_restartApp.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))

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

  def btn_save_screenshot_event(self):
    self.log('=== Save Screenshot Image ===\n')
    def event():
      self.btn_save_screenshot.config(state=DISABLED, text='saving...')
      if not os.path.exists('extract'):
        os.mkdir('extract')
      try:
        filename = fd.asksaveasfilename(
          initialfile='screenshot.png',
          initialdir= './extract',
          defaultextension=".png",
          filetypes=[("Image files","*.png"),("All Files","*.*")])
        if not filename.endswith('.png'):
          filename += '.png'
        self.log(f'FilePath: {filename}\n')

        self.bg_task.detect.save(self.screenshot_image, filename)
      except AttributeError:
        messagebox.showerror('Save Error', 'Need screenshot first', parent=self.window)
      self.btn_save_screenshot.config(state=NORMAL, text='Save\nScreenShot')
    threading.Thread(target = event).start()

  def btn_load_screenshot_event(self):
    self.log('=== Load Screenshot Image ===\n')
    filetypes = (
      ('Image files', '*.png'),
      ('All files', '*.*')
    )
    initFolder = './extract'
    if not os.path.exists('extract'):
      initFolder = './'
    filename = fd.askopenfilename(
      title='Select a image file',
      initialdir=initFolder,
      filetypes=filetypes)
    self.log(f'FilePath: {filename}\n')

    try:
      # read image
      self.screenshot_image = self.bg_task.detect.load(filename)
      # limit
      self.screenshot_image_limit = self.limitImageSize(self.screenshot_image)
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(self.screenshot_image_limit))
    except Exception as e:
      messagebox.showerror('Load Error', traceback.format_exc(), parent=self.window)

  def btn_detect_event(self):
    self.log('=== Detect Screenshot ===\n')
    def event():
      self.btn_detect.config(state=DISABLED, text='Detect...')
      try:
        enable_result = self.bg_task.detect.detectEnable(self.screenshot_image)
        status_result = self.bg_task.detect.detectStatus(self.screenshot_image)
        string = '\n'.join([f'{key}: {val}' for key, val in enable_result.items()] + 
          [f'{key}: {val}' for key, val in status_result.items()])
        messagebox.showinfo('Detect Result', string, parent=self.window)
      except:
        messagebox.showerror('Detect Error', 'Need screenshot first', parent=self.window)
      self.btn_detect.config(state=NORMAL, text='Detect')
    threading.Thread(target = event).start()

  def changeImage(self, label: tk.Label, img):
    label.configure(image=img)
    label.image = img
    label.update()

  def press_select_dice_event(self, idx, _):
    # pop window
    select_dice_window = Toplevel(self.window)
    select_dice_window.withdraw()
    select_dice_window.title("Select Dice")

    for i,(name,img) in enumerate(zip(self.bg_task.detect.dice_name, self.bg_task.detect.dice_image_tk_resize)):
      label_text = tk.Label(select_dice_window, text=name)
      label_img = tk.Label(select_dice_window)
      self.changeImage(label_img, img)
      label_img.grid(row=(i//8)*2, column=i%8, sticky="W")
      label_text.grid(row=(i//8)*2+1, column=i%8, sticky="W")

      def update(update_name, update_img, _):
        self.select_dice_name[idx] = update_name
        self.changeImage(self.select_dice_label[idx], update_img)
        self.frame_select_dice.update()
        select_dice_window.destroy()
        self.getSelectDiceField()

      event = partial(update, name, img)

      label_img.bind('<Button-1>', event)
      label_text.bind('<Button-1>', event)

    select_dice_window.wm_transient(self.window)
    select_dice_window.deiconify()
    
  def getSelectDiceField(self):
    self.bg_task.variable.setDiceParty(self.select_dice_name)

  def setSelectDiceField(self):
    for i,dice in enumerate(self.bg_task.variable.getDiceParty()):
      self.select_dice_name[i] = dice
      dice_idx = self.bg_task.detect.dice_name_idx_dict[dice]
      self.changeImage(self.select_dice_label[i], self.bg_task.detect.dice_image_tk_resize[dice_idx])

  def checkBtn_topWindow(self):
    self.window.call('wm', 'attributes', '.', '-topmost', self.topWindow_booleanVar.get())

  def btn_ADB_connect_event(self):
    if self.isConnected == False:
      if self.bg_task.variable.getControlMode() == ControlMode.WIN32API:
        self.btn_connect.config(state=DISABLED, text='Connecting...')
        try:
          self.bg_task.getWindowID()
          self.log(f'WindowID: {self.bg_task.windowID}\n')
          self.bg_task.init()
          self.enableButton()
          self.btn_connect.config(state=NORMAL, text='Disconnect')
          self.isConnected = True
          # disable control mode setting field
          self.setting_entry['Control Mode'].config(state=DISABLED)
        except Exception as error:
          messagebox.showerror('Connect Error', error, parent=self.window)
          self.btn_connect.config(state=NORMAL, text='Connect')

      elif self.bg_task.variable.getControlMode() == ControlMode.ADB:
        self.log('=== Start Connecting ===\n')
        # connect to device
        def adb_connect():
          self.btn_connect.config(state=DISABLED, text='Connecting...')
          
          # initial value
          r = True
          if self.bg_task.variable.getADBMode() == ADBMode.IP:
            s, r = ADB.connect(self.bg_task.variable.getADBIP(), self.bg_task.variable.getADBPort())
            self.log(s)
          elif self.bg_task.variable.getADBMode() == ADBMode.ID:
            self.log('Use device ID, skip connection\n')
          if r: # success
            self.bg_task.init()
            self.enableButton()
            self.btn_connect.config(state=NORMAL, text='Disconnect')
            self.isConnected = True
            # disable control mode setting field
            self.setting_entry['Control Mode'].config(state=DISABLED)
          else:
            messagebox.showerror('Connect Error', s, parent=self.window)
            self.btn_connect.config(state=NORMAL, text='Connect')

        t = threading.Thread(target = adb_connect)
        t.start()
    else:
      self.log('=== Disconnecting ===\n')
      self.isConnected = False
      # enable control mode setting field
      self.setting_entry['Control Mode'].config(state=NORMAL)
      if self.bg_task.variable.getControlMode() == ControlMode.WIN32API:
        self.btn_connect.config(state=NORMAL, text='Connect')
      elif self.bg_task.variable.getControlMode() == ControlMode.ADB:
        # disconnect
        def adb_disconnect():
          self.btn_connect.config(state=DISABLED, text='Disconnecting...')
          ADB.disconnect()
          self.btn_connect.config(state=NORMAL, text='Connect')

        threading.Thread(target = adb_disconnect).start()

  def enableButton(self):
    self.btn_run.config(state=NORMAL)
    self.btn_result.config(state=NORMAL)
    self.btn_screenshot.config(state=NORMAL)
    self.btn_BM.config(state=NORMAL)
    self.btn_draw.config(state=NORMAL)
    self.btn_save_screenshot.config(state=NORMAL)
    self.btn_load_screenshot.config(state=NORMAL)
    self.btn_detect.config(state=NORMAL)
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
        if self.bg_task.variable.getADBMode() == ADBMode.IP:
          inDiceWar = ADB.detectDiceWar(f"{self.bg_task.variable.getADBIP()}:{self.bg_task.variable.getADBPort()}")
        elif self.bg_task.variable.getADBMode() == ADBMode.ID:
          inDiceWar = ADB.detectDiceWar(self.bg_task.variable.getADBID())
        if not inDiceWar:
          self.log("Error: Focus app is not Dice War App\n")
          if self.restartApp_booleanVar.get() == True:
            self.log(f"Info: Restart app and continue after {self.bg_task.variable.getRestartDelay()} seconds\n")
            if self.bg_task.variable.getADBMode() == ADBMode.IP:
              ADB.restart(f"{self.bg_task.variable.getADBIP()}:{self.bg_task.variable.getADBPort()}")
            elif self.bg_task.variable.getADBMode() == ADBMode.ID:
              ADB.restart(self.bg_task.variable.getADBID())
            time.sleep(self.bg_task.variable.getRestartDelay()) # wait for delay
          else:
            stopDetect()
            break

      previous_status = self.bg_task.status

      # run
      try:
        battleMode = BattleMode.BATTLE_1V1 if self.battle_stringVar.get() == '1v1' else BattleMode.BATTLE_2V2
        self.bg_task.task(self.log, 
          self.autoPlay_booleanVar.get(), 
          self.watchAD_booleanVar.get(),
          battleMode)
      except Exception:
        self.log(f'{traceback.format_exc()}\n')
        stopDetect()
        break
      
      # status changed
      if previous_status != self.bg_task.status:
        status_str = ['Lobby', 'Wait', 'Game', 'Finish', 'Trophy']
        self.log(f'=== Detect {status_str[int(self.bg_task.status)]} ===\n')
        self.status_StringVar.set(status_str[int(self.bg_task.status)])

        # record result
        if self.bg_task.status == Status.FINISH:
          win = int(self.result_StringVar.get().split('/')[0])
          lose = int(self.result_StringVar.get().split('/')[1])
          if self.bg_task.result == True:
            win += 1
          else:
            lose += 1
          self.result_StringVar.set(f'{win} / {lose}')
      
      if self.bg_task.status == Status.LOBBY:
        # initial
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

      time.sleep(self.bg_task.variable.getDetectDelay())

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