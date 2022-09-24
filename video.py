import cv2

from utils import *

class Video:
  
  @staticmethod
  def createVideo(images, image_size, fps):
    video_name = f"video_{getTimeStamp()}.mp4"
    width, height = image_size
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

    video = cv2.VideoWriter(video_name, fourcc, fps, (width,height))

    for image in images:
      video.write(image)

    video.release()