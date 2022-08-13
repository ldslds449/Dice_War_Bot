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
        time.sleep(1)
        return (True, src_star)
    return (False, 0)
  
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
        time.sleep(np.random.uniform(0.5,1,1)) # random delay

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
      time.sleep(0.3)
      diceControl.summonDice()
      time.sleep(0.3)
      diceControl.summonDice()
      time.sleep(0.3)
      diceControl.summonDice()
      MyAction.hasSummonDiceTimes += 4
      return

    # spell
    if canSpell and (passCheckPointStart and not passCheckPointEnd):
      diceControl.castSpell()
    
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    midLateGameParam = 20
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
      else:
        return 1

    def getMergeLimit(wave:int):
      if wave < 20:
        return 4
      else:
        return 5

    def allowMerge(wave:int, count:dict, boardDice:list, boardDiceStar:list):
      valid_joker_count = count['Joker']

      # find max star
      max_star = 0
      for dice,star in zip(boardDice, boardDiceStar):
        if dice != 'Blank':
          max_star = max(max_star, star)

      # find max star joker
      highest_star_joker_count = 0
      highest_star_non_joker_count = 0
      for dice,star in zip(boardDice, boardDiceStar):
        if star == max_star:
          if dice == 'Joker':
            highest_star_joker_count += 1
          elif dice != 'Blank':
            highest_star_non_joker_count += 1

      # check if there is a joker with highest star
      if highest_star_non_joker_count == 0 and highest_star_joker_count == 1:
        valid_joker_count -= 1 # do not count this type of joker

      return (count['Growth'] + valid_joker_count) < getNoMinionLimit(wave)

    
    if hasJoker:
      # joker copy
      if count['Growth'] > 3:
        other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = other + ['Joker']
        excepted = ['Growth']
      else:
        other = [dice for dice in team if dice not in ['Growth', 'Joker']]
        order = ['Growth'] + other + ['Joker']
        excepted = []

      hasJokerCopy = MyAction.strictOrderMerge(diceControl, findMergeDice, count, location, boardDice,
                                                boardDiceStar, 'Joker', 4, excepted, order)

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
      if countBlank == 0 and count['Growth'] > 1 and wave > 25:
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