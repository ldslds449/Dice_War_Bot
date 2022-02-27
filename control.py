import win32gui
import win32con
import win32api
import time
from typing import Tuple

class Control:
  def __init__(self, _hwnd):
    self.hwnd = _hwnd

  # pos: x, y
  def leftClick(self, pos: Tuple[int, int]):
    clickPos = win32api.MAKELONG(pos[0], pos[1])
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, clickPos)
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, None, clickPos)

  def drag(self, src: Tuple[int, int], dst: Tuple[int, int]):
    self.drag_press(src, dst)
    self.drag_up(dst)

  def drag_press(self, src: Tuple[int, int], dst: Tuple[int, int]):
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

  def drag_up(self, dst: Tuple[int, int]):
    clickPos = win32api.MAKELONG(dst[0], dst[1])
    win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, clickPos)

# lParam = win32api.MAKELONG(90, 480)
# lParam = win32api.MAKELONG(140, 480)
# lParam = win32api.MAKELONG(90, 530)
# lParam = win32api.MAKELONG(40, 580) # SP
# lParam = win32api.MAKELONG(340, 580) # Summon
# lParam = win32api.MAKELONG(190, 640) # Level
# lParam = win32api.MAKELONG(130, 640) # Level
# lParam = win32api.MAKELONG(40, 390) # Emoji
# lParam = win32api.MAKELONG(100, 390) # Emoji

class DiceControl(Control):
  def __init__(self, _hwnd):
    Control.__init__(self, _hwnd)

  def getBoardDiceXY(self, idx: int):
    col = 5
    idx_r = idx // col
    idx_c = idx % col

    leftTopDice = (90, 480)
    offset_x = 50
    offset_y = 50
    return (leftTopDice[0]+idx_c*offset_x, leftTopDice[1]+idx_r*offset_y)

  def getLevelDiceXY(self, idx: int):
    leftDice = (70, 640)
    offset_x = 60
    return (leftDice[0]+idx*offset_x, leftDice[1])

  def getEmojiXY(self, idx: int):
    leftEmoji = (40, 390)
    offset_x = 60
    return (leftEmoji[0]+idx*offset_x, leftEmoji[1])

  def mergeDice(self, src: int, dst: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    dst_xy = self.getBoardDiceXY(dst-1) # rescale [1~15] to [0~14]
    self.drag(src_xy, dst_xy)

  def dragPressDice(self, src: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    self.drag_press(src_xy, (190, 400))

  def dragUpDice(self, src: int):
    src_xy = self.getBoardDiceXY(src-1) # rescale [1~15] to [0~14]
    self.drag_up((190, 400))

  def summonDice(self):
    self.leftClick((340, 580))

  def levelUpSP(self):
    self.leftClick((40, 580))

  def levelUpDice(self, idx: int):
    dice_xy = self.getLevelDiceXY(idx-1) # rescale [1~5] to [0~4]
    self.leftClick(dice_xy)

  def openEmojiDialog(self):
    self.leftClick((40, 390))

  def sendEmoji(self, idx: int):
    self.openEmojiDialog()
    emoji_xy = self.getEmojiXY(idx-1) # rescale [1~5] to [0~4]
    time.sleep(0.4) # wait for dialog open
    self.leftClick(emoji_xy)

  def BMOpponent(self, times = 5):
    for i in range(times):
      self.sendEmoji(1)
      time.sleep(0.2)