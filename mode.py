from enum import IntEnum

class ControlMode(IntEnum):
  WIN32API = 0
  ADB = 1

class Emulator(IntEnum):
  BLUESTACKS = 0
  NOX = 1