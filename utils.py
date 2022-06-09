import datetime

def getTimeStamp():
  stamp = datetime.datetime.now().timestamp()
  return int(stamp * 1000 * 1000)

