import cv2
import win32gui
import win32ui
import win32con
import io
import cv2
import numpy as np
from PIL import Image
from typing import Tuple

from control import *

class Screen:
    def __init__(self, _mode: ControlMode, _hwnd: int = None, _ip: str = None, _port: int = None):
        self.mode = _mode
        self.hwnd = _hwnd
        self.ip = _ip
        self.port = _port
        if self.mode == ControlMode.WIN32API:
            if self.mode is None:
                raise Exception('Need hwnd in WIN32API mode')
        elif self.mode == ControlMode.ADB:
            if self.port is None or self.ip is None:
                raise Exception('Need ip and port in ADB mode')

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
            left = int(left * zoom_ratio)
            top = int(top * zoom_ratio)
            w = int(w * zoom_ratio)
            h = int(h * zoom_ratio)

            hdesktop = win32gui.GetDesktopWindow()
            hwndDC = win32gui.GetWindowDC(hdesktop)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

            saveDC.SelectObject(saveBitMap)

            result = saveDC.BitBlt((0, 0), (w, h), mfcDC, (left, top), win32con.SRCCOPY)

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
            win32gui.ReleaseDC(hdesktop, hwndDC)

            return ((im is not None), im)
        elif self.mode == ControlMode.ADB:
            command = f'adb -s {self.ip}:{self.port} shell screencap -p'
            result = ADB.sh(command)
            image_bytes = result.replace(b'\r\n', b'\n')
            img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            img = img.resize((int(img.width*zoom_ratio), int(img.height*zoom_ratio)))
            return (True, img)