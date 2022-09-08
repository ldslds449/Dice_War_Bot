if __name__ == '__main__':
  import sys

  from PySide6.QtWidgets import QApplication, QDialog
  from update import *

  print('Starting...')

  app = QApplication(sys.argv)
  update = Update()
  update.show()
  update.run()
 
  if update.exec() == QDialog.Accepted:
    # run ui
    from ui import *
    ui = UI()
    ui.RUN()

  print('Exited')
  sys.exit(0)

