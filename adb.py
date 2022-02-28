import subprocess

class ADB:
  @staticmethod
  def sh(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = p.stdout.read()
    return result

  @staticmethod
  def connect(port:int):
    ADB.sh(f'adb tcpip {port}')
    ADB.sh(f'adb connect 127.0.0.1:{port}')

  @staticmethod
  def disconnect():
    ADB.sh('adb disconnect')
    ADB.sh('adb kill-server')