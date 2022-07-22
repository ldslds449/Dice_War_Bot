import psutil

from mode import *

class Resource:
  @staticmethod
  def get_pid(emu):
    if not hasattr(Resource, 'pid'):
      if emu == Emulator.BLUESTACKS:
        name = 'HD-Player.exe'
      elif emu == Emulator.NOX:
        name = '夜神模擬器'

      Resource.pid = None
      for proc in psutil.process_iter():
        if proc.name() == name:
          Resource.pid = proc.pid

    return Resource.pid

  @staticmethod
  def getCPU(emu):
    total = 0.0

    # emulator
    if Resource.get_pid(emu) is not None:
      try:
        emu_process = psutil.Process(Resource.get_pid(emu))
        total += emu_process.cpu_percent(interval=1)
      except:
        del Resource.pid
    # python
    total += psutil.Process().cpu_percent(interval=1)

    return total

  @staticmethod
  def getMEM(emu):
    total = 0.0

    # emulator
    if Resource.get_pid(emu) is not None:
      try:
        emu_process = psutil.Process(Resource.get_pid(emu))
        total += emu_process.memory_info().rss
      except:
        del Resource.pid
    # python
    total += psutil.Process().memory_info().rss

    return total
    