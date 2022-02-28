import win32gui
import win32ui
import win32con
from PIL import Image
from typing import Tuple

def getWindowSizeInfo(hwnd_target: int):
    left, top, right, bot = win32gui.GetWindowRect(hwnd_target)
    w = right - left
    h = bot - top
    return (left, top, w, h)

def resizeWindow(hwnd_target: int, size: Tuple[int,int]):
    old_info = getWindowSizeInfo(hwnd_target)
    w_offset = size[0] - old_info[2]
    h_offset = size[1] - old_info[3]
    win32gui.MoveWindow(hwnd_target, 
        old_info[0] - w_offset//2, 
        old_info[1] - h_offset//2, 
        size[0], size[1], True)

# return isSuccess, image
def getScreenShot(hwnd_target: int, zoom_ratio: float):

    left, top, w, h = getWindowSizeInfo(hwnd_target)
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

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hdesktop, hwndDC)

    # if result == None: Success
    return (result == None, im)