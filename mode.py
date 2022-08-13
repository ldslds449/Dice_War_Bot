from enum import IntEnum

class ControlMode(IntEnum):
  WIN32API = 0
  ADB = 1

class Emulator(IntEnum):
  BLUESTACKS = 0
  NOX = 1

class ExtractMode(IntEnum):
  LEFTTOP = 0
  CENTER = 1

class DetectDiceMode(IntEnum):
  HIST = 0
  TEMPLATE = 1
  DHASH = 2
  MSSSIM = 3
  COMBINE = 4
  HIST_COMBINE = 5
  HIST_RGB = 6

class DetectStarMode(IntEnum):
  COMPUTER_VERSION = 0
  ML_SVC = 1

class BattleMode(IntEnum):
  BATTLE_1V1 = 0
  BATTLE_2V2 = 1
  BATTLE_ARCADE = 2

class Status(IntEnum):
  LOBBY = 0
  WAIT = 1
  GAME = 2
  FINISH = 3
  TROPHY = 4
  FINISH_ANIMATION = 5
  ARCADE = 6

class ADBMode(IntEnum):
  IP = 0
  ID = 1