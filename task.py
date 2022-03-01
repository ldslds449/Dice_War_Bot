import sys
import win32gui
import win32con
import random as rd
from tkinter import Variable

from screen import *
from control import *
from detect import *
from variable import *
from mode import *
from action import *

class Task:
  def __init__(self, _action: Action):
    self.action = _action

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    self.windowID = None

    # self.targetDice = ["Healing", "Solar_O", "Rock", "Flash", "Mimic", "Blank", "Solar_X"]

    self.variable = Variable()
    self.variable.loadFromConfigFile()
    # self.variable.setBoardDiceLeftTopXY((90, 477))
    # self.variable.setBoardDiceOffsetXY((49, 49))
    # self.variable.setLevelDiceLeftXY((70, 640))
    # self.variable.setLevelDiceOffsetX(60)
    # self.variable.setEmojiDialogXY((40, 390))
    # self.variable.setEmojiLeftXY((40, 390))
    # self.variable.setEmojiOffsetX(60)
    # self.variable.setSummonDiceXY((340, 580))
    # self.variable.setLevelSpXY((40, 580))
    # self.variable.setMergeFloatLocationXY((190, 400))
    # self.variable.setExtractDiceSizeWH((50, 50))
    # self.variable.setExtractDiceLuSizeWH((40, 40))
    # self.variable.setExtractSpLuSizeWH((5, 5))
    # self.variable.setExtractSummonLuSizeWH((3, 3))
    # self.variable.setExtractLevelDiceLuSizeWH((3, 3))
    # self.variable.setZoomRatio(1)

    self.detect = Detect("./image", self.variable)

  def init(self):
    self.screen = Screen(self.variable.getControlMode(), _hwnd=self.windowID, 
      _ip=self.variable.getADBIP(), _port=self.variable.getADBPort())
    self.diceControl = DiceControl(self.variable.getControlMode(), _hwnd=self.windowID, 
      _ip=self.variable.getADBIP(), _port=self.variable.getADBPort())
    self.diceControl.setVariable(self.variable)

  def getWindowID(self):
    if self.variable.getEmulatorMode() == Emulator.BLUESTACKS:
      hwnd = win32gui.FindWindow(None, "BlueStacks")
      hwndChild = win32gui.GetWindow(hwnd, win32con.GW_CHILD)
      self.windowID = hwndChild
    elif self.variable.getEmulatorMode() == Emulator.NOX:
      hwnd = win32gui.FindWindow(None, "夜神模擬器")
      self.windowID = hwnd
    # check if is valid
    if self.windowID == 0:
      raise RuntimeError('Window Not Found !!!')

  def forAllDiceOnBoard(self, function):
    for i in range(self.variable.getBoardSize()):
      row = i // self.variable.getCol()
      col = i % self.variable.getCol()
      function(i, row, col)

  def findMergeDice(self, srcidx, exceptDice):
    self.diceControl.dragPressDice(srcidx)
    time.sleep(0.2)
    _, canMergeImage = self.screen.getScreenShot(self.variable.getZoomRatio())
    time.sleep(0.2)
    canMergeImage = self.detect.Image2OpenCV(canMergeImage)
    self.diceControl.dragUpDice()

    x = self.variable.getBoardDiceLeftTopXY()[0]
    y = self.variable.getBoardDiceLeftTopXY()[1]
    offset_x = self.variable.getBoardDiceOffsetXY()[0]
    offset_y = self.variable.getBoardDiceOffsetXY()[1]

    merge_dice_location = []
    def detectMerge(i, row, col):
      img = self.detect.extractImage(canMergeImage, 
        (x+col*offset_x, y+row*offset_y, 
        self.variable.getExtractDiceLuSizeWH()[0], self.variable.getExtractDiceLuSizeWH()[1]), ExtractMode.CENTER)
      img_lu = self.detect.getAverageLuminance(img)
      lu_offset = self.board_dice_lu[i] - img_lu
      canMerge = self.detect.canMergeDice(lu_offset)
      if canMerge and self.board_dice[i] != 'Blank':
        if exceptDice is None or self.board_dice[i] not in exceptDice:
          merge_dice_location.append(i)
      if i != 0 and i % self.variable.getCol() == 0 :
        print("")
      print(f"{'O' if canMerge else 'X'} {self.board_dice_lu[i]:4.1f} / {img_lu:4.1f}  ", end="")
      if i+1 == self.variable.getBoardSize():
        print("")

    self.forAllDiceOnBoard(detectMerge)
    
    return merge_dice_location
      
  def task(self):

    x = self.variable.getBoardDiceLeftTopXY()[0]
    y = self.variable.getBoardDiceLeftTopXY()[1]
    offset_x = self.variable.getBoardDiceOffsetXY()[0]
    offset_y = self.variable.getBoardDiceOffsetXY()[1]
    
    r, im = self.screen.getScreenShot(self.variable.getZoomRatio())
    im = self.detect.Image2OpenCV(im)

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    def detectDice(i, row, col):
      dice_xy = (x+col*offset_x, y+row*offset_y)
      img = self.detect.extractImage(im, 
        (dice_xy[0], dice_xy[1], 
        self.variable.getExtractDiceSizeWH()[0], self.variable.getExtractDiceSizeWH()[1]), ExtractMode.CENTER)
      res = self.detect.detectDice(img, self.variable.getDiceParty() + ['Blank'])

      dice_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, 
        (dice_xy[0], dice_xy[1], 
        self.variable.getExtractDiceLuSizeWH()[0], self.variable.getExtractDiceLuSizeWH()[1]), ExtractMode.CENTER))

      self.detect_board_dice_img.append(img)
      self.board_dice.append(res[0])
      self.board_dice_lu.append(dice_lu)

      if i != 0 and i % self.variable.getCol() == 0 :
        print("")
      print(f"{res[0]:10}", end="")
      if i+1 == self.variable.getBoardSize():
        print("")

    self.forAllDiceOnBoard(detectDice)

    summon_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, 
      (self.variable.getSummonDiceXY()[0], self.variable.getSummonDiceXY()[1], 
      self.variable.getExtractSummonLuSizeWH()[0], self.variable.getExtractSummonLuSizeWH()[1]), ExtractMode.CENTER))
    sp_lu = self.detect.getAverageLuminance(self.detect.extractImage(im, 
      (self.variable.getLevelSpXY()[0], self.variable.getLevelSpXY()[1],
      self.variable.getExtractSpLuSizeWH()[0], self.variable.getExtractSpLuSizeWH()[1]), ExtractMode.CENTER))
    level_lu = []
    for i in range(self.variable.getPartyDiceSize()):
      level_dice_x = self.variable.getLevelDiceLeftXY()[0] + i*self.variable.getLevelDiceOffsetX()
      level_dice_y = self.variable.getLevelDiceLeftXY()[1]
      level_lu.append(self.detect.getAverageLuminance(self.detect.extractImage(im, 
        (level_dice_x, level_dice_y,
        self.variable.getExtractLevelDiceLuSizeWH()[0], self.variable.getExtractLevelDiceLuSizeWH()[1]), ExtractMode.CENTER)))

    count = {}
    for dice in self.variable.getDiceParty() + ['Blank']:
      count[dice] = 0
    for dice in self.board_dice:
      count[dice] += 1
    location = {}
    for type in count:
      location[type] = []
    for idx, dice in enumerate(self.board_dice):
      location[dice].append(idx)
    count_sorted = sorted(count.items(), key=lambda x : x[1], reverse=True)
    countTotal = sum([x[1] for x in count.items() if x[0] != 'Blank'])

    self.action.action(
      self.diceControl, self.findMergeDice,
      count, count_sorted, location, self.board_dice, 
      self.detect.canSummon(summon_lu), self.detect.canLevelSP(sp_lu),
      [self.detect.canLevelDice(level_lu[i]) for i in range(self.variable.getPartyDiceSize())],
      countTotal
    )

    print(f'Summon: {summon_lu:3.1f} --- {self.detect.canSummon(summon_lu)}')
    print(f'SP: {sp_lu:3.1f} --- {self.detect.canLevelSP(sp_lu)}')
    for i in range(self.variable.getPartyDiceSize()):
      print(f'Level_{i+1}: {level_lu[i]:3.1f} --- {self.detect.canLevelDice(level_lu[i])}')

    sys.stdout.flush()
    print("\n================")