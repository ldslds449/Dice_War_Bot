from typing import Callable, Dict, List
import abc
import time
import random as rd

from control import *

class Action:
  @staticmethod
  @abc.abstractmethod
  def action(self,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list, 
    canSummon: bool, canLevelSp: bool, canLevelDice: List, canSpell: bool,
    countTotal: int, boardDiceStar: list):
    return NotImplemented

class MyAction(Action):
  @staticmethod
  def get_star(dice_loc, boardDiceStar):
    star = boardDiceStar[dice_loc]
    return star

  @staticmethod
  def isMerge(star):
    star_prob = star / 10
    merge_prob = rd.uniform(0, 1)

    if star >= 5:
      return False
    elif star >= 3:
      star_prob = star_prob*2 + 0.1
    else:
      star_prob = star_prob
    print('star_prob:', star_prob)
    print('merge_prob:', merge_prob)

    return merge_prob > star_prob

  @staticmethod
  def probabilisticMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDiceStar, mergeDice, exceptDice):

    if count[mergeDice] <= 1: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    print('selected ', mergeDice, 'stars:', str(src_star))
    if not MyAction.isMerge(src_star): return
    srcidx = srcidx_ + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
  
  @staticmethod
  def randomMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, mergeDice, exceptDice):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)

  @staticmethod
  def orderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, mergeDice, exceptDice, order):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)
    
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)

  hasSummonFourDice = False
  hasLevelUpFirstSp = False
  hasLevelUpSecondThirdSp = 0
  hasSummonDiceTimes = 0
  SummonDiceFortyTimes = False
  
  @staticmethod
  def init():
    MyAction.hasSummonFourDice = False
    MyAction.hasLevelUpFirstSp = False
    MyAction.hasLevelUpSecondThirdSp = 0
    MyAction.hasSummonDiceTimes = 0
    MyAction.SummonDiceFortyTimes = False

  @staticmethod
  def action(
    diceControl: DiceControl, findMergeDice: Callable,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list,
    canSummon: bool, canLevelSp: bool, canLevelDice: List, canSpell: bool,
    countTotal: int, boardDiceStar: list, team: list):

    countBlank = count['Blank']
    # team = ['Slime', 'Charm', 'Flash', 'Slingshot']
    # team = ['Fire', 'Wind', 'Flash', 'Summoner']
    if 'Growth' in team:
      team.remove('Growth')
    if canSpell:
      diceControl.castSpell()
    # flag
    Liwa_action = True
    if Liwa_action:
      countTotal = sum([v for k, v in count.items() if k != 'Blank'])
      earlyGame = countTotal <= 12
      
      def findStarCount(dice:str, star: int):
        star_Loc = []
        dice_Loc = location[dice] 
        for loc in dice_Loc:
              if boardDiceStar[loc] == star:
                star_Loc.append(loc)
        return star_Loc
      
      if not MyAction.hasSummonFourDice:
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
          if MyAction.hasSummonDiceTimes >= 4:
            MyAction.hasSummonFourDice = True
      elif not MyAction.hasLevelUpFirstSp:
        if canLevelSp:
          diceControl.levelUpSP()
          MyAction.hasLevelUpFirstSp = True
      else:
        # if canLevelSp:
          # diceControl.levelUpSP()
        if countBlank < 2 and MyAction.SummonDiceFortyTimes:
          for d in count_sorted:
            if d[0] == team[0] and canLevelDice[0]:
              diceControl.levelUpDice(1)
              break
            elif d[0] == team[1] and canLevelDice[1]:
              diceControl.levelUpDice(2)
              break
            elif d[0] == team[2] and canLevelDice[2]:
              diceControl.levelUpDice(3)
              break
            elif d[0] == team[3] and canLevelDice[3]:
              diceControl.levelUpDice(4)
              break
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
        if countBlank == 0 and MyAction.hasLevelUpSecondThirdSp < 2:
          for dice in team:
            star_1_dice_Loc = findStarCount(dice, 1)
            if len(star_1_dice_Loc) >= 3:
              diceControl.mergeDice(star_1_dice_Loc[0] + 1, star_1_dice_Loc[1] + 1)
          if canLevelSp:
            diceControl.levelUpSP()
            MyAction.hasLevelUpSecondThirdSp += 1
        elif MyAction.hasSummonDiceTimes >= 20 and not MyAction.SummonDiceFortyTimes:
          if canLevelSp:
            diceControl.levelUpSP()
            MyAction.SummonDiceFortyTimes = True
        elif countBlank < 2 and MyAction.hasLevelUpSecondThirdSp >= 2:
          for name in team:
            if count[name] > 2:
              MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar, name, ['Growth'])
    else:
      for name in team:
        if countBlank > 2:
          break
        if count[name] > 0:
          MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar, name, ['Growth'])

      if canLevelSp:
        diceControl.levelUpSP()
      elif canSummon:
        diceControl.summonDice()
      else:
        for d in count_sorted:
          if d[0] == team[0]:
            diceControl.levelUpDice(1)
          elif d[0] == team[1]:
            diceControl.levelUpDice(2)
          elif d[0] == team[2]:
            diceControl.levelUpDice(3)
          elif d[0] == team[3]:
            diceControl.levelUpDice(4)