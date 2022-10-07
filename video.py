import cv2
import os

from readerwriterlock import rwlock

from utils import *

class Video:

  video = None
  lock = rwlock.RWLockFairD()
  
  @staticmethod
  def createVideo(image_size, fps):
    video_folder = "video"
    # create folder
    if not os.path.exists(video_folder):
      os.makedirs(video_folder)

    video_name = f"video_{getTimeStamp()}.mp4"
    video_path = os.path.join(video_folder, video_name)
    
    width, height = image_size
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    Video.video = cv2.VideoWriter(video_path, fourcc, fps, (width,height))

  @staticmethod
  def addImages(images):
    if Video.video is not None:
      with Video.lock.gen_wlock():
        for image in images:
          Video.video.write(image)

  @staticmethod
  def saveVideo():
    if Video.video is not None:
      with Video.lock.gen_rlock():
        Video.video.release()
        Video.video = None