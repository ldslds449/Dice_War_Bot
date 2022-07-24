import re
import requests
from packaging import version

Program_Version = '1.9.0'

class Version:

  updateMDurl = 'https://raw.githubusercontent.com/ldslds449/Dice_War_Bot/master/update.md'

  @staticmethod
  def checkLatest():
    r = requests.get(Version.updateMDurl)
    versions = re.findall('## Version (\d+.\d+.\d+)', r.text)
    versions = sorted(versions, key=lambda x : version.parse(x), reverse=True)
    latest_version = versions[0]
    if version.parse(Program_Version) < version.parse(latest_version):
      return (False, latest_version)
    else:
      return (True, latest_version)

  