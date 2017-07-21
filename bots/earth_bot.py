import os
from re import sub

from pywinauto import Application
from pywinauto.application import ProcessNotFoundError


def get_earth_exe():
    program_files_32 = os.environ["ProgramW6432"]
    program_files_64 = os.environ["ProgramFiles(x86)"]

    earth_exe_32 = os.path.join(program_files_32, *["Google", "Google Earth", "client", "googleearth.exe"])
    earth_exe_64 = os.path.join(program_files_64, *["Google", "Google Earth", "client", "googleearth.exe"])

    if os.path.isfile(earth_exe_64):
        earth_exe = earth_exe_64
    elif os.path.isfile(earth_exe_32):
        earth_exe = earth_exe_32
    else:
        raise IOError("Google Earth installation not found")
        # TODO: Manual entry of Google Earth location

    return earth_exe


def get_bottom_margin(width):
    return int(36.6428 + 0.0344658 * width)


try:
    app = Application().connect(path=get_earth_exe())
except ProcessNotFoundError:
    app = Application().start(get_earth_exe())
window = app["Google Earth"]
window.wait("exists")

map_area = window["QWidget9"]

print(map_area.rectangle())
area = map(int, sub("[(LTRB)]", "", str(map_area.rectangle())).split(", "))
print(area)
print("width = " + str(area[2] - area[0]))

map_area.set_focus()
rect = type('obj', (object,), {'left': area[0] + 5, 'top': area[1] + 5, 'right': area[2] - 84,
                               'bottom': area[3] - max(76, get_bottom_margin(area[2] - area[0]))})
map_area.CaptureAsImage(rect=rect).save("test.png")
# QPixmap.grabWindow(map_area.handle, 0, 0, area[2] - 84, int(area[3] - (area[2] * 0.047))).save("test.png")
# time.sleep(5)
# window.set_focus()
# keyboard.SendKeys("^o")
# keyboard.SendKeys(os.path.abspath("earth.kml"))
# keyboard.SendKeys("{ENTER}")
