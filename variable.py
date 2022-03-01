from typing import Tuple
from mode import *
from configparser import ConfigParser
import os

# lParam = win32api.MAKELONG(90, 480)
# lParam = win32api.MAKELONG(140, 480)
# lParam = win32api.MAKELONG(90, 530)
# lParam = win32api.MAKELONG(40, 580) # SP
# lParam = win32api.MAKELONG(340, 580) # Summon
# lParam = win32api.MAKELONG(190, 640) # Level
# lParam = win32api.MAKELONG(130, 640) # Level
# lParam = win32api.MAKELONG(40, 390) # Emoji
# lParam = win32api.MAKELONG(100, 390) # Emoji

class Variable:
  def __init__(self):
    self.board_dice_left_top_xy = None
    self.board_dice_offset_xy = None
    self.level_dice_left_xy = None
    self.level_dice_offset_x = None
    self.emoji_dialog_xy = None
    self.emoji_left_xy = None
    self.emoji_offset_x = None
    self.summon_dice_xy = None
    self.level_sp_xy = None
    self.merge_float_location_xy = None
  
    self.extract_dice_size_wh = None
    self.extract_dice_lu_size_wh = None
    self.extract_sp_lu_size_wh = None
    self.extract_summon_lu_size_wh = None
    self.extract_level_dice_lu_size_wh = None

    self.zoom_ratio = 1.0
    self.col = 5 # constant
    self.row = 3 # constant
    self.board_size = self.row * self.col # constant
    self.party_dice_size = 5 # constant
    self.emoji_size = 5 # constant
    self.config_file_name = 'config.ini' # constant

    self.emulator_mode = None
    self.control_mode = None
    self.adb_port = 10311
    self.adb_ip = '127.0.0.1' # constant

  ### read from config file ###
  def loadFromConfigFile(self):
    if os.path.exists(self.getConfigFileName()):
      config = ConfigParser()
      config.read(self.getConfigFileName())

      def str2Type(s, t = int):
        s_split = s.split(' ')
        if len(s_split) > 1:
          return tuple([t(x) for x in s_split])
        else:
          return t(s)

      self.board_dice_left_top_xy = str2Type(config.get('Coordinate', 'BoardDiceLeftTopXY', fallback='0 0'))
      self.board_dice_offset_xy = str2Type(config.get('Coordinate', 'BoardDiceOffsetXY', fallback='0 0'))
      self.level_dice_left_xy = str2Type(config.get('Coordinate', 'LevelDiceLeftXY', fallback='0 0'))
      self.level_dice_offset_x = str2Type(config.get('Coordinate', 'LevelDiceOffsetX', fallback='0'))
      self.emoji_dialog_xy = str2Type(config.get('Coordinate', 'EmojiDialogXY', fallback='0 0'))
      self.emoji_left_xy = str2Type(config.get('Coordinate', 'EmojiLeftXY', fallback='0 0'))
      self.emoji_offset_x = str2Type(config.get('Coordinate', 'EmojiOffsetX', fallback='0'))
      self.summon_dice_xy = str2Type(config.get('Coordinate', 'SummonDiceXY', fallback='0 0'))
      self.level_sp_xy = str2Type(config.get('Coordinate', 'LevelSpXY', fallback='0 0'))
      self.merge_float_location_xy = str2Type(config.get('Coordinate', 'MergeFloatLocationXY', fallback='0 0'))
      self.extract_dice_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceSizeWH', fallback='50 50'))
      self.extract_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceLuSizeWH', fallback='40 40'))
      self.extract_sp_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSpLuSizeWH', fallback='5 5'))
      self.extract_summon_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSummonLuSizeWH', fallback='3 3'))
      self.extract_level_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractLevelDiceLuSizeWH', fallback='40 40'))
      self.zoom_ratio = str2Type(config.get('Window', 'ZoomRatio', fallback='1'), float)
      self.emulator_mode = str2Type(config.get('Mode', 'Emulator', fallback='0'))
      self.control_mode = str2Type(config.get('Mode', 'ControlMode', fallback='0'))
      self.adb_port = str2Type(config.get('ADB', 'Port', fallback='-1'))

      return True
    else:
      return False

  ### write to config file ###
  def saveToConfigFile(self):
    config = ConfigParser()

    def type2Str(t):
      if type(t) is tuple:
        return ' '.join([str(x) for x in list(t)])
      else:
        return str(t)

    config.add_section('Coordinate')
    config.set('Coordinate', 'BoardDiceLeftTopXY', type2Str(self.board_dice_left_top_xy))
    config.set('Coordinate', 'BoardDiceOffsetXY', type2Str(self.board_dice_offset_xy))
    config.set('Coordinate', 'LevelDiceLeftXY', type2Str(self.level_dice_left_xy))
    config.set('Coordinate', 'LevelDiceOffsetX', type2Str(self.level_dice_offset_x))
    config.set('Coordinate', 'EmojiDialogXY', type2Str(self.emoji_dialog_xy))
    config.set('Coordinate', 'EmojiLeftXY', type2Str(self.emoji_left_xy))
    config.set('Coordinate', 'EmojiOffsetX', type2Str(self.emoji_offset_x))
    config.set('Coordinate', 'SummonDiceXY', type2Str(self.summon_dice_xy))
    config.set('Coordinate', 'LevelSpXY', type2Str(self.level_sp_xy))
    config.set('Coordinate', 'MergeFloatLocationXY', type2Str(self.merge_float_location_xy))
    config.set('Coordinate', 'ExtractDiceSizeWH', type2Str(self.extract_dice_size_wh))
    config.set('Coordinate', 'ExtractDiceLuSizeWH', type2Str(self.extract_dice_lu_size_wh))
    config.set('Coordinate', 'ExtractSpLuSizeWH', type2Str(self.extract_sp_lu_size_wh))
    config.set('Coordinate', 'ExtractSummonLuSizeWH', type2Str(self.extract_summon_lu_size_wh))
    config.set('Coordinate', 'ExtractLevelDiceLuSizeWH', type2Str(self.extract_level_dice_lu_size_wh))
    config.add_section('Window')
    config.set('Window', 'ZoomRatio', type2Str(self.zoom_ratio))
    config.add_section('Mode')
    config.set('Mode', 'Emulator', type2Str(self.emulator_mode))
    config.set('Mode', 'ControlMode', type2Str(self.control_mode))
    config.add_section('ADB')
    config.set('ADB', 'Port', type2Str(self.adb_port))

    with open(self.config_file_name, 'w') as f:
      config.write(f)

  ### set ###

  def setBoardDiceLeftTopXY(self, _value: Tuple[int,int]):
    self.board_dice_left_top_xy = _value

  def setBoardDiceOffsetXY(self, _value: Tuple[int,int]):
    self.board_dice_offset_xy = _value

  def setLevelDiceLeftXY(self, _value: Tuple[int,int]):
    self.level_dice_left_xy = _value

  def setLevelDiceOffsetX(self, _value: int):
    self.level_dice_offset_x = _value

  def setEmojiDialogXY(self, _value: Tuple[int,int]):
    self.emoji_dialog_xy = _value

  def setEmojiLeftXY(self, _value: Tuple[int,int]):
    self.emoji_left_xy = _value

  def setEmojiOffsetX(self, _value: int):
    self.emoji_offset_x = _value

  def setSummonDiceXY(self, _value: Tuple[int,int]):
    self.summon_dice_xy = _value

  def setLevelSpXY(self, _value: Tuple[int,int]):
    self.level_sp_xy = _value

  def setMergeFloatLocationXY(self, _value: Tuple[int,int]):
    self.merge_float_location_xy = _value

  def setExtractDiceSizeWH(self, _value: Tuple[int,int]):
    self.extract_dice_size_wh = _value

  def setExtractDiceLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_dice_lu_size_wh = _value

  def setExtractSpLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_sp_lu_size_wh = _value

  def setExtractSummonLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_summon_lu_size_wh = _value

  def setExtractLevelDiceLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_level_dice_lu_size_wh = _value

  def setZoomRatio(self, _value: float):
    self.zoom_ratio = _value

  def setEmulatorMode(self, _value: Emulator):
    self.emulator_mode = _value

  def setControlMode(self, _value: ControlMode):
    self.control_mode = _value

  def setADBPort(self, _value: int):
    self.adb_port = _value

  ### get ###

  def getBoardDiceLeftTopXY(self):
    return self.board_dice_left_top_xy

  def getBoardDiceOffsetXY(self):
    return self.board_dice_offset_xy

  def getLevelDiceLeftXY(self):
    return self.level_dice_left_xy

  def getLevelDiceOffsetX(self):
    return self.level_dice_offset_x

  def getEmojiDialogXY(self):
    return self.emoji_dialog_xy

  def getEmojiLeftXY(self):
    return self.emoji_left_xy

  def getEmojiOffsetX(self):
    return self.emoji_offset_x

  def getSummonDiceXY(self):
    return self.summon_dice_xy

  def getLevelSpXY(self):
    return self.level_sp_xy

  def getMergeFloatLocationXY(self):
    return self.merge_float_location_xy

  def getExtractDiceSizeWH(self):
    return self.extract_dice_size_wh

  def getExtractDiceLuSizeWH(self):
    return self.extract_dice_lu_size_wh

  def getExtractSpLuSizeWH(self):
    return self.extract_sp_lu_size_wh

  def getExtractSummonLuSizeWH(self):
    return self.extract_summon_lu_size_wh

  def getExtractLevelDiceLuSizeWH(self):
    return self.extract_level_dice_lu_size_wh

  def getZoomRatio(self):
    return self.zoom_ratio

  def getCol(self):
    return self.col

  def getRow(self):
    return self.row

  def getBoardSize(self):
    return self.board_size

  def getPartyDiceSize(self):
    return self.party_dice_size

  def getEmojiSize(self):
    return self.emoji_size

  def getConfigFileName(self):
    return self.config_file_name

  def getEmulatorMode(self):
    return self.emulator_mode

  def getControlMode(self):
    return self.control_mode

  def getADBIP(self):
    return self.adb_ip

  def getADBPort(self):
    return self.adb_port