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

<<<<<<< HEAD
=======
    countBlank = count['Blank']
    # team = ['Slime', 'Charm', 'Flash', 'Slingshot']
    # team = ['Fire', 'Wind', 'Flash', 'Summoner']
    if 'Growth' in team:
      team.remove('Growth')
    if canSpell:
      diceControl.castSpell()
>>>>>>> 6921276bd4d0c50885fabbb5408627b9d4f9cf1e
    # flag
    muchPopGun = count['PopGun'] >= 5
    # muchGun = count['Gun'] >= 5
    # hasMimic = count['Mimic'] > 0
    hasFire = count['Fire'] > 0
    noBlank = count['Blank'] == 0
    hasSupplement = count['Supplement'] > 0

    countFire = count['Fire']
    # countHealing = count['Healing']
    countIce = count['Ice']
    # countElectric = count['Electric']
    # countSummoner = count['Summoner']
    # countSlingshot = count['Slingshot']
    # countGun = count['Gun']
    countBlank = count['Blank']
    countTotal = sum([v for k, v in count.items() if k != 'Blank'])
    earlyGame = countTotal <= 12
    
    team = ['Ice','Fire','Growth','PopGun','Supplement']
    # team = ['Ice','Fire','Growth','Gun','Supplement']
    
    def findStarCount(dice:str, star: int):
      star_Loc = []
      dice_Loc = location[dice] 
      for loc in dice_Loc:
            if boardDiceStar[loc] == star:
              star_Loc.append(loc)
      return star_Loc
    # if not hasSolar and hasMimic and not earlyGame:
    #   MyAction.orderMerge(diceControl, findMergeDice,
    #     count, location, boardDice, 'Mimic', (None if countSolar > 4 else ['Solar_X', 'Solar_O']),
    #     ['Rock', 'Mimic']) 
    # if not hasSolar and hasStone and countRock >= 2 and not earlyGame:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, 'Rock', ['Mimic'])
    # if not hasSolar and countSolar == 6 and not earlyGame:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, 'Solar_X', ['Mimic'])
    # if not hasSolar and noBlank:
    #   MyAction.randomMerge(diceControl, findMergeDice,
    #     count, location, count_sorted[0][0], ['Mimic'])
    
    if not MyAction.hasSummonFirstDice:
      if canSummon:
        diceControl.summonDice()
        MyAction.hasSummonDiceTimes += 1
        MyAction.hasSummonFirstDice = True
    elif not MyAction.hasLevelUpFirstSp :
      if canLevelSp:
        diceControl.levelUpSP()
        MyAction.hasLevelUpFirstSp = True    
    else:
      for name in team:
        if countBlank > 2:
          break
        if count[name] > 0:
          MyAction.probabilisticMerge(diceControl, findMergeDice, count, location, boardDiceStar, name, ['Growth'])

      if canLevelSp:
        diceControl.levelUpSP()
      if canLevelDice[3] and muchPopGun:
        diceControl.levelUpDice(4)
      if canSpell:
        diceControl.castSpell()
        time.sleep(1.2)
      if canSummon:
        diceControl.summonDice()
      else:
        # if hasMimic and not earlyGame:
        #   MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Mimic', ['Pop_Gun'])

        if hasSupplement:
          MyAction.orderMerge(diceControl, findMergeDice,count, location, boardDice, 'Supplement', team[0:3], team[3:5])
        if hasFire and countFire >= 2 and noBlank:
          MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Fire', ['Mimic'])
        if countIce >= 2 and noBlank:
          MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Ice', ['Mimic'])

        # if countGun >= 2 and noBlank:
        #   star_1_Gun_Loc = findStarCount("Gun", 1)
        #   if len(star_1_Gun_Loc) >= 2:
        #     diceControl.mergeDice(star_1_Gun_Loc[0] + 1, star_1_Gun_Loc[1] + 1)
        #   star_2_Gun_Loc = findStarCount("Gun", 2)
        #   if len(star_2_Gun_Loc) >= 2:
        #     diceControl.mergeDice(star_2_Gun_Loc[0] + 1, star_2_Gun_Loc[1] + 1)

        # if countHealing >= 2 and noBlank:
        #   MyAction.randomMerge(diceControl, findMergeDice, count, location, 'Healing', ['Mimic'])
        if countBlank == 0:        
          #------------------------------------------------------PopGun 
          star_1_PopGun_Loc = findStarCount("PopGun", 1)
          star_2_PopGun_Loc = findStarCount("PopGun", 2)
          if len(star_1_PopGun_Loc) >= 2:
            diceControl.mergeDice(star_1_PopGun_Loc[0] + 1, star_1_PopGun_Loc[1] + 1)
          elif len(star_2_PopGun_Loc) >= 2:
            diceControl.mergeDice(star_2_PopGun_Loc[0] + 1, star_2_PopGun_Loc[1] + 1)
          #------------------------------------------------------Gun
          # star_1_Gun_Loc = findStarCount("Gun", 1)
          # star_2_Gun_Loc = findStarCount("Gun", 2)
          # if len(star_1_Gun_Loc) >= 2:
          #   diceControl.mergeDice(star_1_Gun_Loc[0] + 1, star_1_Gun_Loc[1] + 1)
          # elif len(star_2_Gun_Loc) >= 2:
          #   diceControl.mergeDice(star_2_Gun_Loc[0] + 1, star_2_Gun_Loc[1] + 1)
    
    time.sleep(0.8)
