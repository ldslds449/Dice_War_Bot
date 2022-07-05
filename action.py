from typing import Callable, Dict, List
import abc
import time
import random as rd
import numpy as np

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
  def isMerge(star, dice):
    star_prob = star / 10
    if dice == "Meteor":
      if star >= 4:
        return False
      elif star == 3:
        star_prob = star_prob*3 
      else:
        star_prob = star_prob - 0.1
    else:
      if star >= 5:
        return False
      elif star >= 3:
        star_prob = star_prob*2 - 0.1
      else:
        star_prob = star_prob

    return np.random.choice([True, False], p=[1.0-star_prob, star_prob])

  @staticmethod
  def probabilisticMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDiceStar, mergeDice, exceptDice):

    if count[mergeDice] <= 1: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    
    if not MyAction.isMerge(src_star, mergeDice): return
    srcidx = srcidx_ + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
        return True
    return False
  
  @staticmethod
  def strictOrderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, boardDiceStar, mergeDice, dice_level, exceptDice, order):
    if count[mergeDice] <= 0: return
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    srcidx = srcidx_ + 1
    
    if src_star > dice_level and 'Growth' in order:
      order.remove('Growth')
      exceptDice += ['Growth']

    merge_dice_location = findMergeDice(srcidx, exceptDice)
    
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(1)
        return True
    return False
  
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
        return True
    return False

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
        return True
    return False
  
  @staticmethod
  def init():
    MyAction.hasSummonFourDice = False
    MyAction.hasLevelUpFirstSp = False
    MyAction.hasLevelUpSecondThirdSp = 0
    MyAction.hasSummonDiceTimes = 0
    MyAction.SpLevelTimes = 0
    MyAction.midLateGame = False
    MyAction.lateGame = False

  @staticmethod
  def action(**kwargs):

    diceControl = kwargs['diceControl']
    findMergeDice = kwargs['findMergeDice']
    count = kwargs['count']
    count_sorted = kwargs['count_sorted']
    location = kwargs['location']
    boardDice = kwargs['boardDice']
    canSummon = kwargs['canSummon']
    canLevelDice = kwargs['canLevelDice']
    canSpell = kwargs['canSpell']
    countTotal = kwargs['countTotal']
    boardDiceStar = kwargs['boardDiceStar']
    team = kwargs['team']
    passCheckPointStart, passCheckPointEnd = kwargs['passCheckPoint']
    wave = kwargs['wave']

    countBlank = count['Blank']
    if canSpell and (passCheckPointStart and not passCheckPointEnd):
      diceControl.castSpell()
    
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    midLateGameParam = 25
    hasJoker = 'Joker' in team
    
    def findStarCount(dice:str, star: int):
      star_Loc = []
      dice_Loc = location[dice] 
      for loc in dice_Loc:
            if boardDiceStar[loc] == star:
              star_Loc.append(loc)
      return star_Loc
    
    if hasJoker:
      # joker copy
      if count['Growth'] > 3:
        other = other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = other + ['Joker']
        excepted = ['Growth']
      else:
        other = other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = ['Growth'] + other + ['Joker']
        excepted = []

      hasJokerCopy = MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice,
                                                boardDiceStar, 'Joker', 4, excepted, order)

      # if joker has copied
      if hasJokerCopy:
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
        # detect dices again
        return
      # summon a dice
      if canSummon:
        diceControl.summonDice()
        MyAction.hasSummonDiceTimes += 1
        if MyAction.hasSummonDiceTimes > midLateGameParam:
          MyAction.midLateGame = True

      if countBlank < 3:
        for name in team:
          if name == 'Growth':
            continue
          elif name == 'Joker':
            continue
          elif count[name] > 2:
            MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar,
                                        name, ['Growth', 'Joker'])
          
      if MyAction.midLateGame:
        for d,_ in count_sorted:
          # skip Joker, Growth and Blank 
          if d == 'Joker' or d == 'Growth' or d == 'Blank':
            continue
          # get location of the dice in team list
          level_location = team.index(d)
          # check whether can level up
          if canLevelDice[level_location]:
            diceControl.levelUpDice(level_location+1) # 1: offset
            break