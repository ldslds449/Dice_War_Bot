import sys
import win32gui
import win32con
import time
import dhash
from typing import Callable
from tkinter import Variable

from screen import *
from control import *
from detect import *
from variable import *
from mode import *
from action import *

class Task:
  def __init__(self):
    self.board_dice = []
    self.detect_board_dice_img = []
    self.detect_board_dice_star = []
    self.board_dice_lu = []
    self.windowID = None

    self.variable = Variable()
    self.variable.loadFromConfigFile()

    # present state
    self.status = Status.LOBBY

    self.detect = Detect("./image/dice", self.variable)

    # same screenshot counter
    self.same_screenshot_cnt = 0
    # previous screenshot hash value
    self.prev_screenshot_hash = None

  def init(self):
    if self.variable.getADBMode() == ADBMode.IP:
      adb_device_code = f"{self.variable.getADBIP()}:{self.variable.getADBPort()}"
    elif self.variable.getADBMode() == ADBMode.ID:
      adb_device_code = self.variable.getADBID()
    self.screen = Screen(self.variable.getControlMode(), _hwnd=self.windowID, 
      _adb_device_code = adb_device_code)
    self.diceControl = DiceControl(self.variable.getControlMode(), _hwnd=self.windowID, 
      _adb_device_code = adb_device_code)
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
      function(i)

  def findMergeDice(self, srcidx, exceptDice):
    if self.variable.getControlMode() == ControlMode.WIN32API:
      self.diceControl.dragPressDice(srcidx)
      time.sleep(0.2)
      _, canMergeImage = self.screen.getScreenShot(self.variable.getZoomRatio())
      time.sleep(0.2)
      canMergeImage = self.detect.Image2OpenCV(canMergeImage)
      self.diceControl.dragUpDice()

      merge_dice_location = []
      def detectMerge(i):
        img = self.detect.getDiceImage(canMergeImage, i, self.variable.getExtractDiceLuSizeWH())
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

    elif self.variable.getControlMode() == ControlMode.ADB:
      srcidx -= 1
      dice_src_name = self.board_dice[srcidx]
      dice_src_star = self.board_dice_star[srcidx]
      if dice_src_name == 'Mimic' or dice_src_name == 'Joker' or dice_src_name == 'Supplement':
        acceptDice = self.variable.getDiceParty() 
      else:
        acceptDice = [dice_src_name, 'Mimic'] 
      merge_dice_location = []
      for i, dice in enumerate(self.board_dice):
        if i != srcidx and dice in acceptDice:
          if exceptDice is None or self.board_dice[i] not in exceptDice:
            if dice_src_star == self.board_dice_star[i]:
              merge_dice_location.append(i)
    
    return merge_dice_location
      
  def task(self, log: Callable, autoPlay: bool, watchAD: bool, battleMode: BattleMode):
    
    _, im = self.screen.getScreenShot(self.variable.getZoomRatio())
    im = self.detect.Image2OpenCV(im)

    # use for detecting joker star
    _, im2 = self.screen.getScreenShot(self.variable.getZoomRatio())
    im2 = self.detect.Image2OpenCV(im2)

    # calculate hash value of screenshot
    im_hash = dhash.dhash_int(im, size=16)
    if self.prev_screenshot_hash == im_hash:
      self.same_screenshot_cnt += 1
    else:
      self.same_screenshot_cnt = 0
      self.prev_screenshot_hash = im_hash

    self.board_dice = []
    self.detect_board_dice_img = []
    self.board_dice_star = []
    self.board_dice_lu = []
    def detectDice(i):
      img = self.detect.getDiceImage(im, i)
      img2 = self.detect.getDiceImage(im2, i)

      # generate dice detect list
      dice_detect_list = self.variable.getDiceParty() + ['Blank']
      if 'Solor' in dice_detect_list and 'SolorX' not in dice_detect_list:
        dice_detect_list += ['SolorX']
      if 'SolorX' in dice_detect_list and 'Solor' not in dice_detect_list:
        dice_detect_list += ['Solor']

      res = self.detect.detectDice(img.copy(), self.variable.getDiceParty() + ['Blank'], self.variable.getDetectDiceMode())
      res_star = self.detect.detectStar(img.copy())
      res2_star = self.detect.detectStar(img2.copy())

      # select the max value of star
      if res_star == 7 or res2_star == 7:
        dice_star = res2_star if res_star == 7 else res_star
      else:
        dice_star = max(res_star, res2_star)

      dice_lu = self.detect.getAverageLuminance(
        self.detect.getDiceImage(im, i, self.variable.getExtractDiceLuSizeWH()))

      self.detect_board_dice_img.append(img)
      self.board_dice_star.append(dice_star)
      self.board_dice.append(res[0])
      self.board_dice_lu.append(dice_lu)

      if i != 0 and i % self.variable.getCol() == 0 :
        print("")
      print(f"{res[0]:10}({res_star}/{res2_star})", end="")
      if i+1 == self.variable.getBoardSize():
        print("")

    self.forAllDiceOnBoard(detectDice)

    # detect status
    status_result = self.detect.detectStatus(im)
    inLobby = status_result['Lobby']
    inWaiting = status_result['Wait']
    inFinish = status_result['Finish']
    inGame = status_result['Game']
    inTrophy = status_result['Trophy']
    hasAD = status_result['AD']
    result = status_result['Result']
    self.result = None

    def detectLobbyAgain():
      _, img = self.screen.getScreenShot(self.variable.getZoomRatio())
      img = self.detect.Image2OpenCV(img)
      return self.detect.detectStatus(im)['Lobby']

    if inGame:
      self.status = Status.GAME
    else:
      if self.status == Status.WAIT:
        if inLobby:
          self.status = Status.LOBBY
      elif self.status == Status.GAME:
        if inLobby:
          self.status = Status.LOBBY
        else:
          self.status = Status.FINISH_ANIMATION
      elif self.status == Status.FINISH:
        if inLobby:
          self.status = Status.LOBBY
        elif inTrophy:
          self.status = Status.TROPHY
        elif inFinish:
          if watchAD and hasAD:
            log('=== Detect AD ===\n')
            # deal with AD
            time.sleep(5)
            self.diceControl.watchAD()
            time.sleep(30)
            if detectLobbyAgain(): return # check if in lobby
            time.sleep(30)
            if detectLobbyAgain(): return # check if in lobby
            self.diceControl.back()
            time.sleep(2)
            if detectLobbyAgain(): return # check if in lobby
            self.diceControl.closeAD()
            time.sleep(10)
            if detectLobbyAgain(): return # check if in lobby
            self.diceControl.closeAD()
            time.sleep(5)
          else:
            self.result = result
            self.diceControl.skip() # leave this stage
            time.sleep(0.5)
            self.diceControl.skip() # click again
            time.sleep(5)
      elif self.status == Status.LOBBY:
        MyAction.init()
        if inWaiting:
          self.status = Status.WAIT
        elif inLobby:
          if autoPlay:
            self.diceControl.battle(battleMode) # start battle
      elif self.status == Status.TROPHY:
        if inLobby:
          self.status = Status.LOBBY
        elif inTrophy:
          self.diceControl.skip()
      elif self.status == Status.FINISH_ANIMATION:
        if inFinish:
          self.status = Status.FINISH
          time.sleep(5)
        elif inLobby:
          self.status = Status.LOBBY

    if self.status != Status.GAME:
      return

    enable_result = self.detect.detectEnable(im)
    canSummon = enable_result['Summon']
    canSP = enable_result['Sp']
    canSpell = enable_result['Spell']
    canLevel = enable_result['Level']

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

    sys.stdout.flush()
    print("\n================")

    MyAction.action(
      diceControl=self.diceControl, 
      findMergeDice=self.findMergeDice,
      count=count, 
      count_sorted=count_sorted, 
      location=location, 
      boardDice=self.board_dice, 
      canSummon=canSummon, 
      canLevelSp=canSP,
      canLevelDice=canLevel,
      canSpell=canSpell,
      countTotal=countTotal, 
      boardDiceStar=self.board_dice_star,
      team=self.variable.getDiceParty().copy()
    )


    