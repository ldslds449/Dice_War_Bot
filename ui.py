import tkinter as tk
import threading
import traceback
import win32clipboard
import matplotlib
import gc
import ctypes
from io import BytesIO
from functools import partial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
  FigureCanvasTkAgg,
  NavigationToolbar2Tk
)
from scipy.ndimage.filters import uniform_filter1d

from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd

from task import *
from screen import *
from mode import *
from version import *
from draw import *
from resource import *

class UI:

  def __init__(self):
    self.window = tk.Tk()
    self.window.withdraw()
    self.window.iconbitmap("image/icon.ico")

    myappid = f"dice_bot.{Program_Version}" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    self.bg_task = Task()

    # let the window on top
    self.window.title(f'Dice Bot {Program_Version}')
    # call onClosing in when closing the window
    self.window.protocol("WM_DELETE_WINDOW", self.onClosing)

    zero_img = tk.PhotoImage()

    # tab
    self.tabControl = ttk.Notebook(self.window)

    self.tab_detect = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_detect, text='Detect')
    self.tab_setting = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_setting, text='Setting')
    self.tab_statistic = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_statistic, text='Statistic')
    self.tab_trophy = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_trophy, text='Trophy')
    self.tab_test = ttk.Frame(self.tabControl)
    self.tabControl.add(self.tab_test, text='Test')

    self.tabControl.pack(expand=1, fill="both")
    self.tabControl.bind('<<NotebookTabChanged>>', self.updateDraw)

    # frame
    self.frame_board = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_board.grid(column=0, row=0, columnspan=2)
    self.frame_screenshot = tk.Frame(self.tab_detect)
    self.frame_screenshot.grid(column=2, row=0, columnspan=2)
    self.frame_select_dice = tk.Frame(self.tab_detect, padx=20)
    self.frame_select_dice.grid(column=0, row=1, columnspan=1)
    self.frame_dashboard = tk.Frame(self.tab_detect)
    self.frame_dashboard.grid(column=1, row=1, columnspan=3)
    self.frame_log = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_log.grid(column=0, row=2, columnspan=4, sticky='we')
    self.frame_screen = tk.Frame(self.tab_detect)
    self.frame_screen.grid(column=5, row=0, rowspan=3, sticky='ns')
    self.frame_detect_btn = tk.Frame(self.tab_detect, pady=10, padx=10)
    self.frame_detect_btn.grid(column=4, row=0, rowspan=3, sticky='ns')
    self.frame_setting = tk.Frame(self.tab_setting, pady=10)
    self.frame_setting.grid(column=0, row=0, sticky='nswe')
    self.frame_setting_page_btn = tk.Frame(self.tab_setting, pady=5)
    self.frame_setting_page_btn.grid(column=0, row=1)
    self.frame_setting_btn = tk.Frame(self.tab_setting, pady=10)
    self.frame_setting_btn.grid(column=0, row=2)
    self.frame_setting_view = tk.Frame(self.tab_setting, padx=20)
    self.frame_setting_view.grid(column=1, row=0, rowspan=3)
    self.tab_setting.columnconfigure(0, weight=1)
    self.tab_setting.columnconfigure(1, weight=2)
    self.frame_statistic_chart = tk.Frame(self.tab_statistic)
    self.frame_statistic_chart.pack(side=LEFT, fill="both")
    self.frame_statistic_info = tk.Frame(self.tab_statistic, padx=20)
    self.frame_statistic_info.pack(side=LEFT, fill="both")
    self.frame_line_chart = tk.Frame(self.tab_trophy)
    self.frame_line_chart.pack(side=LEFT, fill="both")
    self.frame_line_info = tk.Frame(self.tab_trophy, padx=20, pady=10)
    self.frame_line_info.pack(side=LEFT, fill="both")
    self.frame_test_view = tk.Frame(self.tab_test, padx=20, pady=20)
    self.frame_test_view.grid(column=0, row=0)
    self.frame_test_btn = tk.Frame(self.tab_test, padx=20)
    self.frame_test_btn.grid(column=0, row=1)
    

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
      'Detect Star Mode': 0,
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
      'Merge Float Location XY': 1,
      'Battle XY': 1,
      'AD Close XY': 1,
      'Spell XY': 1,
      'Damage List XY': 1,
      'Extract Dice Size WH': 2,
      'Extract Dice Luminance Size WH': 2,
      'Extract Summon Luminance Size WH': 2,
      'Extract Level Dice Luminance Size WH': 2,
      'Extract Spell Luminance Size WH': 2,
      'Emoji Dialog WH': 2,
      'Zoom Ratio': 0,
      'Detect Delay': 0,
      'Restart Delay': 0,
      'Screenshot Delay': 0,
      'Freeze Threshold': 0,
      'Focus Threshold': 0,
      'Party List 1v1 Left XY': 1,
      'Party List 1v1 Offset X': 1,
      'Extract Party List 1v1 Size WH': 2,
      'Trophy Left Top XY': 1,
      'Extract Trophy Size WH': 2,
      'Line Notify Token': 0,
      'Check Point Start XY': 1,
      'Check Point End XY': 1,
      'Wave Left Top XY': 1,
      'Extract Wave Size WH': 2,
      'Max FPS': 0,
      'BitRate': 0,
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
    self.label_screenshot = tk.Label(self.frame_setting_view, image=zero_img)
    self.label_screenshot.config(width=350, height=600)
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
    self.btn_load_screenshot.config(command=self.btn_load_screenshot_event)
    self.btn_load_screenshot.grid(row=1, column=1)
    
    # detect
    self.btn_detect = tk.Button(self.frame_setting_btn, text='Detect', width=10, height=2, font=('Arial', 12))
    self.btn_detect.config(command=self.btn_detect_event, state=DISABLED)
    self.btn_detect.grid(row=1, column=2)

    # board
    self.label_board_dice = []
    self.label_board_star = []
    for i in range(15):
      label = tk.Label(self.frame_board, image=zero_img, padx=5, pady=5)
      label.config(width=self.bg_task.detect.resize_size[0], height=self.bg_task.detect.resize_size[1])
      label.grid(row=i//5, column=(i%5)*2)
      self.label_board_dice.append(label)
      label = tk.Label(self.frame_board, padx=5, pady=5)
      label.config(width=2)
      label.grid(row=i//5, column=(i%5)*2+1)
      self.label_board_star.append(label)

    # screenshot
    self.label_detect_board_dice = []
    for i in range(15):
      label = tk.Label(self.frame_screenshot, image=zero_img, padx=5, pady=5)
      label.config(width=self.bg_task.detect.resize_size[0], height=self.bg_task.detect.resize_size[1])
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

    # dashboard
    self.frame_dashboard.grid_columnconfigure(0, minsize=100)
    self.frame_dashboard.grid_columnconfigure(1, minsize=180)
    ## cpu
    self.cpu_StringVar = StringVar()
    self.cpu_StringVar.set('CPU: --')
    label_cpu = tk.Label(self.frame_dashboard, textvariable=self.cpu_StringVar, anchor="w", justify=LEFT)
    label_cpu.grid(row=0, column=0)
    ## memory
    self.mem_StringVar = StringVar()
    self.mem_StringVar.set('MEM: --')
    label_mem = tk.Label(self.frame_dashboard, textvariable=self.mem_StringVar, anchor="w", justify=LEFT)
    label_mem.grid(row=1, column=0)
    ## elapsed time
    self.last_update_time_stamp = None
    self.elapsed_time_StringVar = StringVar()
    self.elapsed_time_StringVar.set('Elapsed Time: ------')
    label_elapsed_time = tk.Label(self.frame_dashboard, textvariable=self.elapsed_time_StringVar, anchor="w", justify=LEFT)
    label_elapsed_time.grid(row=0, column=1)
    ## wave
    self.wave_StringVar = StringVar()
    self.wave_StringVar.set('Wave: --')
    label_wave = tk.Label(self.frame_dashboard, textvariable=self.wave_StringVar, anchor="w", justify=LEFT)
    label_wave.grid(row=1, column=1)

    # log
    scrollbar_log_y = tk.Scrollbar(self.frame_log)
    scrollbar_log_x = tk.Scrollbar(self.frame_log, orient='horizontal')
    self.text_log = tk.Text(self.frame_log, font=('Arial', 12), height=18, width=48)
    scrollbar_log_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_log_x.pack(side=tk.BOTTOM, fill=tk.X)
    self.text_log.pack(side=tk.LEFT, fill=BOTH, expand=True)
    scrollbar_log_y.config(command=self.text_log.yview)
    scrollbar_log_x.config(command=self.text_log.xview)
    self.text_log.config(yscrollcommand=scrollbar_log_y.set, xscrollcommand=scrollbar_log_x.set)

    # screen
    self.label_screen = tk.Label(self.frame_screen, image=zero_img)
    self.label_screen.pack(fill=BOTH, expand=True)
    self.label_screen.bind('<Button-1>', self.label_screen_click_event)
    self.label_screen.bind('<B1-Motion>', self.label_screen_move_event)
    self.label_screen.bind('<ButtonRelease-1>', self.label_screen_release_event)
    self.label_screen.bind('<Button-2>', self.label_screen_click_event)
    self.label_screen.bind('<Button-3>', self.label_screen_click_event)
    self.label_screen.bind('<Leave>', self.label_screen_leave_event)

    # 1v1 2v2
    battle_mode = [
      "1v1",
      "2v2",
      "Arcade"
    ]
    self.battle_stringVar = StringVar()
    optionMenu_battle = OptionMenu(self.frame_detect_btn, self.battle_stringVar, *battle_mode)
    optionMenu_battle.pack(fill=BOTH, expand=True, side=TOP)

    # detect button
    self.btn_save_extract_images = tk.Button(self.frame_detect_btn, text='Save Extract Images', width=15, height=2, font=('Arial', 10))
    self.btn_save_extract_images.config(command=self.btn_save_extract_images_event, state=DISABLED)
    self.btn_save_extract_images.pack(fill=BOTH, expand=True)
    frame_function = tk.Frame(self.frame_detect_btn)
    frame_function.pack(fill=BOTH, expand=True, side=TOP)
    frame_function.columnconfigure(0, weight=1)
    frame_function.columnconfigure(1, weight=1)
    self.btn_BM = tk.Button(frame_function, text='BM', height=2, font=('Arial', 10))
    self.btn_BM.config(command=self.btn_bm_event, state=DISABLED)
    self.btn_BM.grid(row=0, column=0, sticky='ewns')
    self.btn_result = tk.Button(frame_function, text='Reset\nResult', height=2, font=('Arial', 10))
    self.btn_result.config(command=self.btn_reset_event, state=NORMAL)
    self.btn_result.grid(row=0, column=1, sticky='ewns')
    self.btn_share_party = tk.Button(frame_function, text='Share\nParty', height=2, font=('Arial', 10))
    self.btn_share_party.config(command=self.btn_share_party_event, state=NORMAL)
    self.btn_share_party.grid(row=1, column=0, sticky='ewns')
    self.btn_share_board = tk.Button(frame_function, text='Share\nBoard', height=2, font=('Arial', 10))
    self.btn_share_board.config(command=self.btn_share_board_event, state=DISABLED)
    self.btn_share_board.grid(row=1, column=1, sticky='ewns')

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

    # notify result
    self.notifyResult_booleanVar = tk.BooleanVar() 
    self.notifyResult_booleanVar.set(False)
    self.checkBtn_notifyResult = tk.Checkbutton(self.frame_detect_btn, text='Notify Result', var=self.notifyResult_booleanVar, pady=5) 
    self.checkBtn_notifyResult.pack(fill=BOTH, expand=True, side=TOP)
    self.checkBtn_notifyResult.config(state=NORMAL)

    # dev mode
    self.devMode_booleanVar = tk.BooleanVar() 
    self.devMode_booleanVar.set(False)
    self.checkBtn_devMode = tk.Checkbutton(self.frame_detect_btn, text='Dev Mode', var=self.devMode_booleanVar, pady=5) 
    self.checkBtn_devMode.pack(fill=BOTH, expand=True, side=TOP)
    self.checkBtn_devMode.config(state=NORMAL)
    
    # Status Label
    self.status_StringVar = StringVar()
    self.status_StringVar.set('Lobby')
    label_status = tk.Label(self.frame_detect_btn, padx=5, pady=5, textvariable=self.status_StringVar)
    label_status.pack(fill=BOTH, expand=True, side=TOP)

    # Result Label
    self.result_win = 0
    self.result_lose = 0
    self.result_StringVar = StringVar()
    self.result_StringVar.set(f"{self.result_win} / {self.result_lose}")
    label_result = tk.Label(self.frame_detect_btn, padx=5, pady=5, textvariable=self.result_StringVar)
    label_result.pack(fill=BOTH, expand=True, side=TOP)

    # button
    self.btn_run = tk.Button(self.frame_detect_btn, text='Start', width=15, height=2, font=('Arial', 12))
    self.btn_run.pack(fill=BOTH, side=BOTTOM, expand=True)
    self.btn_run.config(command=self.btn_run_event, state=DISABLED)
    self.isRunning = False
    self.thread_bg_task = None
    self.btn_connect = tk.Button(self.frame_detect_btn, text='Connect', width=15, height=2, font=('Arial', 12))
    self.btn_connect.config(command=self.btn_ADB_connect_event)
    self.btn_connect.pack(fill=BOTH, side=BOTTOM, expand=True)
    self.isConnected = False

    # test dice/star button
    btn_select_dice = tk.Button(self.frame_test_btn, text='Load Dice Image', width=15, height=3, font=('Arial', 12))
    btn_select_dice.config(command=self.btn_test_dice_event, state=NORMAL)
    btn_select_dice.grid(row=0, column=0)

    # test dice/star/joker_copy view
    self.label_test_dice_img = tk.Label(self.frame_test_view, image=zero_img, padx=5, pady=5)
    self.label_test_dice_img.config(width=self.bg_task.detect.resize_size[0], height=self.bg_task.detect.resize_size[1])
    self.label_test_dice_img.grid(row=0, column=0)
    self.label_test_detect_img = tk.Label(self.frame_test_view, image=zero_img, padx=5, pady=5)
    self.label_test_detect_img.config(width=self.bg_task.detect.resize_size[0], height=self.bg_task.detect.resize_size[1])
    self.label_test_detect_img.grid(row=0, column=1)
    self.test_detect_star_StringVar = StringVar()
    label_test_detect_star = tk.Label(self.frame_test_view, textvariable=self.test_detect_star_StringVar, padx=5, pady=5)
    label_test_detect_star.grid(row=0, column=2)

    # test wave button
    btn_select_wave = tk.Button(self.frame_test_btn, text='Load Wave Image', width=15, height=3, font=('Arial', 12))
    btn_select_wave.config(command=self.btn_test_wave_event, state=NORMAL)
    btn_select_wave.grid(row=0, column=1)

    # test wave view
    self.label_test_wave_img = tk.Label(self.frame_test_view, image=zero_img, padx=5, pady=5)
    self.label_test_wave_img.config(width=self.bg_task.detect.resize_size[0], height=self.bg_task.detect.resize_size[1])
    self.label_test_wave_img.grid(row=1, column=0)
    self.test_detect_wave_StringVar = StringVar()
    label_test_detect_wave = tk.Label(self.frame_test_view, textvariable=self.test_detect_wave_StringVar, padx=5, pady=5)
    label_test_detect_wave.grid(row=1, column=1)

    # draw statistic
    matplotlib.use('TkAgg')
    self.statistic_figure = Figure(figsize=(7, 5), dpi=100)
    self.statistic_figure_canvas = FigureCanvasTkAgg(self.statistic_figure, self.frame_statistic_chart)
    NavigationToolbar2Tk(self.statistic_figure_canvas, self.frame_statistic_chart)
    self.statistic_axes = self.statistic_figure.add_subplot()
    self.statistic_figure_canvas.get_tk_widget().pack()
    ## add growth
    self.statistic_add_growth_booleanVar = BooleanVar()
    self.statistic_add_growth_booleanVar.set(False)
    checkBtn_statistic_add_growth = tk.Checkbutton(self.frame_statistic_info, text='Add Growth', var=self.statistic_add_growth_booleanVar, pady=10, font=('Arial', 12), anchor=W, command=self.updateStatistic) 
    checkBtn_statistic_add_growth.pack(fill=BOTH, side=TOP)
    ## add joker
    self.statistic_add_joker_booleanVar = BooleanVar()
    self.statistic_add_joker_booleanVar.set(False)
    checkBtn_statistic_add_joker = tk.Checkbutton(self.frame_statistic_info, text='Add Joker', var=self.statistic_add_joker_booleanVar, pady=10, font=('Arial', 12), anchor=W, command=self.updateStatistic) 
    checkBtn_statistic_add_joker.pack(fill=BOTH, side=TOP)

    # draw tropy line
    self.line_figure = Figure(figsize=(7, 5), dpi=100)
    self.line_figure_canvas = FigureCanvasTkAgg(self.line_figure, self.frame_line_chart)
    NavigationToolbar2Tk(self.line_figure_canvas, self.frame_line_chart)
    self.line_axes = self.line_figure.add_subplot()
    self.line_figure_canvas.get_tk_widget().pack()
    ## moving average
    moving_average = ['No MA', '3 MA', '5 MA', '10 MA']
    self.MA_stringVar = StringVar()
    self.MA_stringVar.set(moving_average[0]) # default value
    optionMenu_MA = OptionMenu(self.frame_line_info, self.MA_stringVar, *moving_average, command=self.updateTrophy)
    optionMenu_MA.pack(fill=BOTH, side=TOP)
    ## regression
    self.line_regression_booleanVar = BooleanVar()
    self.line_regression_booleanVar.set(False)
    checkBtn_line_regression = tk.Checkbutton(self.frame_line_info, text='Regression', var=self.line_regression_booleanVar, pady=10, font=('Arial', 12), anchor=W, command=self.updateTrophy) 
    checkBtn_line_regression.pack(fill=BOTH, side=TOP)
    ## info
    self.line_info_StringVar = StringVar()
    label_line_info_average = tk.Label(self.frame_line_info, textvariable=self.line_info_StringVar, justify=LEFT, font=('Arial', 12), pady=10)
    label_line_info_average.pack(fill=BOTH, side=TOP)
    
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
    self.btn_load_config_event()
    self.setSettingInputField()
    self.setCheckBoxFlag()
    self.setSelectDiceField()
    self.setResult()

    self.infinite_img = self.bg_task.detect.loadImage("./image/infinite.png", "RGBA")
    self.infinite_img = self.bg_task.detect.resizeImage(self.infinite_img, (25,15))

    MyAction.init()

    self.window.deiconify()

  def centerWindowRelativeToParent(self, parent, window):
    x = parent.winfo_x()
    y = parent.winfo_y()
    p_w = parent.winfo_width()
    p_h = parent.winfo_height()
    c_w = window.winfo_width()
    c_h = window.winfo_height()

    offset_x = (p_w - c_w) // 2
    offset_y = (p_h - c_h) // 2

    print(x, y)
    print(p_w, p_h)
    print(c_w, c_h)

    window.geometry(f"{c_w}x{c_h}+{x+offset_x}+{y+offset_y}")

  def setCheckBoxFlag(self):
    if self.bg_task is None:
      raise Exception('setCheckBoxFlag:: Need to set task variable first')
    else:
      self.autoPlay_booleanVar.set(self.bg_task.variable.getAutoPlay())
      self.topWindow_booleanVar.set(self.bg_task.variable.getTopWindow())
      self.watchAD_booleanVar.set(self.bg_task.variable.getWatchAD())
      self.restartApp_booleanVar.set(self.bg_task.variable.getRestartApp())
      self.battle_stringVar.set(self.bg_task.variable.getBattleMode())
      self.notifyResult_booleanVar.set(self.bg_task.variable.getNotifyResult())
      self.devMode_booleanVar.set(self.bg_task.variable.getDevMode())

  def getCheckBoxFlag(self):
    if self.bg_task is None:
      raise Exception('getCheckBoxFlag:: Need to set task variable first')
    else:
      self.bg_task.variable.setAutoPlay(self.autoPlay_booleanVar.get())
      self.bg_task.variable.setTopWindow(self.topWindow_booleanVar.get())
      self.bg_task.variable.setWatchAD(self.watchAD_booleanVar.get())
      self.bg_task.variable.setRestartApp(self.restartApp_booleanVar.get())
      self.bg_task.variable.setBattleMode(self.battle_stringVar.get())
      self.bg_task.variable.setNotifyResult(self.notifyResult_booleanVar.get())
      self.bg_task.variable.setDevMode(self.devMode_booleanVar.get())

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
      self.setting_stringVar['Detect Star Mode'].set(dealString(int(self.bg_task.variable.getDetectStarMode())))
      self.setting_stringVar['ADB Mode'].set(dealString(int(self.bg_task.variable.getADBMode())))
      self.setting_stringVar['ADB IP'].set(self.bg_task.variable.getADBIP())
      self.setting_stringVar['ADB Port'].set(dealString(self.bg_task.variable.getADBPort()))
      self.setting_stringVar['ADB ID'].set(self.bg_task.variable.getADBID())
      self.setting_stringVar['Max FPS'].set(self.bg_task.variable.getMaxFPS())
      self.setting_stringVar['BitRate'].set(self.bg_task.variable.getBitRate())
      self.setting_stringVar['Random Offset'].set(dealString(self.bg_task.variable.getRandomOffset()))
      self.setting_stringVar['Board Left Top XY'].set(dealString(self.bg_task.variable.getBoardDiceLeftTopXY()))
      self.setting_stringVar['Board Dice Offset XY'].set(dealString(self.bg_task.variable.getBoardDiceOffsetXY()))
      self.setting_stringVar['Level Dice Left XY'].set(dealString(self.bg_task.variable.getLevelDiceLeftXY()))
      self.setting_stringVar['Level Dice Offset X'].set(dealString(self.bg_task.variable.getLevelDiceOffsetX()))
      self.setting_stringVar['Emoji Dialog XY'].set(dealString(self.bg_task.variable.getEmojiDialogXY()))
      self.setting_stringVar['Emoji Left XY'].set(dealString(self.bg_task.variable.getEmojiLeftXY()))
      self.setting_stringVar['Emoji Offset X'].set(dealString(self.bg_task.variable.getEmojiOffsetX()))
      self.setting_stringVar['Summon Dice XY'].set(dealString(self.bg_task.variable.getSummonDiceXY()))
      self.setting_stringVar['Merge Float Location XY'].set(dealString(self.bg_task.variable.getMergeFloatLocationXY()))
      self.setting_stringVar['Battle XY'].set(dealString(self.bg_task.variable.getBattleXY()))
      self.setting_stringVar['AD Close XY'].set(dealString(self.bg_task.variable.getADCloseXY()))
      self.setting_stringVar['Spell XY'].set(dealString(self.bg_task.variable.getSpellXY()))
      self.setting_stringVar['Damage List XY'].set(dealString(self.bg_task.variable.getDamageListXY()))
      self.setting_stringVar['Party List 1v1 Left XY'].set(dealString(self.bg_task.variable.getPartyList1v1LeftXY()))
      self.setting_stringVar['Party List 1v1 Offset X'].set(dealString(self.bg_task.variable.getPartyList1v1OffsetX()))
      self.setting_stringVar['Trophy Left Top XY'].set(dealString(self.bg_task.variable.getTrophyLeftTopXY()))
      self.setting_stringVar['Check Point Start XY'].set(dealString(self.bg_task.variable.getCheckPointStartXY()))
      self.setting_stringVar['Check Point End XY'].set(dealString(self.bg_task.variable.getCheckPointEndXY()))
      self.setting_stringVar['Wave Left Top XY'].set(dealString(self.bg_task.variable.getWaveLeftTopXY()))
      self.setting_stringVar['Extract Dice Size WH'].set(dealString(self.bg_task.variable.getExtractDiceSizeWH()))
      self.setting_stringVar['Extract Dice Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractDiceLuSizeWH()))
      self.setting_stringVar['Extract Summon Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractSummonLuSizeWH()))
      self.setting_stringVar['Extract Level Dice Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractLevelDiceLuSizeWH()))
      self.setting_stringVar['Extract Spell Luminance Size WH'].set(dealString(self.bg_task.variable.getExtractSpellLuSizeWH()))
      self.setting_stringVar['Emoji Dialog WH'].set(dealString(self.bg_task.variable.getEmojiDialogWH()))
      self.setting_stringVar['Extract Party List 1v1 Size WH'].set(dealString(self.bg_task.variable.getExtractPartyList1v1SizeWH()))
      self.setting_stringVar['Extract Trophy Size WH'].set(dealString(self.bg_task.variable.getExtractTrophySizeWH()))
      self.setting_stringVar['Extract Wave Size WH'].set(dealString(self.bg_task.variable.getExtractWaveSizeWH()))
      self.setting_stringVar['Zoom Ratio'].set(dealString(self.bg_task.variable.getZoomRatio()))
      self.setting_stringVar['Detect Delay'].set(dealString(self.bg_task.variable.getDetectDelay()))
      self.setting_stringVar['Restart Delay'].set(dealString(self.bg_task.variable.getRestartDelay()))
      self.setting_stringVar['Screenshot Delay'].set(dealString(self.bg_task.variable.getScreenshotDelay()))
      self.setting_stringVar['Freeze Threshold'].set(dealString(self.bg_task.variable.getFreezeThreshold()))
      self.setting_stringVar['Focus Threshold'].set(dealString(self.bg_task.variable.getFocusThreshold()))
      self.setting_stringVar['Line Notify Token'].set(self.bg_task.variable.getLineNotifyToken())

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
      self.bg_task.variable.setDetectStarMode(DetectStarMode(dealString(self.setting_stringVar['Detect Star Mode'].get())))
      self.bg_task.variable.setADBMode(ADBMode(dealString(self.setting_stringVar['ADB Mode'].get())))
      self.bg_task.variable.setADBIP(self.setting_stringVar['ADB IP'].get())
      self.bg_task.variable.setADBPort(dealString(self.setting_stringVar['ADB Port'].get()))
      self.bg_task.variable.setADBID(self.setting_stringVar['ADB ID'].get())
      self.bg_task.variable.setMaxFPS(dealString(self.setting_stringVar['Max FPS'].get()))
      self.bg_task.variable.setBitRate(dealString(self.setting_stringVar['BitRate'].get()))
      self.bg_task.variable.setRandomOffset(dealString(self.setting_stringVar['Random Offset'].get()))
      self.bg_task.variable.setBoardDiceLeftTopXY(dealString(self.setting_stringVar['Board Left Top XY'].get()))
      self.bg_task.variable.setBoardDiceOffsetXY(dealString(self.setting_stringVar['Board Dice Offset XY'].get(), float))
      self.bg_task.variable.setLevelDiceLeftXY(dealString(self.setting_stringVar['Level Dice Left XY'].get()))
      self.bg_task.variable.setLevelDiceOffsetX(dealString(self.setting_stringVar['Level Dice Offset X'].get()))
      self.bg_task.variable.setEmojiDialogXY(dealString(self.setting_stringVar['Emoji Dialog XY'].get()))
      self.bg_task.variable.setEmojiLeftXY(dealString(self.setting_stringVar['Emoji Left XY'].get()))
      self.bg_task.variable.setEmojiOffsetX(dealString(self.setting_stringVar['Emoji Offset X'].get()))
      self.bg_task.variable.setSummonDiceXY(dealString(self.setting_stringVar['Summon Dice XY'].get()))
      self.bg_task.variable.setMergeFloatLocationXY(dealString(self.setting_stringVar['Merge Float Location XY'].get()))
      self.bg_task.variable.setBattleXY(dealString(self.setting_stringVar['Battle XY'].get()))
      self.bg_task.variable.setADCloseXY(dealString(self.setting_stringVar['AD Close XY'].get()))
      self.bg_task.variable.setSpellXY(dealString(self.setting_stringVar['Spell XY'].get()))
      self.bg_task.variable.setDamageListXY(dealString(self.setting_stringVar['Damage List XY'].get()))
      self.bg_task.variable.setPartyList1v1LeftXY(dealString(self.setting_stringVar['Party List 1v1 Left XY'].get()))
      self.bg_task.variable.setPartyList1v1OffsetX(dealString(self.setting_stringVar['Party List 1v1 Offset X'].get()))
      self.bg_task.variable.setTrophyLeftTopXY(dealString(self.setting_stringVar['Trophy Left Top XY'].get()))
      self.bg_task.variable.setCheckPointStartXY(dealString(self.setting_stringVar['Check Point Start XY'].get()))
      self.bg_task.variable.setCheckPointEndXY(dealString(self.setting_stringVar['Check Point End XY'].get()))
      self.bg_task.variable.setWaveLeftTopXY(dealString(self.setting_stringVar['Wave Left Top XY'].get()))
      self.bg_task.variable.setExtractDiceSizeWH(dealString(self.setting_stringVar['Extract Dice Size WH'].get()))
      self.bg_task.variable.setExtractDiceLuSizeWH(dealString(self.setting_stringVar['Extract Dice Luminance Size WH'].get()))
      self.bg_task.variable.setExtractSummonLuSizeWH(dealString(self.setting_stringVar['Extract Summon Luminance Size WH'].get()))
      self.bg_task.variable.setExtractLevelDiceLuSizeWH(dealString(self.setting_stringVar['Extract Level Dice Luminance Size WH'].get()))
      self.bg_task.variable.setExtractSpellLuSizeWH(dealString(self.setting_stringVar['Extract Spell Luminance Size WH'].get()))
      self.bg_task.variable.setEmojiDialogWH(dealString(self.setting_stringVar['Emoji Dialog WH'].get()))
      self.bg_task.variable.setExtractPartyList1v1SizeWH(dealString(self.setting_stringVar['Extract Party List 1v1 Size WH'].get()))
      self.bg_task.variable.setExtractTrophySizeWH(dealString(self.setting_stringVar['Extract Trophy Size WH'].get()))
      self.bg_task.variable.setExtractWaveSizeWH(dealString(self.setting_stringVar['Extract Wave Size WH'].get()))
      self.bg_task.variable.setZoomRatio(dealString(self.setting_stringVar['Zoom Ratio'].get(), float))
      self.bg_task.variable.setDetectDelay(dealString(self.setting_stringVar['Detect Delay'].get(), float))
      self.bg_task.variable.setRestartDelay(dealString(self.setting_stringVar['Restart Delay'].get(), float))
      self.bg_task.variable.setScreenshotDelay(dealString(self.setting_stringVar['Screenshot Delay'].get(), float))
      self.bg_task.variable.setFreezeThreshold(dealString(self.setting_stringVar['Freeze Threshold'].get()))
      self.bg_task.variable.setFocusThreshold(dealString(self.setting_stringVar['Focus Threshold'].get()))
      self.bg_task.variable.setLineNotifyToken(self.setting_stringVar['Line Notify Token'].get())
    
  def btn_run_event(self):
    if self.isRunning == False: # enable
      if self.bg_task is not None:
        if self.thread_bg_task is None or not self.thread_bg_task.is_alive():
          self.getSettingInputField()
          self.getCheckBoxFlag()
          self.getSelectDiceField()
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
    self.result_win = 0
    self.result_lose = 0
    self.result_StringVar.set(f"{self.result_win} / {self.result_lose}")
    self.getResult()

  def setResult(self):
    self.result_win = self.bg_task.variable.getWin()
    self.result_lose = self.bg_task.variable.getLose()
    self.result_StringVar.set(f"{self.result_win} / {self.result_lose}")

  def getResult(self):
    self.bg_task.variable.setWin(self.result_win)
    self.bg_task.variable.setLose(self.result_lose)

  def btn_bm_event(self):
    def bm_function():
      self.btn_BM.config(state=DISABLED, text='BM ing...')
      self.bg_task.diceControl.BMOpponent()
      self.btn_BM.config(state=NORMAL, text='BM')
    t = threading.Thread(target = bm_function)
    t.start()

  def copy_to_clipboard_and_close(self, image, window):
    output = BytesIO()
    image.convert('RGB').save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

    window.destroy()

  def btn_share_party_event(self):
    # pop window
    share_window = Toplevel(self.window)
    share_window.withdraw()
    share_window.title("Share Party")

    label_img = tk.Label(share_window)
    label_img.pack(fill=BOTH, expand=True, side=TOP)

    # draw a draw
    img = Draw.getBlankImage((320,100))
    # add dice
    for i, dice in enumerate(self.select_dice_name):
      idx = self.bg_task.detect.dice_name_idx_dict[dice]
      dice_img = self.bg_task.detect.dice_image_PIL_resize[idx]
      x = i * (self.bg_task.detect.resize_size[0] + 5) + 25
      img = Draw.addImage(img, dice_img, (x, 10))
    # add text
    total = self.result_win + self.result_lose
    win_rate = (self.result_win/total)*100 if total > 0 else 0.0
    lose_rate = (self.result_lose/total)*100 if total > 0 else 0.0
    img = Draw.addText(img, (None, 70), (160, None),
      f"Win: {self.result_win} ({win_rate:.1f} %)    Lose: {self.result_lose} ({lose_rate:.1f} %)",
      16)
    self.changeImage(label_img, self.bg_task.detect.Image2TK(img))

    btn_copy = tk.Button(share_window, text='Copy Image', width=15, height=2, font=('Arial', 10))
    btn_copy.pack(fill=BOTH, expand=True, side=TOP)
    btn_copy.config(command=partial(self.copy_to_clipboard_and_close, img, share_window), state=NORMAL)

    share_window.attributes('-alpha', 0.0)
    share_window.update_idletasks()
    share_window.deiconify()
    self.centerWindowRelativeToParent(self.window, share_window)
    share_window.attributes('-alpha', 1.0)

  def btn_share_board_event(self):
    # pop window
    share_window = Toplevel(self.window)
    share_window.withdraw()
    share_window.title("Share Board")

    label_img = tk.Label(share_window)
    label_img.pack(fill=BOTH, expand=True, side=TOP)

    dashboard = Draw.getBlankImage((700,200))
    # add detect dice
    for i, (dice, star) in enumerate(zip(self.bg_task.board_dice, self.bg_task.board_dice_star)):
      # dice
      idx = self.bg_task.detect.dice_name_idx_dict[dice]
      dice_img = self.bg_task.detect.dice_image_PIL_resize[idx]
      row = i // self.bg_task.variable.col
      col = i % self.bg_task.variable.col
      x = col * (self.bg_task.detect.resize_size[0] + 20) + 25
      y = 10 + (row * (self.bg_task.detect.resize_size[1] + 10))
      dashboard = Draw.addImage(dashboard, dice_img, (x, y))
      # text
      dashboard = Draw.addText(dashboard, (None, None), (x+self.bg_task.detect.resize_size[0]+10, y+(self.bg_task.detect.resize_size[1]//2)), str(star), 14)
    # add screenshot dice
    for i, img in enumerate(self.bg_task.detect_board_dice_img):
      img = self.bg_task.detect.OpenCV2Image(img).convert('RGBA')
      row = i // self.bg_task.variable.col
      col = i % self.bg_task.variable.col
      x = col * (self.bg_task.detect.resize_size[0] + 5) + 405
      y = 10 + (row * (self.bg_task.detect.resize_size[1] + 10))
      dashboard = Draw.addImage(dashboard, img, (x, y))

    self.changeImage(label_img, self.bg_task.detect.Image2TK(dashboard))

    btn_copy = tk.Button(share_window, text='Copy Image', width=15, height=2, font=('Arial', 10))
    btn_copy.pack(fill=BOTH, expand=True, side=TOP)
    btn_copy.config(command=partial(self.copy_to_clipboard_and_close, dashboard, share_window), state=NORMAL)

    share_window.attributes('-alpha', 0.0)
    share_window.update_idletasks()
    share_window.deiconify()
    self.centerWindowRelativeToParent(self.window, share_window)
    share_window.attributes('-alpha', 1.0)

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

  def limitImageSize(self, img, height_limit):
    h,w,_ = img.shape
    if h > height_limit:
      return cv2.resize(img, (int((height_limit/h)*w), height_limit))
    else:
      return img.copy()

  def btn_screenshot_event(self):
    self.log('=== ScreenShot ===\n')
    success, im = self.bg_task.screen.getScreenShot(self.bg_task.variable.getZoomRatio())
    if success:
      self.screenshot_image = im.copy()
      # limit
      self.screenshot_image_limit = self.limitImageSize(self.screenshot_image, 600)
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(self.screenshot_image_limit))
  
  def btn_draw_event(self):
    self.getSettingInputField()
    labeled_screenshot = self.bg_task.detect.drawTestImage(self.screenshot_image.copy())
    # limit
    labeled_screenshot_limit = self.limitImageSize(labeled_screenshot, 600)
    self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(labeled_screenshot_limit))

  def btn_save_config_event(self):
    self.log('=== Save Config ===\n')
    self.getSettingInputField()
    self.getCheckBoxFlag()
    self.getSelectDiceField()
    self.bg_task.variable.saveToConfigFile()
    self.checkBtn_watchAD.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))
    self.checkBtn_restartApp.config(state=(NORMAL if self.bg_task.variable.getControlMode() == ControlMode.ADB else DISABLED))

  def btn_load_config_event(self):
    self.log('=== Load Config ===\n')
    self.bg_task.variable.loadFromConfigFile()
    self.setSettingInputField()
    self.setCheckBoxFlag()
    self.setSelectDiceField()

  def btn_save_extract_images_event(self):
    self.log('=== Save Extract Images ===\n')
    def event():
      try:
        self.btn_save_extract_images.config(state=DISABLED, text='saving...')
        if not os.path.exists('extract'):
          os.mkdir('extract')
        if self.bg_task.detect_board_dice_img is not None:
          for i, (name,star,img) in enumerate(zip(self.bg_task.board_dice, self.bg_task.board_dice_star, self.bg_task.detect_board_dice_img)):
              self.bg_task.detect.save(img, os.path.join('extract', f'{name}_{star}_{getTimeStamp()}{i:02d}.png'))
      except:
        self.log(f'Save Extract Images Error\n{traceback.format_exc()}')
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
    if filename == "": return

    try:
      # read image
      self.screenshot_image = self.bg_task.detect.load(filename)
      # limit
      self.screenshot_image_limit = self.limitImageSize(self.screenshot_image, 600)
      self.changeImage(self.label_screenshot, self.bg_task.detect.OpenCV2TK(self.screenshot_image_limit))
    except Exception as e:
      messagebox.showerror('Load Error', traceback.format_exc(), parent=self.window)
    finally:
      # enable other button
      self.enableButtonByLoadScreenshot()

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

  def diceAddJoker(self, img):
    return Draw.addImage(img, self.infinite_img, (13,17))

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

    select_dice_window.update_idletasks()
    select_dice_window.attributes('-alpha', 0.0)
    select_dice_window.deiconify()
    self.centerWindowRelativeToParent(self.window, select_dice_window)
    select_dice_window.attributes('-alpha', 1.0)
    
  def getSelectDiceField(self):
    self.bg_task.variable.setDiceParty(self.select_dice_name)

  def setSelectDiceField(self):
    for i,dice in enumerate(self.bg_task.variable.getDiceParty()):
      self.select_dice_name[i] = dice
      dice_idx = self.bg_task.detect.dice_name_idx_dict[dice]
      self.changeImage(self.select_dice_label[i], self.bg_task.detect.dice_image_tk_resize[dice_idx])

  def checkBtn_topWindow(self):
    self.window.call('wm', 'attributes', '.', '-topmost', self.topWindow_booleanVar.get())

  def label_screen_click_event(self, event):
    if event.num == 1:
      self.label_screen.isDown = True
      ADB.touch((event.x*self.label_screen.ratio, event.y*self.label_screen.ratio), 0) # down
    elif event.num == 2:
      ADB.home()
    elif event.num == 3:
      ADB.back()

  def label_screen_move_event(self, event):
    ADB.touch((event.x*self.label_screen.ratio, event.y*self.label_screen.ratio), 2) # move

  def label_screen_release_event(self, event):
    self.label_screen.isDown = False
    ADB.touch((event.x*self.label_screen.ratio, event.y*self.label_screen.ratio), 1) # up

  def label_screen_leave_event(self, event):
    if hasattr(self.label_screen, 'isDown') and self.label_screen.isDown == True:
      self.label_screen.isDown = False
      ADB.touch((event.x*self.label_screen.ratio, event.y*self.label_screen.ratio), 1) # up

  def btn_test_dice_event(self):
    self.log('=== Load Dice Image ===\n')
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
    if filename == "": return

    try:
      # read image
      dice_img = self.bg_task.detect.load(filename)
      self.changeImage(self.label_test_dice_img, self.bg_task.detect.OpenCV2TK(dice_img))
      # detect joker copy
      joker_copy = self.bg_task.detect.detectJokerCopy(dice_img)
      # detect dice
      dice_detect = self.bg_task.detect.detectDice(dice_img, None, self.bg_task.variable.getDetectDiceMode())
      dice_detect_img = self.bg_task.detect.dice_image_PIL_resize[self.bg_task.detect.dice_name_idx_dict[dice_detect[0]]]
      # add joker copy
      if joker_copy:
        dice_detect_img = self.diceAddJoker(dice_detect_img)
      dice_detect_img = self.bg_task.detect.Image2TK(dice_detect_img)
      self.changeImage(self.label_test_detect_img, dice_detect_img)
      # detect star
      star_detect = self.bg_task.detect.detectStar(dice_img)
      self.test_detect_star_StringVar.set(str(star_detect))
    except:
      messagebox.showerror('Load Error', traceback.format_exc(), parent=self.window)

  def btn_test_wave_event(self):
    self.log('=== Load Wave Image ===\n')
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
    if filename == "": return

    try:
      # read image
      wave_img = self.bg_task.detect.load(filename)
      self.changeImage(self.label_test_wave_img, self.bg_task.detect.OpenCV2TK(wave_img))
      # detect wave
      wave = self.bg_task.detect.detectWave(wave_img)
      self.test_detect_wave_StringVar.set(str(wave))
    except:
      messagebox.showerror('Load Error', traceback.format_exc(), parent=self.window)
    

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

          def updateScreen(frame):
            frame = self.limitImageSize(frame, self.label_screen.winfo_height()-10)
            frame = self.bg_task.detect.OpenCV2TK(frame)
            self.changeImage(self.label_screen, frame)
            if not hasattr(self.label_screen, 'ratio'):
              orig = ADB.getResolution()
              self.label_screen.ratio = orig[1] / self.label_screen.image.height()
          
          # initial value
          r = True
          s, r = ADB.connect(self.bg_task.variable.getADBMode(), self.bg_task.variable.getADBIP(), self.bg_task.variable.getADBPort(), self.bg_task.variable.getADBID())
          self.log(s + '\n')
          if r: # success
            ADB.createClient(self.bg_task.variable.getADBMode(), self.bg_task.variable.getMaxFPS(), self.bg_task.variable.getBitRate(), updateScreen)
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
    self.btn_screenshot.config(state=NORMAL)
    self.btn_BM.config(state=NORMAL)
    self.btn_draw.config(state=NORMAL)
    self.btn_save_screenshot.config(state=NORMAL)
    self.btn_detect.config(state=NORMAL)
    self.btn_save_extract_images.config(state=NORMAL)
    self.btn_share_board.config(state=NORMAL)
  
  def enableButtonByLoadScreenshot(self):
    self.btn_save_screenshot.config(state=NORMAL)
    self.btn_detect.config(state=NORMAL)
    self.btn_draw.config(state=NORMAL)

  def log(self, text):
    print(text)
    self.text_log.insert(tk.END, text)
    self.text_log.see(tk.END)  

  def updateDraw(self, _):
    if hasattr(self, 'statistic_figure_canvas') and self.tabControl.index(self.tabControl.select()) == 2:
      self.updateStatistic()
    elif hasattr(self, 'line_figure_canvas') and self.tabControl.index(self.tabControl.select()) == 3:
      self.updateTrophy()

  def updateStatistic(self, *_):
    data = self.bg_task.dice_statistic.copy()
    # check joker and growth
    if self.statistic_add_joker_booleanVar.get() == False:
      data.pop('Joker', None)
    if self.statistic_add_growth_booleanVar.get() == False:
      data.pop('Growth', None)

    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    data = dict(data)
    data_x = data.keys()
    data_y = data.values()
    self.statistic_axes.clear()
    self.statistic_axes.bar(data_x, data_y)
    self.statistic_axes.set_title('Number of occurrences of dices in 1v1 mode')
    self.statistic_axes.set_ylabel('Number of occurrences')
    self.statistic_axes.tick_params(labelrotation=90)
    self.statistic_axes.yaxis.get_major_locator().set_params(integer=True)
    self.statistic_figure.tight_layout(rect=[0.05,0.10,0.95,0.95])
    self.statistic_figure_canvas.draw()

  def updateTrophy(self, *_):
    self.line_axes.clear()
    data = self.bg_task.trophy_statistic.copy()
    x = np.arange(len(data))
    self.line_axes.plot(x, data)
    # regression
    if self.line_regression_booleanVar.get() == True:
      coef = np.polyfit(x, data, 1)
      fn = np.poly1d(coef)
      self.line_axes.plot(x, fn(x), color='orange', linestyle='dashed')
    # moving average
    if 'No' not in self.MA_stringVar.get():
      window_size = int(self.MA_stringVar.get().split(' ')[0])
      self.line_axes.plot(x, uniform_filter1d(data, size=window_size, mode='nearest'), color='green', linestyle='dashed')
    self.line_axes.set_title('Line Chart of Trophy')
    self.line_axes.set_ylabel('Trophy')
    self.line_axes.xaxis.get_major_locator().set_params(integer=True)
    self.line_axes.yaxis.get_major_locator().set_params(integer=True)
    self.line_figure_canvas.draw()

    mean = np.mean(data) if len(data) > 0 else float('nan')
    sd = np.std(data) if len(data) > 0 else float('nan')
    total_offset = data[-1] - data[0] if len(data) > 0 else float('nan')
    offset = total_offset/len(data) if len(data) > 0 else float('nan')
    start = int(data[0]) if len(data) > 0 else float('nan')
    current = int(data[-1]) if len(data) > 0 else float('nan')
    size = len(data)
    max = np.max(data) if len(data) > 0 else float('nan')
    min = np.min(data) if len(data) > 0 else float('nan')

    self.line_info_StringVar.set(
f"""Start: {start}\n
Current: {current}\n
Times: {size}\n
Average: {mean:.2f}\n
SD: {sd:.2f}\n
Max: {max}\n
Min: {min}\n
Total Gain: {total_offset:+}\n
Average Gain: {offset:+.2f}""")

  def updateDice(self, board_dice, board_dice_star, board_dice_joker_copy, detect_board_dice_img):
    # update ui
    time_start = time.time()
    for i, zipped in enumerate(zip(board_dice, board_dice_star, board_dice_joker_copy, detect_board_dice_img)):
      name, star, joker_copy, img = zipped
      # left: predicted dice
      idx = self.bg_task.detect.dice_name_idx_dict[name]
      dice_img = self.bg_task.detect.dice_image_PIL_resize[idx]
      ## add joker copy
      if joker_copy:
        dice_img = Draw.addImage(dice_img, self.infinite_img, (13,17))
      dice_img = self.bg_task.detect.Image2TK(dice_img)
      self.changeImage(self.label_board_dice[i], dice_img)
      # left: predicted star
      self.label_board_star[i].config(text=str(star))
      # right: screenshot image
      img = self.bg_task.detect.OpenCV2TK(img)
      self.changeImage(self.label_detect_board_dice[i], img)
    print(f'Update Image Time: {time.time() - time_start} s')

  def run_bg_task(self):
    def stopDetect():
      self.isRunning = False
      self.btn_run.config(text='Start')
      self.log('=== Stop Detecting ===\n')

    def restartApp():
      ADB.restart()
      
    # ---------------------------------------- #

    hasRecordResult = False
    hasNotify = False

    while self.isRunning:
      # detect dice war app
      notInDiceWarCount = 0
      stopRunning = False
      while True:
        if self.bg_task.variable.getControlMode() == ControlMode.ADB:
          inDiceWar,message = ADB.detectDiceWar()
          if not inDiceWar:
            notInDiceWarCount += 1
            self.log(f"Not In Dice War App Count: {notInDiceWarCount}\n")
            if notInDiceWarCount >= self.bg_task.variable.getFocusThreshold():
              self.log(message)
              self.log("Error: Focus app is not Dice War App\n")
              if self.restartApp_booleanVar.get() == True:
                self.log(f"Info: Restart app and continue after {self.bg_task.variable.getRestartDelay()} seconds\n")
                restartApp()
                time.sleep(self.bg_task.variable.getRestartDelay()) # wait for delay
              else:
                stopDetect()
                stopRunning = True
              break
            else:
              time.sleep(0.5)
              continue
          else:
            break
        else:
          break
      if stopRunning:
        break
      
      # record previous state
      previous_status = self.bg_task.status

      # flag
      battleMode = BattleMode.BATTLE_2V2 # default
      if self.battle_stringVar.get() == '1v1':
        battleMode = BattleMode.BATTLE_1V1
      elif self.battle_stringVar.get() == '2v2':
        battleMode = BattleMode.BATTLE_2V2
      elif self.battle_stringVar.get() == 'Arcade':
        battleMode = BattleMode.BATTLE_ARCADE

      # run
      try:
        self.bg_task.task(self.updateDice,
          self.log, 
          self.autoPlay_booleanVar.get(), 
          self.watchAD_booleanVar.get(),
          battleMode,
          self.devMode_booleanVar.get())
      except Exception:
        self.log(f'Run Task Error: {traceback.format_exc()}\n')
        stopDetect()
        break
      
      # status changed
      if previous_status != self.bg_task.status:
        status_str = ['Lobby', 'Wait', 'Game', 'Finish', 'Trophy', 'Finish Animation', 'Arcade']
        self.log(f'=== Detect {status_str[int(self.bg_task.status)]} ===\n')
        self.status_StringVar.set(status_str[int(self.bg_task.status)].replace(" ","\n"))

      # hasRecord
      if self.bg_task.status == Status.LOBBY or self.bg_task.status == Status.ARCADE:
        hasRecordResult = False
        hasNotify = False

      # record result
      if battleMode != BattleMode.BATTLE_ARCADE:
        if not hasRecordResult and self.bg_task.status == Status.FINISH and hasattr(self.bg_task, 'result') and self.bg_task.result is not None:
          hasRecordResult = True
          if self.bg_task.result == True:
            self.result_win += 1
          else:
            self.result_lose += 1
          self.result_StringVar.set(f"{self.result_win} / {self.result_lose}")
          self.getResult()

      # send notify
      if not hasNotify and self.bg_task.status == Status.FINISH and hasattr(self.bg_task, 'result_screenshot') and self.bg_task.result_screenshot is not None:
        hasNotify = True
        if self.notifyResult_booleanVar.get() == True:
          self.log('=== Send Notify ===\n')
          if battleMode == BattleMode.BATTLE_ARCADE:
            text = 'Finish Arcade'
          else:
            text = f'{"Win" if self.bg_task.result else "Lose"} ({self.result_win} / {self.result_lose})'

          success, response, remain = Line.notify(self.bg_task.variable.getLineNotifyToken(), 
            text, self.bg_task.result_screenshot)
          if not success:
            self.log(f'{response}\n')
          else: 
            self.log(f"API Remain: {remain['API']}, Image Remain: {remain['Image']}, Reset Time: {remain['Reset']}\n")

      # update dashboard
      ## update cpu & memory
      if not hasattr(self, 'resource_thread') or not self.resource_thread.is_alive():
        def updateResource():
          self.cpu_StringVar.set(f'CPU: {Resource.getCPU(self.bg_task.variable.getEmulatorMode()):.2f} %')
          self.mem_StringVar.set(f'MEM: {Resource.getMEM(self.bg_task.variable.getEmulatorMode())/1024/1024:.2f} MB')
        self.resource_thread = threading.Thread(target=updateResource)
        self.resource_thread.setDaemon(True)
        self.resource_thread.start()
      ## update elapsed time
      elapsed_time_microsecond = str(int((time.time() - self.last_update_time_stamp) * 1000)).rjust(6) + ' ms' if self.last_update_time_stamp is not None else "   --   "
      self.elapsed_time_StringVar.set(f'Elapsed Time: {elapsed_time_microsecond}')
      self.last_update_time_stamp = time.time()
      ## update wave
      self.wave_StringVar.set(f'Wave: {self.bg_task.wave if hasattr(self.bg_task, "wave") else "--"}')

      # check freeze
      if self.bg_task.same_screenshot_cnt >= self.bg_task.variable.getFreezeThreshold():
        self.log("Error: Dice War App freezes\n")
        if self.restartApp_booleanVar.get() == True:
          self.log(f"Info: Restart app and continue after {self.bg_task.variable.getRestartDelay()} seconds\n")
          restartApp()
          time.sleep(self.bg_task.variable.getRestartDelay()) # wait for delay
        else:
          stopDetect()
          break

      if self.bg_task.status == Status.LOBBY or self.bg_task.status == Status.ARCADE:
        # initial
        if previous_status == Status.LOBBY or previous_status == Status.ARCADE:
          self.bg_task.diceControl.battle(battleMode)
        else:
          if not self.autoPlay_booleanVar.get():
            self.log('Detect Lobby / Arcade, stop detecting\n')
            stopDetect()
            break

      # detect delay
      time.sleep(self.bg_task.variable.getDetectDelay())
      # call gc
      collected = gc.collect()
      print(f'Collect: {collected}')

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
    self.btn_save_config_event()

    # wait thread finish
    while True:
      with self.bg_task.saveImageThreads_lock.gen_rlock():
        if len(self.bg_task.saveImageThreads) == 0:
          break
      time.sleep(0.1)

  def RUN(self):
    self.log('=== Finish Initial ===\n')
    self.window.mainloop()