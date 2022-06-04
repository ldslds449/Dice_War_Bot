import requests
import cv2

class Line:

  @staticmethod
  def notify(token, message, image=None):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
      'Authorization': 'Bearer ' + token
    }
    data = {
      'message': message
    }
    if image is not None:
      is_success, im_buf_arr = cv2.imencode(".png", image)
      if not is_success:
        raise Exception('Notify: convert image to bytes error')
      imageFile = {'imageFile' : im_buf_arr.tobytes()}
      response = requests.post(url, headers=headers, data=data, files=imageFile)
    else:
      response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200, response.text