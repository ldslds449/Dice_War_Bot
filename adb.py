import scrcpy
from typing import Tuple
from adbutils import adb

class ADB:
  packageName = 'com.percent.aos.randomdicewars'

  @staticmethod
  def click(xy: Tuple[int,int]):
    ADB.d.click(xy[0], xy[1])

  @staticmethod
  def swipe(src: Tuple[int,int], dst: Tuple[int,int], time: float):
    ADB.d.swipe(src[0], src[1], dst[0], dst[1], time)

  @staticmethod
  def back():
    ADB.d.keyevent('KEYCODE_BACK')

  @staticmethod
  def screenshot():
    return ADB.frame

  @staticmethod
  def connect(ip:str, port:int, id:str):
    if ip is not None:
      ADB.adb_device_code = f'{ip}:{port}'
      output = adb.connect(ADB.adb_device_code)
      success = 'connected' in output
      r = (output, success)
      if success:
        ADB.d = adb.device(serial=ADB.adb_device_code)
    else:
      ADB.adb_device_code = id
      ADB.d = adb.device(serial=id)
      r = ('Use device ID, skip connection', True)

    return r

  @staticmethod
  def createClient(updateScreen):
    # add screenshot listener
    def on_frame(frame):
      # If you set non-blocking (default) in constructor, the frame event receiver 
      # may receive None to avoid blocking event.
      if frame is not None:
        ADB.frame = frame
        updateScreen(ADB.frame)

    max_fps = 15
    bitrate = 8000000
    ADB.client = scrcpy.Client(device=ADB.d, max_fps=max_fps, bitrate=bitrate, flip=True)
    ADB.client.add_listener(scrcpy.EVENT_FRAME, on_frame)
    ADB.client.start(threaded=True)

  @staticmethod
  def disconnect():
    if hasattr(ADB, 'client'):
      ADB.client.stop()
    if hasattr(ADB, 'adb_device_code'):
      adb.disconnect(ADB.adb_device_code)

  @staticmethod
  def detectDiceWar():
    app_info = ADB.d.app_current()
    return (ADB.packageName in app_info.package, app_info.package)

  @staticmethod
  def restart():
    ADB.d.app_stop(ADB.packageName)
    ADB.d.app_start(ADB.packageName)
