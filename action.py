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

    return merge_prob > star_prob

  @staticmethod
  def probabilisticMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDiceStar, mergeDice, exceptDice):

    if count[mergeDice] <= 1: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    if not MyAction.isMerge(src_star): return
    srcidx = srcidx_ + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
  
  @staticmethod
  def strictOrderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, boardDiceStar, mergeDice, dice_level, exceptDice, order):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    srcidx = srcidx_ + 1
    
    if src_star > dice_level:
      temp = order
      order = exceptDice
      exceptDice = temp

    merge_dice_location = findMergeDice(srcidx, exceptDice)
    
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
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
  
  @staticmethod
  def init():
    MyAction.hasSummonFourDice = False
    MyAction.hasSummonDiceTimes = 0
    MyAction.SpLevelTimes = 0

  @staticmethod
  def action(**kwargs):

    diceControl = kwargs['diceControl']
    findMergeDice = kwargs['findMergeDice']
    count = kwargs['count']
    count_sorted = kwargs['count_sorted']
    location = kwargs['location']
    boardDice = kwargs['boardDice']
    canSummon = kwargs['canSummon']
    canLevelSp = kwargs['canLevelSp']
    canLevelDice = kwargs['canLevelDice']
    canSpell = kwargs['canSpell']
    countTotal = kwargs['countTotal']
    boardDiceStar = kwargs['boardDiceStar']
    team = kwargs['team']

    countBlank = count['Blank']
    if canSpell:
      diceControl.castSpell()
    
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    lateGame = False
    hasJoker = False
    
    def findStarCount(dice:str, star: int):
      star_Loc = []
      dice_Loc = location[dice] 
      for loc in dice_Loc:
            if boardDiceStar[loc] == star:
              star_Loc.append(loc)
      return star_Loc
    
    if not hasJoker:
      if not MyAction.hasSummonFourDice:
        print('Stage 1')
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
          if MyAction.hasSummonDiceTimes >= 4:
            MyAction.hasSummonFourDice = True
      elif MyAction.SpLevelTimes == 0:
        print('Stage 2')
        if canLevelSp:
          diceControl.levelUpSP()
          MyAction.SpLevelTimes += 1 # Sp level reach lv2
      else:
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
        if countBlank == 0 and MyAction.SpLevelTimes < 3: # 還沒生sp lv4以前只合一星
          print('Stage 3')
          for dice in team:
            if dice == 'Growth':
              continue
            star_1_dice_Loc = findStarCount(dice, 1)
            if len(star_1_dice_Loc) > 1:
              diceControl.mergeDice(star_1_dice_Loc[0] + 1, star_1_dice_Loc[1] + 1)
          if canLevelSp:
            diceControl.levelUpSP()
            MyAction.SpLevelTimes += 1
        elif countBlank < 2 and MyAction.SpLevelTimes >= 3:
          if not lateGame:
            lateGameCounter = 0
            for name in team:
              lateGameCounter += len(findStarCount(name, 5))
              lateGameCounter += len(findStarCount(name, 6))
              lateGameCounter += len(findStarCount(name, 7))
            if lateGameCounter > 2:
              lateGame = True
          if not lateGame:
            print('Stage 4')
          else:
            print('Stage 5')
          for name in team:
            if count[name] > 2:
              MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar, name, ['Growth'])
              
          if lateGame:
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
    elif hasJoker:
      if not MyAction.hasSummonFourDice:
        print('Stage 1')
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
          if MyAction.hasSummonDiceTimes >= 4:
            MyAction.hasSummonFourDice = True
        
      elif MyAction.SpLevelTimes == 0:
        print('Stage 2')
        order = ['Growth']
        excepted = []
        for dice in team:
          if dice not in order:
            excepted.append(dice)
        MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice, boardDiceStar, 'Joker', 4, excepted, order)
        if canLevelSp:
          diceControl.levelUpSP()
          MyAction.SpLevelTimes += 1 # Sp level reach lv2
      else:
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
        order = ['Growth']
        excepted = []
        for dice in team:
          if dice not in order:
            excepted.append(dice)
        MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice, boardDiceStar, 'Joker', 4, excepted, order)
        if countBlank == 0 and MyAction.SpLevelTimes < 3: # 還沒生sp lv4以前只合一星
          print('Stage 3')
          for dice in team:
            if dice == 'Growth':
              # print('Growth pass.')
              continue
            elif dice == 'Joker':
              continue
            star_1_dice_Loc = findStarCount(dice, 1)
            if len(star_1_dice_Loc) > 1:
              diceControl.mergeDice(star_1_dice_Loc[0] + 1, star_1_dice_Loc[1] + 1)
          if canLevelSp:
            diceControl.levelUpSP()
            MyAction.SpLevelTimes += 1
        elif countBlank < 2 and MyAction.SpLevelTimes >= 3:
          if not lateGame:
            lateGameCounter = 0
            for name in team:
              lateGameCounter += len(findStarCount(name, 5))
              lateGameCounter += len(findStarCount(name, 6))
              lateGameCounter += len(findStarCount(name, 7))
            if lateGameCounter > 2:
              lateGame = True
          if not lateGame:
            print('Stage 4')
          else:
            print('Stage 5')
          for name in team:
            if name == 'Growth':
              continue
            if name == 'Joker':
              order = ['Growth', 'Joker']
              excepted = []
              for dice in team:
                if dice not in order:
                  excepted.append(dice)
              MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice, boardDiceStar, name, 4, excepted, order)
              continue
            if count[name] > 2:
              MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar, name, ['Growth', 'Joker'])
              
          if lateGame:
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