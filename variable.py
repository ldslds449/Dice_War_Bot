from typing import Tuple

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

    self.zoom_ratio = 1
    self.col = 5 # constant
    self.row = 3 # constant
    self.board_size = self.row * self.col # constant
    self.party_dice_size = 5 # constant

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