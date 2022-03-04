import enum
import cv2
import glob
import os
import numpy as np
import dhash
# from skimage.metrics import structural_similarity
from typing import Tuple
from enum import Enum
from PIL import Image, ImageTk
from variable import *

class ExtractMode(Enum):
  LEFTTOP = 0
  CENTER = 1

class DetectDiceMode(Enum):
  HIST = 0
  TEMPLATE = 1
  DHASH = 2
  COMBINE = 3

class Detect:
  def __init__(self, dice_folder, variable: Variable):
    self.variable = variable

    self.dice_image_rgb = []
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

    for i, f in enumerate(glob.glob(os.path.join(dice_folder, '*.png'))):
      name = os.path.basename(f).split(".")[0]
      image_rgb = cv2.imread(f)
      image_gray = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
      image_pil = Image.open(f)
      self.dice_image_rgb.append(image_rgb)
      self.dice_image_gray.append(image_gray)
      self.dice_image_gray_resize.append(cv2.resize(self.dice_image_gray[-1], variable.getExtractDiceSizeWH()))
      self.dice_image_hsv.append(cv2.cvtColor(image_rgb.copy(), cv2.COLOR_BGR2HSV))
      self.dice_image_hsv_resize.append(cv2.resize(self.dice_image_hsv[-1], variable.getExtractDiceSizeWH()))
      self.dice_image_PIL.append(image_pil)
      self.dice_image_PIL_resize.append(self.dice_image_PIL[-1].resize((50, 50)))
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

    if mode == DetectDiceMode.HIST or mode == DetectDiceMode.COMBINE:
      h_bins = 100
      s_bins = 120
      histSize = [h_bins, s_bins]
      channels = [0, 1]
      # hue varies from 0 to 179, saturation from 0 to 255
      h_ranges = [0, 360]
      s_ranges = [0, 512]
      ranges = h_ranges + s_ranges # concat lists

      img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
      img_hist = cv2.calcHist([img_hsv], channels, None, histSize, ranges, accumulate=False)
      # img_hsv_norm = img_hsv.copy()
      # cv2.normalize(img_hsv, img_hsv_norm, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

      dice_template = getCandidateImage(self.dice_image_hsv_resize)

      # matching
      result = []
      for name, dice in dice_template:
        dice_hist = cv2.calcHist([dice], channels, None, histSize, ranges, accumulate=False)
        # dice_norm = dice.copy()
        # cv2.normalize(img_hsv, dice_norm, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        res = cv2.compareHist(img_hist, dice_hist, cv2.HISTCMP_INTERSECT)
        result.append((name, res))

      result = sorted(result, key=lambda x : x[1], reverse=True)
      if mode == DetectDiceMode.COMBINE:
        for i, (n, r) in enumerate(result):
          score[n] = i + (0 if n not in score else score[n])
    
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

    if mode == DetectDiceMode.COMBINE:
      result = sorted(score.items(), key=lambda x : x[1])

    return result[0]

  def detectStar(self, img):
    img_resize = cv2.resize(img, (50, 50))
    img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)

    # binary
    _, img_binary = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY)
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
    img_edge = cv2.Canny(image=img_gray, threshold1=300, threshold2=400)
    contours, _ = cv2.findContours(img_edge, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    star_count_edge = 0
    centers = []
    for cnt in contours:
      area = cv2.contourArea(cnt)
      perimeter = cv2.arcLength(cnt,True)
      (x,y),radius = cv2.minEnclosingCircle(cnt)
      center = (int(x),int(y))
      radius = int(radius)
      if abs(perimeter-radius*2*3.14) < 10 and abs(area-50) < 15:
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
    return max(star_count_binary, star_count_edge)

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

  def drawTestImage(self, img):
    def tupleAdd(a, b):
      return (a[0]+b[0], a[1]+b[1])

    # color
    color = (0, 0, 255) # red

    # draw board dice
    for i in range(self.variable.getBoardSize()):
      row = i // self.variable.getCol()
      col = i % self.variable.getCol()
      leftCorner = tupleAdd(self.variable.getBoardDiceLeftTopXY(), 
        (self.variable.getBoardDiceOffsetXY()[0]*col, self.variable.getBoardDiceOffsetXY()[1]*row))
      leftCorner = tupleAdd(leftCorner, 
        (-self.variable.getExtractDiceSizeWH()[0]//2, -self.variable.getExtractDiceSizeWH()[1]//2))
      cv2.rectangle(img, leftCorner, 
        tupleAdd(leftCorner, self.variable.getExtractDiceSizeWH()), color, 2)

    # draw level
    for i in range(self.variable.getPartyDiceSize()):
      cv2.circle(img, tupleAdd(self.variable.getLevelDiceLeftXY(), 
        (self.variable.getLevelDiceOffsetX()*i, 0)), 5, color, -1)

    # draw summon
    cv2.circle(img, self.variable.getSummonDiceXY(), 5, color, -1)

    # draw sp
    cv2.circle(img, self.variable.getLevelSpXY(), 5, color, -1)

    # draw emoji
    cv2.circle(img, self.variable.getEmojiDialogXY(), 5, color, -1)
    for i in range(self.variable.getEmojiSize()):
      cv2.circle(img, tupleAdd(self.variable.getEmojiLeftXY(), 
        (self.variable.getEmojiOffsetX()*i, 0)), 5, color, -1)

    return img