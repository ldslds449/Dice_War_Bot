import win32con
import win32api
import time
import subprocess
from enum import Enum
from typing import List, Tuple

from variable import *
from adb import *

class ControlMode(Enum):
  WIN32API = 0
  ADB = 1

class Control:
  def __init__(self, _mode: ControlMode, _hwnd = None, _port = None):
    self.mode = _mode
    if self.mode == ControlMode.WIN32API:
      self.hwnd = _hwnd
      if self.hwnd is None:
        raise Exception('Need hwnd parameter in WIN32API mode')
    elif self.mode == ControlMode.ADB:
      self.ip = '127.0.0.1'
      self.port = _port
      if self.port is None:
        raise Exception('Need port parameter in ADB mode')

  def sh(self, *commands):
    if self.mode == ControlMode.WIN32API:
      result = win32api.PostMessage(commands[0], commands[1], commands[2], commands[3])
    elif self.mode == ControlMode.ADB:
      result = ADB.sh(commands[0])
    return result

  # pos: x, y
  def tap(self, pos: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(pos[0], pos[1])
      self.sh(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, clickPos)
      self.sh(self.hwnd, win32con.WM_LBUTTONUP, None, clickPos)
    elif self.mode == ControlMode.ADB:
      command = f'adb -s {self.ip}:{self.port} shell input tap {pos[0]} {pos[1]}'
      self.sh(command)

  def drag_press(self, src: Tuple[int, int], dst: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(src[0], src[1])
      self.sh(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, clickPos)

      offset = (dst[0] - src[0], dst[1] - src[1])
      max_value = max(abs(offset[0]), abs(offset[1]))
      max_value = max_value//5 if max_value > 60 else max_value//2
      step = (offset[0]/max_value, offset[1]/max_value)
      for i in range(max_value):
        clickPos = win32api.MAKELONG(src[0]+int(step[0]*i), src[1]+int(step[1]*i))
        self.sh(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, clickPos)
        time.sleep(0.001)
    elif self.mode == ControlMode.ADB:
      pass

  def drag_up(self, dst: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(dst[0], dst[1])
      self.sh(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, clickPos)
    elif self.mode == ControlMode.ADB:
      pass

  def drag(self, src: Tuple[int, int], dst: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      self.drag_press(src, dst)
      self.drag_up(dst)
    elif self.mode == ControlMode.ADB:
      offset_x = src[0] - dst[0]
      offset_y = src[1] - dst[1]
      dist = offset_x**2 + offset_y**2
      duration = (dist // 50) * 50
      command = f'adb -s {self.ip}:{self.port} shell input swipe {src[0]} {src[1]} {dst[0]} {dst[1]} {duration}'
      self.sh(command)

class DiceControl(Control):
  def __init__(self, _mode: ControlMode, _hwnd = None, _port = None):
    super(DiceControl, self).__init__(_mode, _hwnd, _port)

  def setVariable(self, _variable: Variable):
    self.variable = _variable
    self.col = 5

  def modifyZoom(self, value):
    scalar = self.variable.getZoomRatio();
    if type(value) is tuple:
      list_value = list(value)
      return tuple(int(x/scalar) for x in list_value)
    elif type(value) is int:
      return int(value/scalar)
    else:
      raise Exception(f'modifyZoom:: do not support this type --- {type(value)}')

  def getBoardDiceXY(self, idx: int):
    idx_r = idx // self.col
    idx_c = idx % self.col

    leftTopDice_x = self.modifyZoom(self.variable.getBoardDiceLeftTopXY()[0])
    leftTopDice_y = self.modifyZoom(self.variable.getBoardDiceLeftTopXY()[1])
    offset_x = self.modifyZoom(self.variable.getBoardDiceOffsetXY()[0])
    offset_y = self.modifyZoom(self.variable.getBoardDiceOffsetXY()[1])
    return (leftTopDice_x+idx_c*offset_x, leftTopDice_y+idx_r*offset_y)

  def getLevelDiceXY(self, idx: int):
    leftDice_x = self.modifyZoom(self.variable.getLevelDiceLeftXY()[0])
    leftDice_y = self.modifyZoom(self.variable.getLevelDiceLeftXY()[1])
    offset_x = self.modifyZoom(self.variable.getLevelDiceOffsetX())
    return (leftDice_x+idx*offset_x, leftDice_y)

  def getEmojiXY(self, idx: int):
    leftEmoji = self.modifyZoom(self.variable.getEmojiLeftXY())
    offset_x = self.modifyZoom(self.variable.getEmojiOffsetX())
    return (leftEmoji[0]+idx*offset_x, leftEmoji[1])

  def mergeDice(self, src: int, dst: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    dst_xy = self.getBoardDiceXY(dst-1) # rescale [1~15] to [0~14]
    self.drag(src_xy, dst_xy)

  def dragPressDice(self, src: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    self.drag_press(src_xy, self.modifyZoom(self.variable.getMergeFloatLocationXY()))

  def dragUpDice(self, src: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    self.drag_up(self.modifyZoom(self.variable.getMergeFloatLocationXY()))

  def summonDice(self):
    self.tap(self.modifyZoom(self.variable.getSummonDiceXY()))

  def levelUpSP(self):
    self.tap(self.modifyZoom(self.variable.getLevelSpXY()))

  def levelUpDice(self, idx: int):
    dice_xy = self.getLevelDiceXY(idx-1) # rescale [1~5] to [0~4]
    self.tap(dice_xy)

  def openEmojiDialog(self):
    self.tap(self.modifyZoom(self.variable.getEmojiDialogXY()))

  def sendEmoji(self, idx: int):
    self.openEmojiDialog()
    emoji_xy = self.getEmojiXY(idx-1) # rescale [1~5] to [0~4]
    time.sleep(0.4) # wait for dialog open
    self.tap(emoji_xy)

  def BMOpponent(self, times = 5):
    for i in range(times):
      self.sendEmoji(1)
      time.sleep(0.2)