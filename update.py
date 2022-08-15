from PySide6.QtWidgets import QDialog, QTextEdit, QProgressBar, QVBoxLayout, QMessageBox, QPushButton, QHBoxLayout
from PySide6.QtCore import QThread, Signal, Qt
  
import time
import urllib.request
import zipfile
import shutil
import glob
import os

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
    self.checktask.message_signal.connect(self.showMessage)
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

  def showMessage(self, title:str, message:str):
    QMessageBox.information(self, title, message, QMessageBox.Ok)

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
    self.task.start()


class CheckUpdateTask(QThread):
  pbar_set_signal = Signal(int)
  log_signal = Signal(str)
  message_signal = Signal(str,str)
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

  update_version = None

  updateURL = "https://github.com/ldslds449/Dice_War_Bot/archive/refs/heads/master.zip"

  def download_hook(self, chunk_number, max_size_chunk_read, read_total_size):
    pass

  def run(self):
    zipFile = "code.zip"
    zipFolder = "tmp"
    unzipFolder = os.path.join(zipFolder, "Dice_War_Bot-master")

    self.log_signal.emit("======= Updating =======")

    # download
    self.log_signal.emit("Download...")
    urllib.request.urlretrieve(self.updateURL, zipFile, reporthook=self.download_hook)
    self.pbar_set_signal.emit(50)

    # unzip
    with zipfile.ZipFile(zipFile, "r") as zip_ref:
      zip_ref.extractall(zipFolder)
    self.pbar_set_signal.emit(70)
    self.log_signal.emit("Finish Extracting")

    # move file
    for file in glob.glob(os.path.join(zipFolder, "**", "*"), recursive=True):
      if not os.path.isdir(file):
        print(file, os.path.relpath(file, unzipFolder))
        shutil.move(file, os.path.relpath(file, unzipFolder))
    self.pbar_set_signal.emit(90)
    self.log_signal.emit("Finish Copy")

    # remove file
    os.remove(zipFile)
    shutil.rmtree(zipFolder)
    self.pbar_set_signal.emit(100)
    self.log_signal.emit("Finish Deleting Temporary Files")

    self.update_btn_text_signal.emit("Finish Updating")
    self.launch_btn_signal.emit(True)

    # change program version to latest version
    v.Program_Version = self.update_version
