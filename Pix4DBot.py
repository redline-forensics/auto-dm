import os
import re
import warnings
import CustomWidgets

from PySide.QtCore import QThread, Signal
from PySide.QtGui import QMessageBox
from pywinauto import Application
from pywinauto.timings import TimeoutError


class Bot(QThread):
    run_on_ui = Signal(object)

    def __init__(self):
        # QThread.__init__(self, parent)
        super(Bot, self).__init__()
        self.parent = None

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

        self.run_on_ui.emit(_startup_show_loading)
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
        try:
            login_dlg.wait("exists", 10)
        except TimeoutError:
            self.run_on_ui.emit(_startup_hide_loading)
            self.run_on_ui.emit(_startup_show_timeout)
            return
        self.run_on_ui.emit(_startup_hide_loading)

    def stop(self):
        if self.app is not None:
            self.app.kill_()


def start_bot(parent=None):
    bot.set_parent(parent)
    bot.start()

    global _parent
    _parent = parent


def stop_bot():
    bot.stop()
    bot.quit()


def _startup_show_loading():
    global _loading_dlg
    _loading_dlg = CustomWidgets.IndefiniteProgressDialog("Loading...", "Loading Pix4D...", _parent)
    _loading_dlg.show()


def _startup_hide_loading():
    if _loading_dlg is not None:
        _loading_dlg.done(0)


def _startup_show_timeout():
    QMessageBox.warning(_parent, "Timed Out", "Could not open Pix4D.")


def _run_on_ui(fn):
    fn()


warnings.filterwarnings("error")
bot = Bot()
bot.run_on_ui.connect(_run_on_ui)
_parent = None
_loading_dlg = None
