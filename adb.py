import subprocess

class ADB:
  @staticmethod
  def sh(command):
    print(command)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = p.stdout.read()
    return result

  @staticmethod
  def connect(ip:str, port:int):
    print(ADB.sh(f'adb tcpip {port}'))
    print(ADB.sh(f'adb connect {ip}:{port}'))

  @staticmethod
  def disconnect():
    print(ADB.sh('adb disconnect'))
    print(ADB.sh('adb kill-server'))