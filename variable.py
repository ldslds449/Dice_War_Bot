from typing import Tuple
from mode import *
from configparser import ConfigParser

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
    self.merge_float_location_xy = None
    self.battle_xy = None
    self.ad_close_xy = None
    self.spell_xy = None
    self.damage_list_xy = None
    self.party_list_1v1_left_xy = None
    self.party_list_1v1_offset_x = None
    self.trophy_left_top_xy = None
    self.checkpoint_start_xy = None
    self.checkpoint_end_xy = None
    self.wave_left_top_xy = None
  
    self.extract_dice_size_wh = None
    self.extract_dice_lu_size_wh = None
    self.extract_summon_lu_size_wh = None
    self.extract_level_dice_lu_size_wh = None
    self.extract_spell_lu_size_wh = None
    self.emoji_dialog_wh = None
    self.extract_party_list_1v1_size_wh = None
    self.extract_trophy_size_wh = None
    self.extract_wave_size_wh = None

    self.zoom_ratio = 1.0
    self.random_offset = 0
    self.detect_delay = None
    self.restart_delay = None
    self.screenshot_delay = None
    self.freeze_threshold = None
    self.focus_threshold = None
    self.wait_time_limit = None
    self.drag_time_scale = None
    self.close_dialog_threshold = None

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
    self.detect_dice_mode = None
    self.detect_star_mode = None

    self.adb_port = None
    self.adb_ip = None
    self.adb_id = None

    self.max_fps = None
    self.bitrate = None
    self.flip_screen = None
    self.show_screen = None

    self.battle_mode = None
    self.last_game = None
    self.top_window = None
    self.watch_ad = None
    self.restart_app = None
    self.notify_result = None
    self.dev_mode = None

    self.win = None
    self.lose = None

    self.dice_party = None

    self.line_notify_token = None

    self.emulator_name = None
    self.emulator_path = None
    self.run_emulator_delay = None

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
    self.board_dice_offset_xy = str2Type(config.get('Coordinate', 'BoardDiceOffsetXY', fallback='0.0 0.0'), float)
    self.level_dice_left_xy = str2Type(config.get('Coordinate', 'LevelDiceLeftXY', fallback='0 0'))
    self.level_dice_offset_x = str2Type(config.get('Coordinate', 'LevelDiceOffsetX', fallback='0'))
    self.emoji_dialog_xy = str2Type(config.get('Coordinate', 'EmojiDialogXY', fallback='0 0'))
    self.emoji_left_xy = str2Type(config.get('Coordinate', 'EmojiLeftXY', fallback='0 0'))
    self.emoji_offset_x = str2Type(config.get('Coordinate', 'EmojiOffsetX', fallback='0'))
    self.summon_dice_xy = str2Type(config.get('Coordinate', 'SummonDiceXY', fallback='0 0'))
    self.merge_float_location_xy = str2Type(config.get('Coordinate', 'MergeFloatLocationXY', fallback='0 0'))
    self.battle_xy = str2Type(config.get('Coordinate', 'BattleXY', fallback='0 0'))
    self.ad_close_xy = str2Type(config.get('Coordinate', 'ADCloseXY', fallback='0 0'))
    self.spell_xy = str2Type(config.get('Coordinate', 'SpellXY', fallback='0 0'))
    self.damage_list_xy = str2Type(config.get('Coordinate', 'DamageListXY', fallback='0 0'))
    self.party_list_1v1_left_xy = str2Type(config.get('Coordinate', 'PartyList1v1LeftXY', fallback='0 0'))
    self.party_list_1v1_offset_x = str2Type(config.get('Coordinate', 'PartyList1v1OffsetX', fallback='0'))
    self.trophy_left_top_xy = str2Type(config.get('Coordinate', 'TrophyLeftTopXY', fallback='0 0'))
    self.checkpoint_start_xy = str2Type(config.get('Coordinate', 'CheckPointStartXY', fallback='0 0'))
    self.checkpoint_end_xy = str2Type(config.get('Coordinate', 'CheckPointEndXY', fallback='0 0'))
    self.wave_left_top_xy = str2Type(config.get('Coordinate', 'WaveLeftTopXY', fallback='0 0'))
    self.extract_dice_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceSizeWH', fallback='50 50'))
    self.extract_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractDiceLuSizeWH', fallback='40 40'))
    self.extract_summon_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSummonLuSizeWH', fallback='3 3'))
    self.extract_level_dice_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractLevelDiceLuSizeWH', fallback='40 40'))
    self.extract_spell_lu_size_wh = str2Type(config.get('Coordinate', 'ExtractSpellLuSizeWH', fallback='5 5'))
    self.emoji_dialog_wh = str2Type(config.get('Coordinate', 'EmojiDialogWH', fallback='30 25'))
    self.extract_party_list_1v1_size_wh = str2Type(config.get('Coordinate', 'ExtractPartyList1v1SizeWH', fallback='20 20'))
    self.extract_trophy_size_wh = str2Type(config.get('Coordinate', 'ExtractTrophySizeWH', fallback='0 0'))
    self.extract_wave_size_wh = str2Type(config.get('Coordinate', 'ExtractWaveSizeWH', fallback='0 0'))
    self.random_offset = str2Type(config.get('Coordinate', 'RandomOffset', fallback='0'))
    self.zoom_ratio = str2Type(config.get('Window', 'ZoomRatio', fallback='1'), float)
    self.emulator_mode = Emulator(str2Type(config.get('Mode', 'Emulator', fallback='0')))
    self.control_mode = ControlMode(str2Type(config.get('Mode', 'ControlMode', fallback='0')))
    self.detect_dice_mode = DetectDiceMode(str2Type(config.get('Mode', 'DetectDiceMode', fallback='0')))
    self.detect_star_mode = DetectStarMode(str2Type(config.get('Mode', 'DetectStarMode', fallback='0')))
    self.adb_mode = ADBMode(str2Type(config.get('Mode', 'ADBMode', fallback='0')))
    self.adb_ip = config.get('ADB', 'IP', fallback='127.0.0.1')
    self.adb_port = str2Type(config.get('ADB', 'Port', fallback='5555'), int)
    self.adb_id = str2Type(config.get('ADB', 'ID', fallback=''), str)
    self.max_fps = str2Type(config.get('ADB', 'MaxFPS', fallback='15'), int)
    self.bitrate = str2Type(config.get('ADB', 'BitRate', fallback='8000000'), int)
    self.flip_screen = str2Type(config.get('Window', 'FlipScreen', fallback='1'))
    self.show_screen = str2Type(config.get('Window', 'ShowScreen', fallback='1'))
    self.dice_party = list(str2Type(config.get('Dice', 'DiceParty', fallback=''), str))
    self.detect_delay = str2Type(config.get('Detect', 'DetectDelay', fallback='0.0'), float)
    self.restart_delay = str2Type(config.get('Detect', 'RestartDelay', fallback='10.0'), float)
    self.screenshot_delay = str2Type(config.get('Detect', 'ScreenshotDelay', fallback='0.0'), float)
    self.freeze_threshold = str2Type(config.get('Detect', 'FreezeThreshold', fallback='50'))
    self.focus_threshold = config.get('Detect', 'FocusThreshold', fallback='5') 
    self.wait_time_limit = config.get('Detect', 'WaitTimeLimit', fallback='90') 
    self.drag_time_scale = config.get('Control', 'DragTimeScale', fallback='600') 
    self.close_dialog_threshold = config.get('Detect', 'CloseDialogThreshold', fallback='30') 
    self.battle_mode = config.get('Flag', 'BattleMode', fallback='2v2') 
    # eval('True') = True, eval('False') = False
    self.last_game = str2Type(config.get('Flag', 'LastGame', fallback='False'), eval) 
    self.top_window = str2Type(config.get('Flag', 'TopWindow', fallback='False'), eval)
    self.watch_ad = str2Type(config.get('Flag', 'WatchAD', fallback='False'), eval)
    self.restart_app = str2Type(config.get('Flag', 'RestartApp', fallback='False'), eval)
    self.notify_result = str2Type(config.get('Flag', 'NotifyResult', fallback='False'), eval)
    self.dev_mode = str2Type(config.get('Flag', 'DevMode', fallback='False'), eval)
    self.win = str2Type(config.get('Record', 'Win', fallback='0'))
    self.lose = str2Type(config.get('Record', 'Lose', fallback='0'))
    self.line_notify_token = config.get('Notify', 'LineNotifyToken', fallback='')
    self.emulator_name = config.get('Emulator', 'EmulatorName', fallback='BlueStacks')
    self.emulator_path = config.get('Emulator', 'EmulatorPath', fallback='')
    self.run_emulator_delay = str2Type(config.get('Emulator', 'RunEmulatorDelay', fallback='60'), int)

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
    config.set('Coordinate', 'MergeFloatLocationXY', type2Str(self.merge_float_location_xy))
    config.set('Coordinate', 'BattleXY', type2Str(self.battle_xy))
    config.set('Coordinate', 'ADCloseXY', type2Str(self.ad_close_xy))
    config.set('Coordinate', 'SpellXY', type2Str(self.spell_xy))
    config.set('Coordinate', 'DamageListXY', type2Str(self.damage_list_xy))
    config.set('Coordinate', 'PartyList1v1LeftXY', type2Str(self.party_list_1v1_left_xy))
    config.set('Coordinate', 'PartyList1v1OffsetX', type2Str(self.party_list_1v1_offset_x))
    config.set('Coordinate', 'TrophyLeftTopXY', type2Str(self.trophy_left_top_xy))
    config.set('Coordinate', 'CheckPointStartXY', type2Str(self.checkpoint_start_xy))
    config.set('Coordinate', 'CheckPointEndXY', type2Str(self.checkpoint_end_xy))
    config.set('Coordinate', 'WaveLeftTopXY', type2Str(self.wave_left_top_xy))
    config.set('Coordinate', 'ExtractDiceSizeWH', type2Str(self.extract_dice_size_wh))
    config.set('Coordinate', 'ExtractDiceLuSizeWH', type2Str(self.extract_dice_lu_size_wh))
    config.set('Coordinate', 'ExtractSummonLuSizeWH', type2Str(self.extract_summon_lu_size_wh))
    config.set('Coordinate', 'ExtractLevelDiceLuSizeWH', type2Str(self.extract_level_dice_lu_size_wh))
    config.set('Coordinate', 'ExtractSpellLuSizeWH', type2Str(self.extract_spell_lu_size_wh))
    config.set('Coordinate', 'EmojiDialogWH', type2Str(self.emoji_dialog_wh))
    config.set('Coordinate', 'ExtractPartyList1v1SizeWH', type2Str(self.extract_party_list_1v1_size_wh))
    config.set('Coordinate', 'ExtractTrophySizeWH', type2Str(self.extract_trophy_size_wh))
    config.set('Coordinate', 'ExtractWaveSizeWH', type2Str(self.extract_wave_size_wh))
    config.set('Coordinate', 'RandomOffset', type2Str(self.random_offset))
    config.add_section('Window')
    config.set('Window', 'ZoomRatio', type2Str(self.zoom_ratio))
    config.set('Window', 'FlipScreen', type2Str(self.flip_screen))
    config.set('Window', 'ShowScreen', type2Str(self.show_screen))
    config.add_section('Mode')
    config.set('Mode', 'Emulator', type2Str(int(self.emulator_mode)))
    config.set('Mode', 'ControlMode', type2Str(int(self.control_mode)))
    config.set('Mode', 'DetectDiceMode', type2Str(int(self.detect_dice_mode)))
    config.set('Mode', 'DetectStarMode', type2Str(int(self.detect_star_mode)))
    config.set('Mode', 'ADBMode', type2Str(int(self.adb_mode)))
    config.add_section('ADB')
    config.set('ADB', 'IP', self.adb_ip)
    config.set('ADB', 'Port', type2Str(self.adb_port))
    config.set('ADB', 'ID', self.adb_id)
    config.set('ADB', 'MaxFPS', type2Str(self.max_fps))
    config.set('ADB', 'BitRate', type2Str(self.bitrate))
    config.add_section('Dice')
    config.set('Dice', 'DiceParty', type2Str(tuple(self.dice_party)))
    config.add_section('Detect')
    config.set('Detect', 'DetectDelay', type2Str(self.detect_delay))
    config.set('Detect', 'RestartDelay', type2Str(self.restart_delay))
    config.set('Detect', 'ScreenshotDelay', type2Str(self.screenshot_delay))
    config.set('Detect', 'FreezeThreshold', type2Str(self.freeze_threshold))
    config.set('Detect', 'FocusThreshold', type2Str(self.focus_threshold))
    config.set('Detect', 'WaitTimeLimit', type2Str(self.wait_time_limit))
    config.set('Detect', 'CloseDialogThreshold', type2Str(self.close_dialog_threshold))
    config.add_section('Control')
    config.set('Control', 'DragTimeScale', type2Str(self.drag_time_scale))
    config.add_section('Flag')
    config.set('Flag', 'BattleMode', self.battle_mode)
    config.set('Flag', 'LastGame', type2Str(self.last_game))
    config.set('Flag', 'TopWindow', type2Str(self.top_window))
    config.set('Flag', 'WatchAD', type2Str(self.watch_ad))
    config.set('Flag', 'RestartApp', type2Str(self.restart_app))
    config.set('Flag', 'NotifyResult', type2Str(self.notify_result))
    config.set('Flag', 'DevMode', type2Str(self.dev_mode))
    config.add_section('Record')
    config.set('Record', 'Win', type2Str(self.win))
    config.set('Record', 'Lose', type2Str(self.lose))
    config.add_section('Notify')
    config.set('Notify', 'LineNotifyToken', self.line_notify_token)
    config.add_section('Emulator')
    config.set('Emulator', 'EmulatorName', self.emulator_name)
    config.set('Emulator', 'EmulatorPath', self.emulator_path)
    config.set('Emulator', 'RunEmulatorDelay', type2Str(self.run_emulator_delay))

    with open(self.config_file_name, 'w') as f:
      config.write(f)

  ### set ###

  def setBoardDiceLeftTopXY(self, _value: Tuple[int,int]):
    self.board_dice_left_top_xy = _value

  def setBoardDiceOffsetXY(self, _value: Tuple[float,float]):
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
  
  def setPartyList1v1LeftXY(self, _value: Tuple[int,int]):
    self.party_list_1v1_left_xy = _value

  def setPartyList1v1OffsetX(self, _value: Tuple[int,int]):
    self.party_list_1v1_offset_x = _value

  def setTrophyLeftTopXY(self, _value: Tuple[int,int]):
    self.trophy_left_top_xy = _value

  def setCheckPointStartXY(self, _value: Tuple[int,int]):
    self.checkpoint_start_xy = _value

  def setCheckPointEndXY(self, _value: Tuple[int,int]):
    self.checkpoint_end_xy = _value

  def setWaveLeftTopXY(self, _value: Tuple[int,int]):
    self.wave_left_top_xy = _value

  def setExtractDiceSizeWH(self, _value: Tuple[int,int]):
    self.extract_dice_size_wh = _value

  def setExtractDiceLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_dice_lu_size_wh = _value

  def setExtractSummonLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_summon_lu_size_wh = _value

  def setExtractLevelDiceLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_level_dice_lu_size_wh = _value

  def setExtractSpellLuSizeWH(self, _value: Tuple[int,int]):
    self.extract_spell_lu_size_wh = _value

  def setEmojiDialogWH(self, _value: Tuple[int,int]):
    self.emoji_dialog_wh = _value

  def setExtractPartyList1v1SizeWH(self, _value: Tuple[int,int]):
    self.extract_party_list_1v1_size_wh = _value

  def setExtractTrophySizeWH(self, _value: Tuple[int,int]):
    self.extract_trophy_size_wh = _value

  def setExtractWaveSizeWH(self, _value: Tuple[int,int]):
    self.extract_wave_size_wh = _value

  def setZoomRatio(self, _value: float):
    self.zoom_ratio = _value

  def setEmulatorMode(self, _value: Emulator):
    self.emulator_mode = _value

  def setControlMode(self, _value: ControlMode):
    self.control_mode = _value

  def setDetectDiceMode(self, _value: DetectDiceMode):
    self.detect_dice_mode = _value
  
  def setDetectStarMode(self, _value: DetectStarMode):
    self.detect_star_mode = _value

  def setADBMode(self, _value: ADBMode):
    self.adb_mode = _value

  def setADBIP(self, _value: str):
    self.adb_ip = _value

  def setADBPort(self, _value: int):
    self.adb_port = _value

  def setADBID(self, _value: str):
    self.adb_id = _value

  def setMaxFPS(self, _value: int):
    self.max_fps = _value

  def setBitRate(self, _value: int):
    self.bitrate = _value

  def setFlipScreen(self, _value: int):
    self.flip_screen = _value

  def setShowScreen(self, _value: int):
    self.show_screen = _value

  def setDiceParty(self, _value: list):
    self.dice_party = _value

  def setRandomOffset(self, _value: int):
    self.random_offset = _value

  def setDetectDelay(self, _value: float):
    self.detect_delay = _value
  
  def setRestartDelay(self, _value: float):
    self.restart_delay = _value

  def setScreenshotDelay(self, _value: float):
    self.screenshot_delay = _value

  def setFreezeThreshold(self, _value: int):
    self.freeze_threshold = _value

  def setFocusThreshold(self, _value: int):
    self.focus_threshold = _value

  def setWaitTimeLimit(self, _value: int):
    self.wait_time_limit = _value

  def setDragTimeScale(self, _value: int):
    self.drag_time_scale = _value
    
  def setCloseDialogThreshold(self, _value: int):
    self.close_dialog_threshold = _value

  def setBattleMode(self, _value: str):
    self.battle_mode = _value

  def setLastGame(self, _value: bool):
    self.last_game = _value

  def setTopWindow(self, _value: bool):
    self.top_window = _value

  def setWatchAD(self, _value: bool):
    self.watch_ad = _value

  def setRestartApp(self, _value: bool):
    self.restart_app = _value

  def setNotifyResult(self, _value: bool):
    self.notify_result = _value

  def setDevMode(self, _value: bool):
    self.dev_mode = _value

  def setWin(self, _value: int):
    self.win = _value

  def setLose(self, _value: int):
    self.lose = _value

  def setLineNotifyToken(self, _value: str):
    self.line_notify_token = _value

  def setEmulatorName(self, _value: str):
    self.emulator_name = _value
  
  def setEmulatorPath(self, _value: str):
    self.emulator_path = _value

  def setRunEmulatorDelay(self, _value: str):
    self.run_emulator_delay = _value

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

  def getPartyList1v1LeftXY(self):
    return self.party_list_1v1_left_xy

  def getPartyList1v1OffsetX(self):
    return self.party_list_1v1_offset_x

  def getTrophyLeftTopXY(self):
    return self.trophy_left_top_xy

  def getCheckPointStartXY(self):
    return self.checkpoint_start_xy

  def getCheckPointEndXY(self):
    return self.checkpoint_end_xy

  def getWaveLeftTopXY(self):
    return self.wave_left_top_xy

  def getExtractDiceSizeWH(self):
    return self.extract_dice_size_wh

  def getExtractDiceLuSizeWH(self):
    return self.extract_dice_lu_size_wh

  def getExtractSummonLuSizeWH(self):
    return self.extract_summon_lu_size_wh

  def getExtractLevelDiceLuSizeWH(self):
    return self.extract_level_dice_lu_size_wh

  def getExtractSpellLuSizeWH(self):
    return self.extract_spell_lu_size_wh

  def getEmojiDialogWH(self):
    return self.emoji_dialog_wh
  
  def getExtractPartyList1v1SizeWH(self):
    return self.extract_party_list_1v1_size_wh

  def getExtractTrophySizeWH(self):
    return self.extract_trophy_size_wh

  def getExtractWaveSizeWH(self):
    return self.extract_wave_size_wh

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

  def getDetectStarMode(self):
    return self.detect_star_mode

  def getADBMode(self):
    return self.adb_mode

  def getADBIP(self):
    return self.adb_ip

  def getADBPort(self):
    return self.adb_port

  def getADBID(self):
    return self.adb_id

  def getMaxFPS(self):
    return self.max_fps

  def getBitRate(self):
    return self.bitrate

  def getFlipScreen(self):
    return self.flip_screen

  def getShowScreen(self):
    return self.show_screen

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

  def getScreenshotDelay(self):
    return self.screenshot_delay

  def getFreezeThreshold(self):
    return self.freeze_threshold

  def getFocusThreshold(self):
    return self.focus_threshold

  def getWaitTimeLimit(self):
    return self.wait_time_limit

  def getDragTimeScale(self):
    return self.drag_time_scale

  def getCloseDialogThreshold(self):
    return self.close_dialog_threshold

  def getBattleMode(self):
    return self.battle_mode

  def getLastGame(self):
    return self.last_game

  def getTopWindow(self):
    return self.top_window

  def getWatchAD(self):
    return self.watch_ad

  def getRestartApp(self):
    return self.restart_app

  def getNotifyResult(self):
    return self.notify_result

  def getDevMode(self):
    return self.dev_mode

  def getWin(self):
    return self.win

  def getLose(self):
    return self.lose

  def getLineNotifyToken(self):
    return self.line_notify_token

  def getEmulatorName(self):
    return self.emulator_name

  def getEmulatorPath(self):
    return self.emulator_path

  def getRunEmulatorDelay(self):
    return self.run_emulator_delay