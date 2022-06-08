import requests
import cv2
import datetime
import traceback

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

    try:
      if image is not None:
        is_success, im_buf_arr = cv2.imencode(".png", image)
        if not is_success:
          raise Exception('Notify: convert image to bytes error')
        imageFile = {'imageFile' : im_buf_arr.tobytes()}
        response = requests.post(url, headers=headers, data=data, files=imageFile)
      else:
        response = requests.post(url, headers=headers, data=data)

      remain = {
        'API': -1 if not 'X-RateLimit-Remaining' in response.headers else int(response.headers['X-RateLimit-Remaining']),
        'Image': -1 if not 'X-RateLimit-ImageRemaining' in response.headers else int(response.headers['X-RateLimit-ImageRemaining']),
        'Reset': -1 if not 'X-RateLimit-Reset' in response.headers else datetime.datetime.utcfromtimestamp(int(response.headers['X-RateLimit-Reset'])) + datetime.timedelta(hours=8)
      }
    except:
      return False, traceback.format_exc(), None

    return response.status_code == 200, response.text, remain