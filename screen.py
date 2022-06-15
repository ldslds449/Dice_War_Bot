import cv2
import win32gui
import win32ui
import traceback
from ctypes import windll
from PIL import Image
from typing import Tuple

from control import *

class Screen:
    def __init__(self, _mode: ControlMode, _hwnd: int = None, _adb_device_code: str = None):
        self.mode = _mode
        self.hwnd = _hwnd
        self.adb_device_code = _adb_device_code
        if self.mode == ControlMode.WIN32API:
            if self.mode is None:
                raise Exception('Need hwnd in WIN32API mode')
        elif self.mode == ControlMode.ADB:
            if self.adb_device_code is None:
                raise Exception('Need adb device code in ADB mode')

    def getWindowSizeInfo(self):
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        w = right - left
        h = bot - top
        return (left, top, w, h)

    def resizeWindow(self, size: Tuple[int,int]):
        old_info = self.getWindowSizeInfo()
        w_offset = size[0] - old_info[2]
        h_offset = size[1] - old_info[3]
        win32gui.MoveWindow(self.hwnd, 
            old_info[0] - w_offset//2, 
            old_info[1] - h_offset//2, 
            size[0], size[1], True)

    # return isSuccess, image
    def getScreenShot(self, zoom_ratio: float):
        if self.mode == ControlMode.WIN32API:
            left, top, w, h = self.getWindowSizeInfo()
            # windows zoom setting
            w = int(w * zoom_ratio)
            h = int(h * zoom_ratio)

            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), 3)
            print(result)

            # result = saveDC.BitBlt((0, 0), (w, h), mfcDC, (left, top), win32con.SRCCOPY)

            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            if bmpinfo['bmWidth'] != 1 or bmpinfo['bmHeight'] != 1:
                im = Image.frombuffer(
                    'RGB',
                    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                    bmpstr, 'raw', 'BGRX', 0, 1)
            else:
                im = None

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)

            return ((im is not None), im)
        elif self.mode == ControlMode.ADB:
            try:
                img = ADB.screenshot()
                height, width = img.shape[:2]
                img = cv2.resize(img, (int(width*zoom_ratio), int(height*zoom_ratio)))
            except:
                print(traceback.format_exc())
                return (False, None)
            return (True, img)