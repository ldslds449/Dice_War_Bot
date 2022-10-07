import cv2
import win32gui
import win32ui
import traceback
from ctypes import windll
from PIL import Image

from control import *

class Screen:
    def __init__(self, _mode: ControlMode, _hwnd: int = None):
        self.mode = _mode
        self.hwnd = _hwnd
        if self.mode == ControlMode.WIN32API:
            if self.hwnd is None:
                raise Exception('Need hwnd in WIN32API mode')
        elif self.mode == ControlMode.ADB:
            pass

    def getWindowSizeInfo(self):
        left, top, right, bot = win32gui.GetWindowRect(self.hwnd)
        w = right - left
        h = bot - top
        return (left, top, w, h)

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