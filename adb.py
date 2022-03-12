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
    s = ADB.sh(f'adb connect {ip}:{port}').decode('utf-8')
    return (s, 'connected' in s)

  @staticmethod
  def disconnect():
    ADB.sh('adb disconnect')
    ADB.sh('adb kill-server')

  @staticmethod
  def detectDiceWar(ip:str, port:int):
    r = ADB.sh(f'adb -s {ip}:{port} shell "dumpsys window windows | grep -E \'mCurrentFocus|mFocusedApp\'"').decode('utf-8')
    return 'com.percent.aos.randomdicewars' in r