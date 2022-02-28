import sys
from tkinter import Variable
import win32gui
import win32con
import random as rd

from screen import *
from control import *
from detect import *
from ui import *
from variable import *

class Task:
  def __init__(self):
    self.getWindowID()
    self.detect = Detect("./image")

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    self.merge_dice = []
    self.merge_dice_location = []

    self.targetDice = ["Healing", "Solar_O", "Rock", "Flash", "Mimic", "Blank", "Solar_X"]

    self.variable = Variable()
    self.variable.setBoardDiceLeftTopXY((90, 477))
    self.variable.setBoardDiceOffsetXY((49, 49))
    self.variable.setLevelDiceLeftXY((70, 640))
    self.variable.setLevelDiceOffsetX(60)
    self.variable.setEmojiDialogXY((40, 390))
    self.variable.setEmojiLeftXY((40, 390))
    self.variable.setEmojiOffsetX(60)
    self.variable.setSummonDiceXY((340, 580))
    self.variable.setLevelSpXY((40, 580))
    self.variable.setMergeFloatLocationXY((190, 400))
    self.variable.setExtractDiceSizeWH((50, 50))
    self.variable.setExtractDiceLuSizeWH((40, 40))
    self.variable.setExtractSpLuSizeWH((5, 5))
    self.variable.setExtractSummonLuSizeWH((3, 3))
    self.variable.setExtractLevelDiceLuSizeWH((3, 3))
    self.variable.setZoomRatio(1)
    
    self.diceControl = DiceControl(ControlMode.WIN32API, self.hwndChild)
    self.diceControl.setVariable(self.variable)

  def getWindowID(self):
    self.hwnd = win32gui.FindWindow(None, "BlueStacks")
    self.hwndChild = win32gui.GetWindow(self.hwnd, win32con.GW_CHILD)

  def forAllDiceOnBoard(self, function):
    for i in range(self.variable.getBoardSize()):
      row = i // self.variable.getCol()
      col = i % self.variable.getCol()
      function(i, row, col)

  def findMergeDice(self, count, location, orig_lu, mergeDice, exceptDice):
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1
    self.diceControl.dragPressDice(srcidx)
    time.sleep(0.2)
    _, canMergeImage = getScreenShot(self.hwndChild, self.variable.getZoomRatio())
    time.sleep(0.2)
    canMergeImage = self.detect.Image2OpenCV(canMergeImage)
    self.diceControl.dragUpDice(srcidx)

    x = self.variable.getBoardDiceLeftTopXY()[0]
    y = self.variable.getBoardDiceLeftTopXY()[1]
    offset_x = self.variable.getBoardDiceOffsetXY()[0]
    offset_y = self.variable.getBoardDiceOffsetXY()[1]

    self.merge_dice = []
    self.merge_dice_location = []
    def detectMerge(i, row, col):
      img = self.detect.extractImage(canMergeImage, 
        (x+col*offset_x, y+row*offset_y, 
        self.variable.getExtractDiceLuSizeWH()[0], self.variable.getExtractDiceLuSizeWH()[1]), ExtractMode.CENTER)
      img_lu = self.detect.getAverageLuminance(img)
      lu_offset = orig_lu[i] - img_lu
      canMerge = self.detect.canMergeDice(lu_offset)
      self.merge_dice.append(canMerge)
      if canMerge and self.board_dice[i] != 'Blank':
        if exceptDice is None or self.board_dice[i] not in exceptDice:
          self.merge_dice_location.append(i)
      if i != 0 and i % self.variable.getCol() == 0 :
        print("")
      print(f"{'O' if canMerge else 'X'} {orig_lu[i]:4.1f} / {img_lu:4.1f}  ", end="")
      if i+1 == self.variable.getBoardSize():
        print("")

    self.forAllDiceOnBoard(detectMerge)
    
    if len(self.merge_dice_location) > 0:
      dstidx = self.merge_dice_location[rd.randrange(0, len(self.merge_dice_location))] + 1
      if srcidx != dstidx:
        self.diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
      
  def task(self):

    x = self.variable.getBoardDiceLeftTopXY()[0]
    y = self.variable.getBoardDiceLeftTopXY()[1]
    offset_x = self.variable.getBoardDiceOffsetXY()[0]
    offset_y = self.variable.getBoardDiceOffsetXY()[1]
    
    r, im = getScreenShot(self.hwndChild, self.variable.getZoomRatio())
    im = self.detect.Image2OpenCV(im)

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_lu = []
    def detectDice(i, row, col):
      dice_xy = (x+col*offset_x, y+row*offset_y)
      img = self.detect.extractImage(im, 
        (dice_xy[0], dice_xy[1], 
        self.variable.getExtractDiceSizeWH()[0], self.variable.getExtractDiceSizeWH()[1]), ExtractMode.CENTER)
      res = self.detect.detectDice(img, self.targetDice)

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
      (self.variable.getLevelSpXY()[0], self.variable.getSummonDiceXY()[1],
      self.variable.getExtractSpLuSizeWH()[0], self.variable.getExtractSpLuSizeWH()[1]), ExtractMode.CENTER))
    level_lu = []
    for i in range(self.variable.getPartyDiceSize()):
      level_dice_x = self.variable.getLevelDiceLeftXY()[0] + i*self.variable.getLevelDiceOffsetX()
      level_dice_y = self.variable.getLevelDiceLeftXY()[1]
      level_lu.append(self.detect.getAverageLuminance(self.detect.extractImage(im, 
        (level_dice_x, level_dice_y,
        self.variable.getExtractLevelDiceLuSizeWH()[0], self.variable.getExtractLevelDiceLuSizeWH()[1]), ExtractMode.CENTER)))

    count = {}
    for dice in self.targetDice:
      count[dice] = 0
    for dice in self.board_dice:
      count[dice] += 1
    location = {}
    for type in count:
      location[type] = []
    for idx, dice in enumerate(self.board_dice):
      location[dice].append(idx)
    count_sorted = sorted(count.items(), key=lambda x : x[1], reverse=True)

    # flag
    hasSolar = count['Solar_O'] >= 4
    hasMimic = count['Mimic'] > 0
    hasStone = count['Rock'] > 0
    noBlank = count['Blank'] == 0

    countRock = count['Rock']
    countSolar = count['Solar_O'] + count['Solar_X']
    countBlank = count['Blank']
    countTotal = sum([x[1] for x in count.items() if x[0] != 'Blank'])

    earlyGame = countTotal <= 10

    if not hasSolar and hasMimic and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Mimic', (None if countSolar > 4 else ['Solar_X', 'Solar_O']))
    if not hasSolar and hasStone and countRock >= 2 and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Rock', ['Mimic'])
    if not hasSolar and countSolar == 6 and not earlyGame:
      self.findMergeDice(count, location, self.board_dice_lu, 'Solar_X', ['Mimic'])
    if not hasSolar and noBlank:
      self.findMergeDice(count, location, self.board_dice_lu, count_sorted[0][0], ['Mimic'])

    if self.detect.canLevelSP(sp_lu):
      self.diceControl.levelUpSP()
    elif self.detect.canSummon(summon_lu) and (not hasSolar or countBlank >= 3):
      self.diceControl.summonDice()
    elif self.detect.canLevelDice(level_lu[2]):
      self.diceControl.levelUpDice(3)
    elif self.detect.canLevelDice(level_lu[0]):
      self.diceControl.levelUpDice(1)
    elif self.detect.canLevelDice(level_lu[3]):
      self.diceControl.levelUpDice(4)

    print(f'Summon: {summon_lu} --- {self.detect.canSummon(summon_lu)}')
    print(f'SP: {sp_lu} --- {self.detect.canLevelSP(sp_lu)}')
    for i in range(self.variable.getPartyDiceSize()):
      print(f'Level_{i+1}: {level_lu[i]} --- {self.detect.canLevelDice(level_lu[i])}')

    sys.stdout.flush()
    print("\n================")