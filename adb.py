import subprocess

class ADB:
  @staticmethod
  def sh(command):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, _ = p.communicate()
    return result

  @staticmethod
  def connect(ip:str, port:int):
    ADB.sh(f'adb tcpip {port}')
    return ADB.sh(f'adb connect {ip}:{port}').decode('utf-8')

  @staticmethod
  def disconnect():
    ADB.sh('adb disconnect')
    ADB.sh('adb kill-server')