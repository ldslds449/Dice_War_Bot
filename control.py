import win32con
import win32api
import time
import math
import random as rd
from typing import Tuple

from variable import *
from adb import *
from mode import ControlMode

class Control:
  def __init__(self, _mode: ControlMode, _hwnd = None):
    self.mode = _mode
    if self.mode == ControlMode.WIN32API:
      self.hwnd = _hwnd
      if self.hwnd is None:
        raise Exception('Need hwnd parameter in WIN32API mode')
    elif self.mode == ControlMode.ADB:
      pass

  # pos: x, y
  def tap(self, pos: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(pos[0], pos[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, clickPos)
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, clickPos)
    elif self.mode == ControlMode.ADB:
      ADB.click(pos)

  def drag_press(self, src: Tuple[int, int], dst: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(src[0], src[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, clickPos)

      offset = (dst[0] - src[0], dst[1] - src[1])
      max_value = max(abs(offset[0]), abs(offset[1]))
      max_value = max_value//5 if max_value > 60 else max_value//2
      step = (offset[0]/max_value, offset[1]/max_value)
      for i in range(max_value):
        clickPos = win32api.MAKELONG(src[0]+int(step[0]*i), src[1]+int(step[1]*i))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, clickPos)
        time.sleep(0.001)
    elif self.mode == ControlMode.ADB:
      pass

  def drag_up(self, dst: Tuple[int, int]):
    if self.mode == ControlMode.WIN32API:
      clickPos = win32api.MAKELONG(dst[0], dst[1])
      win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, clickPos)
    elif self.mode == ControlMode.ADB:
      pass

  def drag(self, src: Tuple[int, int], dst: Tuple[int, int], time_scale: int):
    if self.mode == ControlMode.WIN32API:
      self.drag_press(src, dst)
      self.drag_up(dst)
    elif self.mode == ControlMode.ADB:
      offset_x = src[0] - dst[0]
      offset_y = src[1] - dst[1]
      dist = math.sqrt(abs(offset_x)**2 + abs(offset_y)**2)
      duration = dist / time_scale
      ADB.swipe(src, dst, duration)

  def back(self):
    if self.mode == ControlMode.WIN32API:
      pass # not supported
    elif self.mode == ControlMode.ADB:
      ADB.back()

class DiceControl(Control):
  def __init__(self, _mode: ControlMode, _hwnd = None):
    super(DiceControl, self).__init__(_mode, _hwnd)

  def setVariable(self, _variable: Variable):
    self.variable = _variable
    self.col = 5

  def modifyZoom(self, value):
    scalar = self.variable.getZoomRatio()
    if type(value) is tuple:
      list_value = list(value)
      return tuple(int(x/scalar) for x in list_value)
    elif type(value) is int or type(value) is float:
      return int(value/scalar)
    else:
      raise Exception(f'modifyZoom:: do not support this type --- {type(value)}')

  def randomOffset(self, value):
    offset_value = self.variable.getRandomOffset()
    if type(value) is tuple:
      list_value = list(value)
      for i in range(len(list_value)):
        offset = rd.randint(-offset_value, offset_value)
        list_value[i] = list_value[i] + offset
      return tuple(list_value)
    elif type(value) is int or type(value) is float:
      offset = rd.randint(-offset_value, offset_value)
      return int(value+offset)
    else:
      raise Exception(f'randomOffset:: do not support this type --- {type(value)}')

  def getBoardDiceXY(self, idx: int):
    idx_r = idx // self.col
    idx_c = idx % self.col

    leftTopDice_x = self.modifyZoom(self.variable.getBoardDiceLeftTopXY()[0])
    leftTopDice_y = self.modifyZoom(self.variable.getBoardDiceLeftTopXY()[1])
    offset_x = self.modifyZoom(self.variable.getBoardDiceOffsetXY()[0])
    offset_y = self.modifyZoom(self.variable.getBoardDiceOffsetXY()[1])
    return self.randomOffset((int(leftTopDice_x+idx_c*offset_x), int(leftTopDice_y+idx_r*offset_y)))

  def getLevelDiceXY(self, idx: int):
    leftDice_x = self.modifyZoom(self.variable.getLevelDiceLeftXY()[0])
    leftDice_y = self.modifyZoom(self.variable.getLevelDiceLeftXY()[1])
    offset_x = self.modifyZoom(self.variable.getLevelDiceOffsetX())
    return self.randomOffset((leftDice_x+idx*offset_x, leftDice_y))

  def getEmojiXY(self, idx: int):
    leftEmoji = self.modifyZoom(self.variable.getEmojiLeftXY())
    offset_x = self.modifyZoom(self.variable.getEmojiOffsetX())
    return self.randomOffset((leftEmoji[0]+idx*offset_x, leftEmoji[1]))

  def mergeDice(self, src: int, dst: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    dst_xy = self.getBoardDiceXY(dst-1) # rescale [1~15] to [0~14]
    self.drag(src_xy, dst_xy, self.variable.getDragTimeScale())

  def dragPressDice(self, src: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    dst_xy = self.randomOffset(self.modifyZoom(self.variable.getMergeFloatLocationXY()))
    self.drag_press(src_xy, dst_xy)

  def dragUpDice(self):
    self.drag_up(self.randomOffset(self.modifyZoom(self.variable.getMergeFloatLocationXY())))

  def summonDice(self):
    self.tap(self.randomOffset(self.modifyZoom(self.variable.getSummonDiceXY())))
  
  def castSpell(self):
    self.tap(self.randomOffset(self.modifyZoom(self.variable.getSpellXY())))

  def levelUpDice(self, idx: int):
    dice_xy = self.getLevelDiceXY(idx-1) # rescale [1~5] to [0~4]
    self.tap(dice_xy)

  def openEmojiDialog(self):
    self.tap(self.randomOffset(self.modifyZoom(self.variable.getEmojiDialogXY())))

  def sendEmoji(self, idx: int):
    self.openEmojiDialog()
    emoji_xy = self.getEmojiXY(idx-1) # rescale [1~5] to [0~4]
    time.sleep(0.1) # wait for dialog open
    self.tap(emoji_xy)

  def BMOpponent(self, times = 5):
    for _ in range(times):
      self.sendEmoji(1)

  def skip(self):
    self.summonDice()

  def battle(self, battleMode: BattleMode):
    if battleMode == BattleMode.BATTLE_1V1:
      self.tap(self.getLevelDiceXY(2))
      time.sleep(1)
      self.tap(self.getBoardDiceXY(5))
    elif battleMode == BattleMode.BATTLE_2V2:
      self.tap(self.getLevelDiceXY(2))
      time.sleep(1)
      self.tap(self.getBoardDiceXY(9))
    elif battleMode == BattleMode.BATTLE_ARCADE:
      self.castSpell()
      time.sleep(1)
      self.tap(self.getBoardDiceXY(7))
    time.sleep(1)
    self.tap(self.randomOffset(self.modifyZoom(self.variable.getBattleXY())))

  def watchAD(self):
    self.tap(self.getBoardDiceXY(12))

  def closeAD(self):
    self.tap(self.modifyZoom(self.variable.getADCloseXY()))