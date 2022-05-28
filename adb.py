import subprocess

class ADB:
  packageName = 'com.percent.aos.randomdicewars'

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
  def detectDiceWar(adb_device_code:str):
    r = ADB.sh(f'adb -s {adb_device_code} shell "dumpsys activity activities | grep mResumedActivity"').decode('utf-8')
    return (ADB.packageName in r, r)

  @staticmethod
  def restart(adb_device_code:str):
    ADB.sh(f'adb -s {adb_device_code} shell am force-stop {ADB.packageName}')
    ADB.sh(f'adb -s {adb_device_code} shell monkey -p {ADB.packageName} -c android.intent.category.LAUNCHER 1')