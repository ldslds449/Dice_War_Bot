import enum
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

    if count[mergeDice] <= 1: return (False, 0)
    rdidx = rd.randrange(count[mergeDice])
    srcidx_ = location[mergeDice][rdidx]
    src_star = MyAction.get_star(srcidx_, boardDiceStar)
    
    if not MyAction.isMerge(src_star, mergeDice): return (False, 0)
    srcidx = srcidx_ + 1

    merge_dice_location = findMergeDice(srcidx, exceptDice)

    if len(merge_dice_location) > 0:
      dstidx = merge_dice_location[rd.randrange(0, len(merge_dice_location))] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(np.random.uniform(0.2,0.6,1)) # random delay
        return (True, src_star)
    return (False, 0)
  
  @staticmethod
  def strictOrderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, boardDiceStar, mergeDice, mergeList, dice_level, exceptDice, order):
    if mergeDice is not None: 
      if count[mergeDice] <= 0: return False
      # random select a target dice
      rdidx = rd.randrange(count[mergeDice])
      srcidx_ = location[mergeDice][rdidx]
      src_star = MyAction.get_star(srcidx_, boardDiceStar)
      srcidx = srcidx_ + 1
    else:
      if len(mergeList) == 0: return False
      # random select a target dice in list
      rdidx = rd.randrange(len(mergeList))
      srcidx_ = mergeList[rdidx]
      src_star = MyAction.get_star(srcidx_, boardDiceStar)
      srcidx = srcidx_ + 1
    
    # check star of the dice
    if src_star != 7:
      if src_star > dice_level and 'Growth' in order:
        if 'Joker' in order:
          order.insert(order.index('Joker'), order.pop(order.index('Growth')))
        else:
          order.append(order.pop(order.index('Growth')))
    else: # do not copy any growth when joker star is 7
      if 'Growth' in order:
        order.remove('Growth')
        exceptDice.append('Growth')

    # find all dices that the dice can merge
    merge_dice_location = findMergeDice(srcidx, exceptDice)
    rd.shuffle(merge_dice_location) # shuffle
    
    # select one dice in order to merge
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(np.random.uniform(0.2,0.6,1)) # random delay
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
        time.sleep(np.random.uniform(0.2,0.6,1)) # random delay
        return True
    return False

  @staticmethod
  def orderMerge(diceControl: DiceControl, findMergeDice: Callable,
    count, location, boardDice, mergeDice, exceptDice, order):
    if count[mergeDice] <= 0: return
    # random select a target dice
    rdidx = rd.randrange(count[mergeDice])
    srcidx = location[mergeDice][rdidx] + 1

    # find all dices that the dice can merge
    merge_dice_location = findMergeDice(srcidx, exceptDice)
    rd.shuffle(merge_dice_location) # shuffle
    
    # select one dice in order to merge
    if len(merge_dice_location) > 0:
      merge_dice_location = sorted(merge_dice_location, key= lambda x: 99999 if boardDice[x] not in order else order.index(boardDice[x]))
      dstidx = merge_dice_location[0] + 1
      if srcidx != dstidx:
        diceControl.mergeDice(srcidx, dstidx)
        time.sleep(np.random.uniform(0.2,0.6,1)) # random delay
        return True
    return False

  @staticmethod
  def greedyMerge(diceControl: DiceControl, location, boardDiceStar, jokerCopy, mergeDice, starLimit):
    # count star
    merge_dice_star_count = []
    merge_dice_location_classify_by_star_and_joker_copy = []
    for dice in mergeDice:
      star_count = [0 for _ in range(8)]
      location_classify_by_star_and_joker_copy = [[[],[]] for _ in range(8)]
      for loc in location[dice]:
        star = boardDiceStar[loc]
        star_count[star] += 1
        isJokerCopy = jokerCopy[loc]
        location_classify_by_star_and_joker_copy[star][int(isJokerCopy)].append(loc)
      merge_dice_star_count.append(star_count)
      merge_dice_location_classify_by_star_and_joker_copy.append(location_classify_by_star_and_joker_copy)

    # print
    for i in range(len(mergeDice)):
      print(f"{mergeDice[i].ljust(12)}: ", end="")
      for k in range(1, 7+1):
        print(f"{merge_dice_star_count[i][k]} ", end="")
      print("")

    # find the dice which can be merged and has the smallest star count
    for star in range(1, 7+1):
      canMergeDiceIndex = []
      selectProb = []
      selectProbAll = 0
      for i in range(len(mergeDice)):
        if merge_dice_star_count[i][star] >= 2:
          canMergeDiceIndex.append(i)
          selectProb.append(2**i)
          selectProbAll += 2**i
      if len(canMergeDiceIndex) > 0:
        # check star limit
        if starLimit < star:
          return (False, "", 0)
        # random select one dice
        idx = np.random.choice(canMergeDiceIndex, p=[p/selectProbAll for p in selectProb])
        dice = mergeDice[idx]
        # select joker copy dice first
        joker_copy_size = len(merge_dice_location_classify_by_star_and_joker_copy[idx][star][int(True)])
        loc_joker_copy = np.random.choice(merge_dice_location_classify_by_star_and_joker_copy[idx][star][int(True)], min(2, joker_copy_size), replace=False)
        loc_no_joker_copy = np.random.choice(merge_dice_location_classify_by_star_and_joker_copy[idx][star][int(False)], max(0, 2-len(loc_joker_copy)), replace=False)
        loc = np.concatenate((loc_joker_copy, loc_no_joker_copy), axis=0)
        # merge
        diceControl.mergeDice(int(loc[0])+1, int(loc[1])+1)
        time.sleep(np.random.uniform(0.2,0.6,1)) # random delay

        return (True, dice, star)
    return (False, "", 0)    

  
  @staticmethod
  def init():
    MyAction.hasSummonDiceTimes = 0
    MyAction.midLateGame = False

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
    jokerCopy = kwargs['jokerCopy']

    countBlank = count['Blank']
    # game beginning
    if countBlank == 15:
      # summon dice four times
      diceControl.summonDice()
      time.sleep(0.2)
      diceControl.summonDice()
      time.sleep(0.2)
      diceControl.summonDice()
      time.sleep(0.2)
      diceControl.summonDice()
      MyAction.hasSummonDiceTimes += 4
      return

    # spell
    if canSpell and (passCheckPointStart and not passCheckPointEnd):
      diceControl.castSpell()
    
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    midLateGameParam = 15
    hasJoker = 'Joker' in team

    if MyAction.hasSummonDiceTimes > midLateGameParam:
      MyAction.midLateGame = True
    
    def findStarCount(dice:str, star: int):
      star_Loc = []
      dice_Loc = location[dice] 
      for loc in dice_Loc:
        if boardDiceStar[loc] == star:
          star_Loc.append(loc)
      return star_Loc

    def getNoMinionLimit(wave:int):
      if wave < 10:
        return 4
      elif wave < 20:
        return 3
      elif wave < 25:
        return 2
      elif wave < 29:
        return 1
      elif wave <= 30:
        return 0
      else: # some error happen
        return 3

    def getMergeLimit(wave:int):
      if wave < 20:
        return 4
      else:
        return 5

    def allowMerge(wave:int, count:dict, boardDice:list, boardDiceStar:list):
      valid_joker_count = count['Joker'] if 'Joker' in count else 0
      valid_growth_count = count['Growth'] if 'Growth' in count else 0

      if 'Joker' in count:
        # count
        count_non_joker = [0,0,0,0,0,0,0,0]
        count_joker = [0,0,0,0,0,0,0,0]
        for dice,star in zip(boardDice, boardDiceStar):
          if dice != 'Blank':
            if dice == 'Joker':
              count_joker[star] += 1
            else:
              count_non_joker[star] += 1

        # find valid joker
        for dice,star in zip(boardDice, boardDiceStar):
          if dice == 'Joker':
            if count_non_joker[star] == 0 and count_joker[star] < 2:
              valid_joker_count -= 1

      return (valid_growth_count + valid_joker_count) < getNoMinionLimit(wave)

    
    if hasJoker:
      # joker copy
      if 'Growth' in count and count['Growth'] > 3:
        other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = other + ['Joker']
        excepted = ['Growth']
      else:
        other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = ['Growth'] + other + ['Joker']
        excepted = []

      dice_count_by_star = [0,0,0,0,0,0,0,0]
      jokerMergeList = []
      for dice,star in zip(boardDice, boardDiceStar):
        if dice != 'Blank':
          dice_count_by_star[star] += 1
      for i,(dice,star) in enumerate(zip(boardDice, boardDiceStar)):
        if dice == 'Joker':
          if dice_count_by_star[star] > 1:
            jokerMergeList.append(i)

      hasJokerCopy = MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice, boardDiceStar, None, jokerMergeList, 4, excepted, order)

      # if joker has copied
      if hasJokerCopy:
        if canSummon:
          diceControl.summonDice()
          MyAction.hasSummonDiceTimes += 1
        return # detect dices again

    # summon a dice
    if canSummon:
      diceControl.summonDice()
      MyAction.hasSummonDiceTimes += 1

    # merge other dice
    if countBlank == 0 and allowMerge(wave, count, boardDice, boardDiceStar):
      other = [dice for dice in team if dice not in ['Growth', 'Joker']]
      MyAction.greedyMerge(diceControl, location, boardDiceStar, jokerCopy, other, getMergeLimit(wave))
      diceControl.summonDice()
      MyAction.hasSummonDiceTimes += 1

    # merge growth
    if countBlank == 0 and 'Growth' in count and count['Growth'] > 1 and wave > 25:
      MyAction.greedyMerge(diceControl, location, boardDiceStar, jokerCopy, ['Growth'], 3)
      diceControl.summonDice()
      MyAction.hasSummonDiceTimes += 1
          
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