from enum import Enum

class ControlMode(Enum):
  WIN32API = 0
  ADB = 1

class Emulator(Enum):
  BLUESTACKS = 0
  NOX = 1