import os
import re
import time
import warnings

from PySide.QtCore import QThread, Signal
from PySide.QtGui import QMessageBox
from pywinauto import Application, keyboard, clipboard
from pywinauto.timings import TimeoutError

import CustomWidgets
import Preferences

warnings.filterwarnings("error")


def _run_on_ui(fn):
    fn()


class Bot(object):
    def __init__(self, job_num, parent=None):
        self.job_num = job_num
        self.parent = parent
        self.worker = Bot.Worker(self)
        self.worker.run_on_ui.connect(_run_on_ui)
        self.loading_dlg = None

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.stop()
        self.worker.quit()

    def startup_show_loading(self):
        if self.loading_dlg is None:
            self.loading_dlg = CustomWidgets.IndefiniteProgressDialog("Loading...", "Loading Pix4D...", self.parent)
        self.loading_dlg.show()

    def startup_hide_loading(self):
        if self.loading_dlg is not None:
            self.loading_dlg.done(0)
            self.loading_dlg = None

    def startup_show_timeout(self):
        QMessageBox.warning(self.parent, "Timed Out", "Could not open Pix4D.")

    def show_bitness_error(self, pix4d_bitness, python_bitness):
        self.stop()

        flags = QMessageBox.StandardButton.Yes
        flags |= QMessageBox.StandardButton.No
        response = QMessageBox.warning(self.parent, "Warning",
                                       "Attempting to start {:d}-bit Pix4D using {:d}-bit Python. Unexpected "
                                       "behavior may occur. Proceed?".format(pix4d_bitness, python_bitness),
                                       flags)
        if response == QMessageBox.StandardButton.Yes:
            self.worker.set_ignore_bitness_error(True)
            self.worker.start()

    class Worker(QThread):
        run_on_ui = Signal(object)

        def __init__(self, parent):
            super(Bot.Worker, self).__init__()
            self.parent = parent
            self.ignore_bitness_error = False
            self.app = None

        def run(self):
            self.run_on_ui.emit(self.parent.startup_show_loading)
            if not self.get_app():
                return

            pix4d_wnd = None

            t_end = time.time() + 10
            while time.time() < t_end:
                top_wnd = self.app.top_window()
                if top_wnd is not None:
                    pix4d_wnd = top_wnd
                    break

            self.run_on_ui.emit(self.parent.startup_hide_loading)

            wnd_title = pix4d_wnd.WindowText()

            if wnd_title == "Pix4Ddesktop Login":
                self._login(pix4d_wnd)
                pix4d_wnd = self.app.window(title_re="Pix4Ddiscovery.*")
                self._new_project(pix4d_wnd)
            elif "Pix4Ddiscovery" in wnd_title:
                self._new_project(pix4d_wnd)

        def set_ignore_bitness_error(self, ignore):
            self.ignore_bitness_error = ignore

        def get_app(self):
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

            try:
                if self.ignore_bitness_error:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.app = Application().start(pix4d_exe)
                else:
                    self.app = Application().start(pix4d_exe)
                return True
            except UserWarning as user_warning:
                self.run_on_ui.emit(self.parent.startup_hide_loading)

                warning_nums = re.findall(r"\d+", str(user_warning))
                pix4d_bitness = int(warning_nums[0])
                python_bitness = int(warning_nums[1])
                self.run_on_ui.emit(lambda: self.parent.show_bitness_error(pix4d_bitness, python_bitness))

                return False

        def _login(self, login_dlg):
            try:
                login_dlg.wait("exists", 10)
            except TimeoutError:
                self.run_on_ui.emit(self.parent.startup_hide_loading)
                self.run_on_ui.emit(self.parent.startup_show_timeout)
                return

            email = Preferences.get_pix4d_email()
            if email != "":
                login_dlg.click_input(coords=(45, 170))
                keyboard.SendKeys("^a^c")
                if clipboard.GetData() != email:
                    keyboard.SendKeys("{BACK}")
                    keyboard.SendKeys(email)

            password = Preferences.get_pix4d_password()
            if password != "":
                login_dlg.click_input(coords=(45, 195))
                keyboard.SendKeys("^a^c{BACK}")
                keyboard.SendKeys(password)

            login_dlg.click_input(coords=(45, 220))

            license_dlg = self.app["Pix4Ddesktop Login"]
            try:
                license_dlg.wait("exists", 10)
                license_dlg.wait_not("exists")
            except TimeoutError:
                return

        def _new_project(self, main_wnd):
            main_wnd.set_keyboard_focus()
            keyboard.SendKeys("^n")

        def stop(self):
            if self.app is not None:
                self.app.kill_()
