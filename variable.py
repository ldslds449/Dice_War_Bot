from typing import Tuple
from mode import *
from configparser import ConfigParser
import os

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
    self.battle_xy = None
    self.ad_close_xy = None
    self.spell_xy = None
    self.damage_list_xy = None
  
    self.extract_dice_size_wh = None
    self.extract_dice_lu_size_wh = None
    self.extract_sp_lu_size_wh = None
    self.extract_summon_lu_size_wh = None
    self.extract_level_dice_lu_size_wh = None
    self.extract_spell_lu_size_wh = None
    self.emoji_dialog_wh = None

    self.detect_dice_mode = None

    self.zoom_ratio = 1.0
    self.random_offset = 0
    self.detect_delay = None
    self.restart_delay = None

    self.col = 5 # constant
    self.row = 3 # constant
    self.board_size = self.row * self.col # constant
    self.party_dice_size = 5 # constant
    self.emoji_size = 5 # constant
    self.config_file_name = 'config.ini' # constant
    self.update_file_name = 'update.md' # constant

    self.emulator_mode = None
    self.control_mode = None
    self.adb_mode = None
    self.adb_port = None
    self.adb_ip = None
    self.adb_id = None

    self.dice_party = None

  ### read from config file ###
  def loadFromConfigFile(self):
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
    self.battle_xy = str2Type(config.get('Coordinate', 'BattleXY', fallback='0 0'))
    self.ad_close_xy = str2Type(config.get('Coordinate', 'ADCloseXY', fallback='0 0'))
    self.spell_xy = str2Type(config.get('Coordinate', 'SpellXY', fallback='0 0'))
    self.damage_list_xy = str2Type(config.get('Coordinate', 'DamageListXY', fallback='0 0'))
    self.extract_dice_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceSizeWH', fallback='50 50'))
    self.extract_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceLuSizeWH', fallback='40 40'))
    self.extract_sp_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSpLuSizeWH', fallback='5 5'))
    self.extract_summon_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSummonLuSizeWH', fallback='3 3'))
    self.extract_level_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractLevelDiceLuSizeWH', fallback='40 40'))
    self.extract_spell_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSpellLuSizeWH', fallback='5 5'))
    self.emoji_dialog_wh = str2Type(config.get('Coordinate', 'EmojiDialogWH', fallback='30 25'))
    self.random_offset = str2Type(config.get('Coordinate', 'RandomOffset', fallback='0'))
    self.zoom_ratio = str2Type(config.get('Window', 'ZoomRatio', fallback='1'), float)
    self.emulator_mode = Emulator(str2Type(config.get('Mode', 'Emulator', fallback='0')))
    self.control_mode = ControlMode(str2Type(config.get('Mode', 'ControlMode', fallback='0')))
    self.detect_dice_mode = DetectDiceMode(str2Type(config.get('Mode', 'DetectDiceMode', fallback='0')))
    self.adb_mode = ADBMode(str2Type(config.get('Mode', 'ADBMode', fallback='0')))
    self.adb_ip = config.get('ADB', 'IP', fallback='127.0.0.1')
    self.adb_port = str2Type(config.get('ADB', 'Port', fallback='5555'), int)
    self.adb_id = str2Type(config.get('ADB', 'ID', fallback=''), str)
    self.dice_party = list(str2Type(config.get('Dice', 'DiceParty', fallback=''), str))
    self.detect_delay = str2Type(config.get('Detect', 'DetectDelay', fallback='0.0'), float)
    self.restart_delay = str2Type(config.get('Detect', 'RestartDelay', fallback='10.0'), float)

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
    config.set('Coordinate', 'BattleXY', type2Str(self.battle_xy))
    config.set('Coordinate', 'ADCloseXY', type2Str(self.ad_close_xy))
    config.set('Coordinate', 'SpellXY', type2Str(self.spell_xy))
    config.set('Coordinate', 'DamageListXY', type2Str(self.damage_list_xy))
    config.set('Coordinate', 'ExtractDiceSizeWH', type2Str(self.extract_dice_size_wh))
    config.set('Coordinate', 'ExtractDiceLuSizeWH', type2Str(self.extract_dice_lu_size_wh))
    config.set('Coordinate', 'ExtractSpLuSizeWH', type2Str(self.extract_sp_lu_size_wh))
    config.set('Coordinate', 'ExtractSummonLuSizeWH', type2Str(self.extract_summon_lu_size_wh))
    config.set('Coordinate', 'ExtractLevelDiceLuSizeWH', type2Str(self.extract_level_dice_lu_size_wh))
    config.set('Coordinate', 'ExtractSpellLuSizeWH', type2Str(self.extract_spell_lu_size_wh))
    config.set('Coordinate', 'EmojiDialogWH', type2Str(self.emoji_dialog_wh))
    config.set('Coordinate', 'RandomOffset', type2Str(self.random_offset))
    config.add_section('Window')
    config.set('Window', 'ZoomRatio', type2Str(self.zoom_ratio))
    config.add_section('Mode')
    config.set('Mode', 'Emulator', type2Str(int(self.emulator_mode)))
    config.set('Mode', 'ControlMode', type2Str(int(self.control_mode)))
    config.set('Mode', 'DetectDiceMode', type2Str(int(self.detect_dice_mode)))
    config.set('Mode', 'ADBMode', type2Str(int(self.adb_mode)))
    config.add_section('ADB')
    config.set('ADB', 'IP', self.adb_ip)
    config.set('ADB', 'Port', type2Str(self.adb_port))
    config.set('ADB', 'ID', self.adb_id)
    config.add_section('Dice')
    config.set('Dice', 'DiceParty', type2Str(tuple(self.dice_party)))
    config.add_section('Detect')
    config.set('Detect', 'DetectDelay', type2Str(self.detect_delay))
    config.set('Detect', 'RestartDelay', type2Str(self.restart_delay))

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

  def setBattleXY(self, _value: Tuple[int,int]):
    self.battle_xy = _value

  def setADCloseXY(self, _value: Tuple[int,int]):
    self.ad_close_xy = _value

  def setSpellXY(self, _value: Tuple[int,int]):
    self.spell_xy = _value

  def setDamageListXY(self, _value: Tuple[int,int]):
    self.damage_list_xy = _value

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

  def setExtractSpellLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_spell_lu_size_wh = _value

  def setEmojiDialogWH(self, _value: Tuple[int,int]):
    self.emoji_dialog_wh = _value

  def setZoomRatio(self, _value: float):
    self.zoom_ratio = _value

  def setEmulatorMode(self, _value: Emulator):
    self.emulator_mode = _value

  def setControlMode(self, _value: ControlMode):
    self.control_mode = _value

  def setDetectDiceMode(self, _value: DetectDiceMode):
    self.detect_dice_mode = _value

  def setADBMode(self, _value: ADBMode):
    self.adb_mode = _value

  def setADBIP(self, _value: str):
    self.adb_ip = _value

  def setADBPort(self, _value: int):
    self.adb_port = _value

  def setADBID(self, _value: str):
    self.adb_id = _value

  def setDiceParty(self, _value: list):
    self.dice_party = _value

  def setRandomOffset(self, _value: int):
    self.random_offset = _value

  def setDetectDelay(self, _value: float):
    self.detect_delay = _value
  
  def setRestartDelay(self, _value: float):
    self.restart_delay = _value

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

  def getBattleXY(self):
    return self.battle_xy

  def getADCloseXY(self):
    return self.ad_close_xy

  def getSpellXY(self):
    return self.spell_xy

  def getDamageListXY(self):
    return self.damage_list_xy

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

  def getExtractSpellLuSizeWH(self):
    return self.extract_spell_lu_size_wh

  def getEmojiDialogWH(self):
    return self.emoji_dialog_wh

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

  def getDetectDiceMode(self):
    return self.detect_dice_mode

  def getADBMode(self):
    return self.adb_mode

  def getADBIP(self):
    return self.adb_ip

  def getADBPort(self):
    return self.adb_port

  def getADBID(self):
    return self.adb_id

  def getDiceParty(self):
    return self.dice_party

  def getUpdateFileName(self):
    return self.update_file_name

  def getRandomOffset(self):
    return self.random_offset

  def getDetectDelay(self):
    return self.detect_delay
  
  def getRestartDelay(self):
    return self.restart_delay