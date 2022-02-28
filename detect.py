import enum
import cv2
import glob
import os
import numpy as np
from skimage.metrics import structural_similarity
from typing import Tuple
from enum import Enum
from PIL import Image, ImageTk

class ExtractMode(Enum):
  LEFTTOP = 0
  CENTER = 1

class DetectDiceMode(Enum):
  HIST = 0
  TEMPLATE = 1

class Detect:
  def __init__(self, dice_folder):
    self.dice_image_rgb = []
    self.dice_image_gray = []
    self.dice_image_gray_resize = []
    self.dice_image_hsv = []
    self.dice_image_hsv_resize = []
    self.dice_image_PIL = []
    self.dice_image_tk = []
    self.dice_image_tk_resize = []
    self.dice_name = []
    self.dice_name_idx_dict = {}

    for i, f in enumerate(glob.glob(os.path.join(dice_folder, '*.png'))):
      name = os.path.basename(f).split(".")[0]
      image_rgb = cv2.imread(f)
      image_gray = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
      image_pil = Image.open(f)
      self.dice_image_rgb.append(image_rgb)
      self.dice_image_gray.append(image_gray)
      self.dice_image_gray_resize.append(cv2.resize(self.dice_image_gray[-1], (50, 50)))
      self.dice_image_hsv.append(cv2.cvtColor(image_rgb.copy(), cv2.COLOR_BGR2HSV))
      self.dice_image_hsv_resize.append(cv2.resize(self.dice_image_hsv[-1], (50, 50)))
      self.dice_image_PIL.append(image_pil)
      self.dice_image_tk.append(ImageTk.PhotoImage(image_pil))
      self.dice_image_tk_resize.append(ImageTk.PhotoImage(image_pil.resize((40, 40))))
      self.dice_name.append(name)
      self.dice_name_idx_dict[name] = i

  def detectDice(self, img, candidate = None, mode: DetectDiceMode = DetectDiceMode.HIST):
    if mode == DetectDiceMode.HIST:
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

      dice_template = zip(self.dice_name, self.dice_image_hsv_resize) if candidate is None else []
      if candidate is not None:
        for name, image in zip(self.dice_name, self.dice_image_hsv_resize):
          if name in candidate:
            dice_template.append((name, image))

      # matching
      result = []
      for name, dice in dice_template:
        dice_hist = cv2.calcHist([dice], channels, None, histSize, ranges, accumulate=False)
        # dice_norm = dice.copy()
        # cv2.normalize(img_hsv, dice_norm, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        res = cv2.compareHist(img_hist, dice_hist, cv2.HISTCMP_INTERSECT)
        result.append((name, res))

      result = sorted(result, key=lambda x : x[1], reverse=True)
    
    elif mode == DetectDiceMode.TEMPLATE:
      img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

      dice_template = zip(self.dice_name, self.dice_image_gray_resize) if candidate is None else []
      if candidate is not None:
        for name, image in zip(self.dice_name, self.dice_image_gray_resize):
          if name in candidate:
            dice_template.append((name, image))

      result = []
      for name, dice in dice_template:
        res = cv2.matchTemplate(img_gray, dice, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7, True, False)
        result.append((name, np.sum(loc)))

      result = sorted(result, key=lambda x : x[1], reverse=True)

    return result[0]

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