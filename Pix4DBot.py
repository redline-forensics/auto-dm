import os
import re
import warnings
import CustomWidgets

from PySide.QtCore import QThread, Qt, Signal
from PySide.QtGui import QMessageBox
from pywinauto import Application


class Bot(QThread):
    startup_started = Signal(object)
    startup_finished = Signal()

    def __init__(self):
        # QThread.__init__(self, parent)
        super(Bot, self).__init__()
        self.parent = None

        self.startup_started.connect(startup_show_loading)
        self.startup_finished.connect(startup_hide_loading)

        self.app = None

    def set_parent(self, parent):
        self.parent = parent

    def run(self):
        program_files_32 = os.environ["ProgramW6432"]
        program_files_64 = os.environ["ProgramFiles(x86)"]

        pix4d_exe_32 = os.path.join(program_files_32, *["Pix4Dmapper", "pix4dmapper.exe"])
        pix4d_exe_64 = os.path.join(program_files_64, *["Pix4Dmapper", "pix4dmapper.exe"])

        if os.path.isfile(pix4d_exe_64):
            pix4d_exe = pix4d_exe_64
        elif os.path.isfile(pix4d_exe_32):
            pix4d_exe = pix4d_exe_32
        else:
            raise IOError("Pix4D installation not found")
            # TODO: Manual entry of Pix4D location

        self.startup_started.emit(self.parent)
        try:
            self.app = Application().start(pix4d_exe)
        except UserWarning as user_warning:
            warning_nums = re.findall(r"\d+", str(user_warning))

            pix4d_bitness = int(warning_nums[0])
            python_bitness = int(warning_nums[1])

            flags = QMessageBox.StandardButton.Yes
            flags |= QMessageBox.StandardButton.No
            response = QMessageBox.warning(self.parent, "Warning",
                                           "Attempting to start {:d}-bit Pix4D using {:d}-bit Python. Unexpected "
                                           "behavior may occur. Proceed?".format(pix4d_bitness, python_bitness),
                                           flags)
            if response == QMessageBox.StandardButton.Yes:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.app = Application().start(pix4d_exe)
            else:
                return

        login_dlg = self.app["Pix4Ddesktop Login"]
        login_dlg.wait("exists", 10)
        self.startup_finished.emit()

    def stop(self):
        if self.app is not None:
            self.app.kill_()


def start_bot(parent=None):
    bot.set_parent(parent)
    bot.start()


def stop_bot():
    bot.stop()
    bot.quit()


def startup_show_loading(parent):
    global loading_dlg
    loading_dlg = CustomWidgets.IndefiniteProgressDialog("Loading...", "Loading Pix4D...", parent)
    loading_dlg.show()


def startup_hide_loading():
    global loading_dlg
    if loading_dlg is not None:
        loading_dlg.done(0)


warnings.filterwarnings("error")
bot = Bot()
