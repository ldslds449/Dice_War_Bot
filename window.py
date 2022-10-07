import win32gui
import win32con
from typing import Tuple

from mode import *

class Window:
  mainWindowID = None
  windowID = None

  @staticmethod
  def resizeWindow(self, size: Tuple[int,int]):
    old_info = self.getWindowSizeInfo()
    w_offset = size[0] - old_info[2]
    h_offset = size[1] - old_info[3]
    win32gui.MoveWindow(self.hwnd, 
        old_info[0] - w_offset//2, 
        old_info[1] - h_offset//2, 
        size[0], size[1], True)

  @staticmethod
  def getWindowID(mode, name) -> None:
    def enumHandler(hwnd, _):
      windowText = win32gui.GetWindowText(hwnd)
      if mode == Emulator.BLUESTACKS:
        if name in windowText:
          hwndChild = win32gui.GetWindow(hwnd, win32con.GW_CHILD)
          Window.mainWindowID = hwnd
          Window.windowID = hwndChild
      elif mode == Emulator.NOX:
        if name in windowText:
          Window.mainWindowID = hwnd
          Window.windowID = hwnd

    win32gui.EnumWindows(enumHandler, None)
    
    # check if is valid
    if Window.mainWindowID == 0 or Window.windowID == 0:
      raise RuntimeError('Window Not Found !!!')

  @staticmethod
  def existWindow(hwnd):
    return win32gui.IsWindow(hwnd)