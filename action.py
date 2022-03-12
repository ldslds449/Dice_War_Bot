from typing import Callable, Dict, List
import abc
import time

from control import *

class Action:
  @staticmethod
  @abc.abstractmethod
  def action(self,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list, 
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int, boardDiceStar: list):
    return NotImplemented

import random as rd

class MyAction(Action):
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

  hasleveledSp = False

  @staticmethod
  def init():
    MyAction.hasleveledSp = False

  @staticmethod
  def action(
    diceControl: DiceControl, findMergeDice: Callable,
    count: Dict[str, int], count_sorted: Dict[str, int], location: Dict[str, List], boardDice: list,
    canSummon: bool, canLevelSp: bool, canLevelDice: List,
    countTotal: int, boardDiceStar: list):

    # flag
    hasSolar = (count['Solar_O'] == 7)
    hasJoker = count['Joker'] > 0
    hasCharm = count['Charm'] > 0
    noBlank = count['Blank'] == 0

    countCharm = count['Charm']
    countSolar = count['Solar_O'] + count['Solar_X']
    countBlank = count['Blank']

    earlyGame = countTotal <= 10

    if hasJoker and not earlyGame:
      MyAction.orderMerge(diceControl, findMergeDice,
        count, location, boardDice, 'Joker', ([] if countSolar > 4 else ['Solar_O', 'Solar_X']) + ['Joker'],
        ['Charm']) 
    if not hasSolar and hasCharm and countCharm >= 2 and not earlyGame:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, 'Charm', ['Joker'])
    if not hasSolar and noBlank:
      MyAction.randomMerge(diceControl, findMergeDice,
        count, location, count_sorted[0][0], ['Joker', 'Solar_X', 'Solar_O'])

    if not MyAction.hasleveledSp:
      if canLevelSp:
        diceControl.levelUpSP()
        MyAction.hasleveledSp = True
    else:
      if canLevelSp:
        diceControl.levelUpSP()
      elif canSummon and (not hasSolar or countBlank > 0):
        diceControl.summonDice()
      elif canLevelDice[2]:
        diceControl.levelUpDice(3)
      elif canLevelDice[0]:
        diceControl.levelUpDice(1)
      elif canLevelDice[3]:
        diceControl.levelUpDice(4)

    time.sleep(0.6)