import cv2
import threading
import json
import requests

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO

from adb import *

class Action(IntEnum):
  PRESS_DOWN = 0
  PRESS_UP = 1
  PRESS_MOVE = 2
  BACK = 3
  HOME = 4

class StreamServer():
  app = Flask(__name__, template_folder="./web", static_folder="./web")
  app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # disable cache

  socketio = SocketIO(app)

  @app.route('/video_feed')
  def video_feed():

    # get the frame and encode the frame
    def gen_frames():
      while True:
        if not hasattr(ADB, "frame"):
          break
        else:
          _, buffer = cv2.imencode('.jpg', ADB.frame)
          frame = buffer.tobytes()
          yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # return encoded frame to web
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

  @socketio.on('action')
  def action(values):
    values = json.loads(values)
    print(values)
    act = values["action"]

    if act == Action.PRESS_DOWN or act == Action.PRESS_UP or act == Action.PRESS_MOVE:
      coord = values["coord"]
      size = values["size"]
      ratio = ADB.getResolution()[1] / size[1]
      ADB.touch((coord[0]*ratio, coord[1]*ratio), int(act)) # 0: down, 1: up, 2: move
    elif act == Action.BACK:
      ADB.back()
    elif act == Action.HOME:
      ADB.home()
    return {}

  @app.route('/shutdown', methods=['POST'])
  def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
      raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

  @app.route('/')
  def index():
    return render_template('index.html')

  def run(self):
    self.app.run(host="0.0.0.0", port="8787", threaded=True)

  def run_in_bg(self):
    def func():
      self.app.run(host="0.0.0.0", port="8787", threaded=True)
      print("Close Stream Server...")
    t = threading.Thread(target=func)
    t.setDaemon(True)
    t.start()

  def stop(self):
    t = threading.Thread(target=lambda: requests.post('http://127.0.0.1:8787/shutdown', data = {}))
    t.setDaemon(True)
    t.start()
    
