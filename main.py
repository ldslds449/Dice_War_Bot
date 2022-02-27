import win32gui
import win32con
import win32api
import time
import sys

from screen import *
from control import *
from detect import *
from task import *
from ui import *

# hwnd = win32gui.FindWindow(None, "BlueStacks")
# print(hex(hwnd))
# hwndChild = win32gui.GetWindow(hwnd, win32con.GW_CHILD)
# print(hex(hwndChild))

# diceControl = DiceControl(hwndChild)
# diceControl.mergeDice(4, 6)
# diceControl.summonDice()
# diceControl.levelUpSP()
# diceControl.levelUpDice(4)
# diceControl.sendEmoji(3)
# diceControl.BMOpponent()

# detect = Detect("./image")

ui = UI()
task = Task()
ui.setTask(task)
ui.RUN()

# im.save("test2.png")


# import cv2
# im = cv2.imread("test.png")


# im = detect.Image2OpenCV(im)

# img = detect.extractImage(im, (89, 478, 50, 50), ExtractMode.CENTER)
# img = detect.extractImage(im, (90, 527, 50, 50), ExtractMode.CENTER)
# img = detect.extractImage(im, (187, 576, 50, 50), ExtractMode.CENTER)
# img = detect.extractImage(im, (236, 576, 50, 50), ExtractMode.CENTER)
# detect.detectDice(img)

