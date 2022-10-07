from PySide6.QtWidgets import QDialog, QTextEdit, QProgressBar, QVBoxLayout, QMessageBox, QPushButton, QHBoxLayout
from PySide6.QtCore import QThread, Signal, Qt
  
import time
import requests
import zipfile
import shutil
import glob
import os
import hashlib
import subprocess

import version as v

class Update(QDialog):

  def __init__(self) -> None:
    super(Update, self).__init__()
    self.setWindowTitle('Updater')
    self.resize(400, 200)
    self.setAttribute(Qt.WA_DeleteOnClose)

    self.text = QTextEdit()
    self.text.setReadOnly(True)

    self.pbar = QProgressBar(self)
    self.pbar.setValue(0)

    self.update_btn = QPushButton("Update")
    self.update_btn.setEnabled(False)
    self.update_btn.clicked.connect(self.runUpdate)

    self.launch_btn = QPushButton("Launch")
    self.launch_btn.setEnabled(False)
    self.launch_btn.clicked.connect(self.accept)

    self.hbox = QHBoxLayout()
    self.hbox.addWidget(self.update_btn)
    self.hbox.addWidget(self.launch_btn)
    
    self.vbox = QVBoxLayout()
    self.vbox.addWidget(self.pbar)
    self.vbox.addWidget(self.text)
    self.vbox.addLayout(self.hbox)

    self.setLayout(self.vbox)

    self.checktask = CheckUpdateTask()
    self.checktask.pbar_set_signal.connect(self.setPbar)
    self.checktask.log_signal.connect(self.log)
    self.checktask.update_btn_signal.connect(self.enableUpdateBtn)
    self.checktask.launch_btn_signal.connect(self.enableLaunchBtn)
    self.checktask.launch_btn_text_signal.connect(self.setLaunchBtnText)
    self.checktask.launch_btn_click_signal.connect(self.launch)
    self.checktask.return_latest_version.connect(self.returnLatestVersion)

  def run(self):
    self.checktask.start()

  def log(self, line:str):
    self.text.append(line)

  def setPbar(self, value:int):
    self.pbar.setValue(value)

  def showMessage(self, title:str, message:str, buttonText: str = "OK", needClose = False):
    box = QMessageBox()
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    buttonY = box.button(QMessageBox.Ok)
    buttonY.setText(buttonText)
    box.exec()
    
    if needClose:
      self.closeApp()

  def enableUpdateBtn(self, value:bool):
    self.update_btn.setEnabled(value)

  def enableLaunchBtn(self, value:bool):
    self.launch_btn.setEnabled(value)

  def setUpdateBtnText(self, text:str):
    self.update_btn.setText(text)

  def setLaunchBtnText(self, text:str):
    self.launch_btn.setText(text)

  def returnLatestVersion(self, version:str):
    self.latestVersion = version

  def launch(self):
    self.accept()

  def closeApp(self):
    self.close()

  def runUpdate(self):
    self.enableUpdateBtn(False)
    self.enableLaunchBtn(False)
    self.setUpdateBtnText("Updating...")
    self.setPbar(0)

    self.task = UpdateTask()
    self.task.pbar_set_signal.connect(self.setPbar)
    self.task.log_signal.connect(self.log)
    self.task.update_btn_text_signal.connect(self.setUpdateBtnText)
    self.task.launch_btn_signal.connect(self.enableLaunchBtn)
    self.task.update_version = self.latestVersion
    self.task.message_signal.connect(self.showMessage)
    self.task.close_signal.connect(self.closeApp)
    self.task.start()


class CheckUpdateTask(QThread):
  pbar_set_signal = Signal(int)
  log_signal = Signal(str)
  update_btn_signal = Signal(bool)
  launch_btn_signal = Signal(bool)
  launch_btn_text_signal = Signal(str)
  launch_btn_click_signal = Signal()
  return_latest_version = Signal(str)

  def run(self):
    time.sleep(0.5)

    # version
    islatest, latestVersion = self.checkVersion()
    self.return_latest_version.emit(latestVersion)
    self.pbar_set_signal.emit(100)
    if not islatest and latestVersion != "?":
      self.launch_btn_signal.emit(True)
      self.update_btn_signal.emit(True)
    else:
      self.launch_btn_text_signal.emit("Starting...")
      time.sleep(1)
      self.launch_btn_click_signal.emit()

  def checkVersion(self):
    self.log_signal.emit("======= Check Version =======")
    self.log_signal.emit(f"URL: {v.Version.updateMDurl}")
    self.pbar_set_signal.emit(30)
    try:
      islatest, latestVersion = v.Version.checkLatest()
      self.pbar_set_signal.emit(50)
      self.log_signal.emit(f"Latest Version: {latestVersion}")
      self.log_signal.emit(f"Your Version: {v.Program_Version}")
      self.log_signal.emit(f"Version ----- {'Latest' if islatest else 'Need update'}")
    except:
      self.log_signal.emit(f"Version ----- Failed to check version")
      return (False, "?")
    return (islatest, latestVersion)


class UpdateTask(QThread):

  pbar_set_signal = Signal(int)
  log_signal = Signal(str)
  update_btn_text_signal = Signal(str)
  launch_btn_signal = Signal(bool)
  message_signal = Signal(str,str,str,bool)
  close_signal = Signal()

  update_version = None

  updateURL = "https://github.com/ldslds449/Dice_War_Bot/archive/refs/heads/master.zip"

  def download_hook(self, chunk_number, max_size_chunk_read, read_total_size):
    pass

  def is_same(self, file1, file2):
    def sha256(file):
      h  = hashlib.sha256()
      b  = bytearray(128*1024)
      mv = memoryview(b)
      with open(file, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
          h.update(mv[:n])
      return h.hexdigest()

    return sha256(file1) == sha256(file2)

  def delete_files(self, zipFile, zipFolder):
    os.remove(zipFile)
    shutil.rmtree(zipFolder)
    self.log_signal.emit("Finish Deleting Temporary Files")

  def run(self):
    zipFolder = "tmp"
    unzipFolder = os.path.join(zipFolder, "Dice_War_Bot-master")

    self.log_signal.emit("======= Updating =======")

    # download
    r = requests.get(self.updateURL, stream=True)
    zipFile = r.headers.get("content-disposition")[r.headers.get("content-disposition").rfind("=")+1:]
    self.log_signal.emit(f"FileName: {zipFile}")
    fileSize = 13000000 # fake
    totalSave = 0
    self.log_signal.emit("Download...")
    with open(zipFile, 'wb') as f:
      for chunk in r.iter_content(chunk_size=1024):
        if chunk: 
          f.write(chunk)
          totalSave += 1024
          self.pbar_set_signal.emit(min((totalSave / fileSize)*30, 30))
    self.pbar_set_signal.emit(30)

    # unzip
    with zipfile.ZipFile(zipFile, "r") as zip_ref:
      zip_ref.extractall(zipFolder)
    self.pbar_set_signal.emit(50)
    self.log_signal.emit("Finish Extracting")

    # create folder
    for file in glob.glob(os.path.join(zipFolder, "**", "*"), recursive=True):
      if os.path.isdir(file):
        folder_path = os.path.relpath(file, unzipFolder)
        if not os.path.exists(folder_path):
          print(f"Create Folder: {folder_path}")
          os.makedirs(folder_path)
    self.pbar_set_signal.emit(60)
    self.log_signal.emit("Finish Creating Folders")

    # update update.py first
    needRestart = False
    for file in glob.glob(os.path.join(zipFolder, "**", "*"), recursive=True):
      if not os.path.isdir(file):
        if os.path.basename(__file__) == os.path.basename(file):
          if not self.is_same(__file__, file):
            print(f"Need to update {os.path.basename(__file__)} !")
            shutil.move(file, os.path.relpath(file, unzipFolder))
            needRestart = True
            break
    self.pbar_set_signal.emit(70)
    
    if needRestart:
      self.delete_files(zipFile, zipFolder) # remove file
      self.log_signal.emit("You need to restart the app to continue updating...")
      self.message_signal.emit("Restart App", "You need to restart the app to continue updating...", "Close", True)
    else:
      # move files
      for file in glob.glob(os.path.join(zipFolder, "**", "*"), recursive=True):
        if not os.path.isdir(file):
          print(file, os.path.relpath(file, unzipFolder))
          shutil.move(file, os.path.relpath(file, unzipFolder))
      self.pbar_set_signal.emit(90)
      self.log_signal.emit("Finish Copy")

      # install modules
      r = subprocess.run(["python.exe", "-m", "pip", "install", "-r", "requirements.txt"], capture_output=True)
      print(r.stdout.decode("utf-8"))
      if r.returncode != 0:
        self.delete_files(zipFile, zipFolder) # remove file
        self.log_signal.emit("Install Modules Error")
        self.message_signal.emit("Error", "Install Modules Error", "OK", True)
      else:
      # remove file
        self.delete_files(zipFile, zipFolder)

        self.pbar_set_signal.emit(100)
        self.update_btn_text_signal.emit("Finish Updating")
        self.launch_btn_signal.emit(True)

        # change program version to latest version
        v.Program_Version = self.update_version
