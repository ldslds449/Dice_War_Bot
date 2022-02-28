from task import *
from ui import *
from screen import *

ui = UI()
task = Task()

print(getWindowSizeInfo(task.hwnd))
print(getWindowSizeInfo(task.hwndChild))
# resizeWindow(task.hwnd, (414, 710))
print(getWindowSizeInfo(task.hwnd))
print(getWindowSizeInfo(task.hwndChild))


ui.setTask(task)
ui.RUN()
