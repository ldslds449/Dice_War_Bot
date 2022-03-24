import enum
import cv2
import glob
import os
import numpy as np
import dhash
from sewar import *
from typing import Tuple
from PIL import Image, ImageTk

from variable import *
from mode import *

class Detect:
  def __init__(self, dice_folder, variable: Variable):
    self.variable = variable

    self.dice_image_rgb = []
    self.dice_image_rgb_resize = []
    self.dice_image_gray = []
    self.dice_image_gray_resize = []
    self.dice_image_hsv = []
    self.dice_image_hsv_resize = []
    self.dice_image_PIL = []
    self.dice_image_PIL_resize = []
    self.dice_image_tk = []
    self.dice_image_tk_resize = []
    self.dice_image_dhash_resize = []
    self.dice_name = []
    self.dice_name_idx_dict = {}

    self.dhash_size = 16
    self.resize_size = (50, 50)

    # dice
    for i, f in enumerate(glob.glob(os.path.join(dice_folder, '*.png'))):
      name = os.path.basename(f).split(".")[0]
      image_rgb = cv2.imread(f)
      image_gray = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
      image_pil = Image.open(f)
      self.dice_image_rgb.append(image_rgb)
      self.dice_image_rgb_resize.append(cv2.resize(image_rgb, self.resize_size))
      self.dice_image_gray.append(image_gray)
      self.dice_image_gray_resize.append(cv2.resize(self.dice_image_gray[-1], variable.getExtractDiceSizeWH()))
      self.dice_image_hsv.append(cv2.cvtColor(image_rgb.copy(), cv2.COLOR_BGR2HSV))
      self.dice_image_hsv_resize.append(cv2.resize(self.dice_image_hsv[-1], variable.getExtractDiceSizeWH()))
      self.dice_image_PIL.append(image_pil)
      self.dice_image_PIL_resize.append(self.dice_image_PIL[-1].resize(self.resize_size))
      self.dice_image_tk.append(self.Image2TK(image_pil))
      self.dice_image_tk_resize.append(self.Image2TK(image_pil.resize(variable.getExtractDiceSizeWH())))
      self.dice_image_dhash_resize.append(dhash.dhash_int(self.dice_image_PIL_resize[-1], size=self.dhash_size))
      self.dice_name.append(name)
      self.dice_name_idx_dict[name] = i

  def detectDice(self, img, candidate = None, mode: DetectDiceMode = DetectDiceMode.COMBINE):

    def getCandidateImage(original_list):
      dice_template = zip(self.dice_name, original_list) if candidate is None else []
      if candidate is not None:
        for name, image in zip(self.dice_name, original_list):
          if name in candidate:
            dice_template.append((name, image))
      return dice_template

    if mode == DetectDiceMode.COMBINE:
      score = {}

    if mode == DetectDiceMode.HIST or mode == DetectDiceMode.HIST_COMBINE or mode == DetectDiceMode.COMBINE:
      h_bins = 100
      s_bins = 120
      histSize = [h_bins, s_bins]
      channels = [0, 1]
      # hue varies from 0 to 179, saturation from 0 to 255
      h_ranges = [0, 360]
      s_ranges = [0, 512]
      ranges = h_ranges + s_ranges # concat lists

      img = cv2.resize(img, self.resize_size)
      img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
      img_hist = cv2.calcHist([img_hsv], channels, None, histSize, ranges, accumulate=False)
      # cv2.normalize(img_hist, img_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

      dice_template = getCandidateImage(self.dice_image_hsv_resize)

      # matching
      result1 = []
      result2 = []
      rank_dict = {}
      for name, dice in dice_template:
        dice_hist = cv2.calcHist([dice], channels, None, histSize, ranges, accumulate=False)
        # cv2.normalize(dice_hist, dice_hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        res1 = cv2.compareHist(img_hist, dice_hist, cv2.HISTCMP_INTERSECT)
        result1.append((name, res1))
        if mode == DetectDiceMode.HIST_COMBINE:
          res2 = cv2.compareHist(img_hist, dice_hist, cv2.HISTCMP_BHATTACHARYYA)
          result2.append((name, res2))
          rank_dict[name] = 0

      if mode == DetectDiceMode.COMBINE:
        for i, (n, r) in enumerate(result):
          score[n] = i + (0 if n not in score else score[n])
      elif mode == DetectDiceMode.HIST_COMBINE:
        # combine Intersection & Bhattacharyya
        result1 = sorted(result1, key=lambda x : x[1], reverse=True)
        result2 = sorted(result2, key=lambda x : x[1])
        for i,(r1,r2) in enumerate(zip(result1, result2)):
          rank_dict[r1[0]] += i
          rank_dict[r2[0]] += i
        result = sorted(rank_dict.items(), key=lambda x : x[1])
      elif mode == DetectDiceMode.HIST:
        result = sorted(result1, key=lambda x : x[1], reverse=True)
    
    if mode == DetectDiceMode.TEMPLATE:
      img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

      dice_template = getCandidateImage(self.dice_image_gray_resize)

      result = []
      for name, dice in dice_template:
        res = cv2.matchTemplate(img_gray, dice, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7, True, False)
        result.append((name, np.sum(loc)))

      result = sorted(result, key=lambda x : x[1], reverse=True)

    if mode == DetectDiceMode.DHASH or mode == DetectDiceMode.COMBINE:
      img = cv2.resize(img, self.resize_size)
      img = self.OpenCV2Image(img)
      img_hash = dhash.dhash_int(img, size=self.dhash_size)

      dice_template = getCandidateImage(self.dice_image_dhash_resize)

      result = []
      for name, dice in dice_template:
        r = dhash.get_num_bits_different(img_hash, dice)
        result.append((name, r))

      result = sorted(result, key=lambda x : x[1])
      if mode == DetectDiceMode.COMBINE:
        for i, (n, r) in enumerate(result):
          score[n] = i + (0 if n not in score else score[n])

    if mode == DetectDiceMode.MSSSIM:
      img = cv2.resize(img, self.resize_size)
      dice_template = getCandidateImage(self.dice_image_rgb_resize)
      
      result = []
      for name, dice in dice_template:
        r = msssim(img, dice)
        result.append((name, r))

      result = sorted(result, key=lambda x : x[1])

    if mode == DetectDiceMode.COMBINE:
      result = sorted(score.items(), key=lambda x : x[1])

    return result[0]

  def detectStar(self, img):
    img_resize = cv2.resize(img, (50, 50))
    img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

    # binary
    _, img_binary = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)
    kernel = np.array([
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]
    ], np.uint8)
    img_erosion = cv2.erode(img_binary, kernel, iterations = 1)
    img_dilation = cv2.dilate(img_erosion, kernel, iterations = 1)
    contours, _ = cv2.findContours(img_dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    star_count_binary = 0
    for cnt in contours:
      area = cv2.contourArea(cnt)
      perimeter = cv2.arcLength(cnt,True)
      _, radius = cv2.minEnclosingCircle(cnt)
      radius = int(radius)
      if abs(perimeter-radius*2*3.14) < 10 and abs(area-50) < 15:
          star_count_binary += 1

    # edge detection
    img_edge = cv2.Canny(image=img_gray, threshold1=350, threshold2=400)
    contours, _ = cv2.findContours(img_edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    star_count_edge = 0
    centers = []
    for cnt in contours:
      area = cv2.contourArea(cnt)
      perimeter = cv2.arcLength(cnt,True)
      (x,y),radius = cv2.minEnclosingCircle(cnt)
      center = (int(x),int(y))
      radius = int(radius)
      if abs(perimeter-radius*2*3.14) < 10 and abs(perimeter - 25) < 10 and abs(area-50) < 15:
        # find if is overlap
        overlap = False
        for c in centers:
          dist = abs(c[0]-center[0])**2 + abs(c[1]-center[1])**2
          if dist <= 30:
            overlap = True
            break
        if not overlap:
          star_count_edge += 1
          centers.append(center)

    max_star_value = max(star_count_binary, star_count_edge)
    return 7 if max_star_value == 0 else max_star_value

  def detectLobby(self, img):
    img = cv2.resize(img, self.resize_size)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.asarray([100, 216, 252])
    hsv_color2 = np.asarray([105, 226, 255])

    mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)
    extract_pixel_count = np.sum(mask)//255
    ratio = extract_pixel_count/self.resize_size[0]/self.resize_size[1]

    print(f'Lobby {ratio}')

    return ratio > 0.55

  def detectWaiting(self, img):
    img = cv2.resize(img, self.resize_size)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.asarray([125, 165, 84])
    hsv_color2 = np.asarray([126, 169, 88])

    mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)
    extract_pixel_count = np.sum(mask)//255
    ratio = extract_pixel_count/self.resize_size[0]/self.resize_size[1]

    print(f'Wait {ratio}')

    return ratio > 0.90

  def detectFinish(self, img):
    img = cv2.resize(img, self.resize_size)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.asarray([125, 161, 69])
    hsv_color2 = np.asarray([129, 193, 101])

    mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)
    extract_pixel_count = np.sum(mask)//255
    ratio = extract_pixel_count/self.resize_size[0]/self.resize_size[1]

    print(f'Finish {ratio}')

    return ratio > 0.90

  def detectGame(self, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h,w = img.shape
    count = 0
    for i in range(h):
      for j in range(w):
        if img[i,j] > 240:
          count += 1
    print(f'Game {count/w/h}')
    return count >= w*h*0.65

  def detectAD(self, img):
    img = cv2.resize(img, self.resize_size)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.asarray([66, 153, 181])
    hsv_color2 = np.asarray([71, 176, 212])

    mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)
    extract_pixel_count = np.sum(mask)//255
    ratio = extract_pixel_count/self.resize_size[0]/self.resize_size[1]

    print(f'AD {ratio}')

    return ratio > 0.35

  def detectTrophy(self, img):
    img = cv2.resize(img, self.resize_size)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_color1 = np.asarray([124, 180, 70])
    hsv_color2 = np.asarray([126, 183, 73])

    mask = cv2.inRange(img_hsv, hsv_color1, hsv_color2)
    extract_pixel_count = np.sum(mask)//255
    ratio = extract_pixel_count/self.resize_size[0]/self.resize_size[1]

    print(f'Trophy {ratio}')

    return ratio > 0.90

  def canSummon(self, luminance: float):
    if luminance >= 180:
      return True
    else:
      return False
  
  def canLevelSP(self, luminance: float):
    if luminance >= 135:
      return True
    else:
      return False

  def canLevelDice(self, luminance: float):
    if luminance >= 130:
      return True
    else:
      return False

  def canMergeDice(self, lu_offset: float):
    if lu_offset <= 20:
      return True
    else:
      return False

  def canSpell(self, luminance: float):
    if luminance >= 110:
      return True
    else:
      return False

  # x, y, w, h
  def extractImage(self, img, region: Tuple[int, int, int, int], mode):
    if mode == ExtractMode.LEFTTOP:
      return img[
        region[1]:region[1]+region[3], 
        region[0]:region[0]+region[2],:]
    elif mode == ExtractMode.CENTER:
      return img[
        region[1]-(region[3]//2):region[1]-(region[3]//2)+region[3], 
        region[0]-(region[2]//2):region[0]-(region[2]//2)+region[2],:]

  def extractColor(self, img, pixel: Tuple[int, int]):
    return img[pixel[1],pixel[0],:]

  def getAverageLuminance(self, img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return np.average(img_hsv[:,:,2])

  def Image2OpenCV(self, img):
    return cv2.cvtColor(np.asarray(img).astype(np.uint8), cv2.COLOR_RGB2BGR)

  def OpenCV2Image(self, img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

  def Image2TK(self, img):
    return ImageTk.PhotoImage(img)

  def OpenCV2TK(self, img):
    return ImageTk.PhotoImage(self.OpenCV2Image(img))

  def resize(self, img, size):
    return cv2.resize(img, size)

  def save(self, img, fname):
    cv2.imwrite(fname, img)

  def getDiceImage(self, img, idx, WH = None):
    x = self.variable.getBoardDiceLeftTopXY()[0]
    y = self.variable.getBoardDiceLeftTopXY()[1]
    offset_x = self.variable.getBoardDiceOffsetXY()[0]
    offset_y = self.variable.getBoardDiceOffsetXY()[1]
    if WH is None:
      w = self.variable.getExtractDiceSizeWH()[0]
      h = self.variable.getExtractDiceSizeWH()[1]
    else:
      w, h = WH

    row = idx // self.variable.getCol()
    col = idx % self.variable.getCol()

    dice_xy = (x+col*offset_x, y+row*offset_y)
    dice_img = self.extractImage(img, (dice_xy[0], dice_xy[1], w, h), ExtractMode.CENTER)
    return dice_img

  def drawTestImage(self, img):
    def tupleAdd(a, b):
      return (a[0]+b[0], a[1]+b[1])

    # color
    red = (0, 0, 255) # red
    green = (0, 255, 0) # green

    # draw board dice
    for i in range(self.variable.getBoardSize()):
      row = i // self.variable.getCol()
      col = i % self.variable.getCol()
      leftCorner = tupleAdd(self.variable.getBoardDiceLeftTopXY(), 
        (self.variable.getBoardDiceOffsetXY()[0]*col, self.variable.getBoardDiceOffsetXY()[1]*row))
      leftCorner = tupleAdd(leftCorner, 
        (-self.variable.getExtractDiceSizeWH()[0]//2, -self.variable.getExtractDiceSizeWH()[1]//2))
      cv2.rectangle(img, leftCorner, 
        tupleAdd(leftCorner, self.variable.getExtractDiceSizeWH()), red, 2)

    # draw level
    for i in range(self.variable.getPartyDiceSize()):
      cv2.circle(img, tupleAdd(self.variable.getLevelDiceLeftXY(), 
        (self.variable.getLevelDiceOffsetX()*i, 0)), 5, red, -1)

    # draw summon
    cv2.circle(img, self.variable.getSummonDiceXY(), 5, red, -1)

    # draw sp
    cv2.circle(img, self.variable.getLevelSpXY(), 5, red, -1)

    # draw emoji
    leftCorner = tupleAdd(self.variable.getEmojiDialogXY(), 
      (-self.variable.getEmojiDialogWH()[0]//2, -self.variable.getEmojiDialogWH()[1]//2))
    cv2.rectangle(img, leftCorner, 
      tupleAdd(leftCorner, self.variable.getEmojiDialogWH()), green, 2)
    for i in range(self.variable.getEmojiSize()):
      cv2.circle(img, tupleAdd(self.variable.getEmojiLeftXY(), 
        (self.variable.getEmojiOffsetX()*i, 0)), 5, red, -1)

    # draw battle
    cv2.circle(img, self.variable.getBattleXY(), 5, green, -1)

    # draw AD close
    cv2.circle(img, self.variable.getADCloseXY(), 5, red, -1)

    # draw spell
    cv2.circle(img, self.variable.getSpellXY(), 5, green, -1)

    return img

  def detectEnable(self, img):
    summon_lu = self.getAverageLuminance(self.extractImage(img, 
      (self.variable.getSummonDiceXY()[0], self.variable.getSummonDiceXY()[1], 
      self.variable.getExtractSummonLuSizeWH()[0], self.variable.getExtractSummonLuSizeWH()[1]), ExtractMode.CENTER))
    sp_lu = self.getAverageLuminance(self.extractImage(img, 
      (self.variable.getLevelSpXY()[0], self.variable.getLevelSpXY()[1],
      self.variable.getExtractSpLuSizeWH()[0], self.variable.getExtractSpLuSizeWH()[1]), ExtractMode.CENTER))
    spell_lu = self.getAverageLuminance(self.extractImage(img, 
      (self.variable.getSpellXY()[0], self.variable.getSpellXY()[1],
      self.variable.getExtractSpellLuSizeWH()[0], self.variable.getExtractSpellLuSizeWH()[1]), ExtractMode.CENTER))
    level_lu = []
    for i in range(self.variable.getPartyDiceSize()):
      level_dice_x = self.variable.getLevelDiceLeftXY()[0] + i*self.variable.getLevelDiceOffsetX()
      level_dice_y = self.variable.getLevelDiceLeftXY()[1]
      level_lu.append(self.getAverageLuminance(self.extractImage(img, 
        (level_dice_x, level_dice_y,
        self.variable.getExtractLevelDiceLuSizeWH()[0], self.variable.getExtractLevelDiceLuSizeWH()[1]), ExtractMode.CENTER)))
    return {
      'Summon': summon_lu, 
      'Sp': sp_lu, 
      'Spell': spell_lu,
      'Level': level_lu
    }

  def detectStatus(self, img):
    inLobby = False
    inWaiting = False
    inFinish = False
    inGame = False
    inTrophy = False
    hasAD = False

    if self.detectLobby(self.getDiceImage(img, 8)):
      inLobby = True
    if self.detectWaiting(self.getDiceImage(img, 2)):
      inWaiting = True
    if self.detectFinish(self.getDiceImage(img, 4)) or \
      self.detectFinish(self.getDiceImage(img, 14)):
      inFinish = True
    if self.detectGame(self.extractImage(img, 
      (self.variable.getEmojiDialogXY()[0], self.variable.getEmojiDialogXY()[1],
      self.variable.getEmojiDialogWH()[0], self.variable.getEmojiDialogWH()[1]), ExtractMode.CENTER)):
      inGame = True
    if self.detectAD(self.getDiceImage(img, 12)):
      hasAD = True
    if self.detectTrophy(self.getDiceImage(img, 4)):
      inTrophy = True

    return {
      'Lobby': inLobby, 
      'Wait': inWaiting, 
      'Finish': inFinish,
      'Game': inGame,
      'Trophy': inTrophy,
      'AD': hasAD
    }