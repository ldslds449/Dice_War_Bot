import cv2
import os

from utils import *

class Video:
  
  @staticmethod
  def createVideo(images, image_size, fps):
    video_folder = "video"
    # create folder
    if not os.path.exists(video_folder):
      os.makedirs(video_folder)

    video_name = f"video_{getTimeStamp()}.mp4"
    video_path = os.path.join(video_folder, video_name)
    
    width, height = image_size
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(video_name, fourcc, fps, (width,height))

    for image in images:
      video.write(image)

    video.release()