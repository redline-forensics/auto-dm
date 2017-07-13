import os
import re
import time
import warnings
import win32gui

import pyttsx
from PySide.QtCore import QThread, Signal, Qt
from PySide.QtGui import QMessageBox
from pywinauto import Application, keyboard, clipboard
from pywinauto.timings import TimeoutError

import CustomWidgets
import Preferences
from Main import JobType

warnings.filterwarnings("error")


def _run_on_ui(fn):
    fn()


def get_pixel_colour(x, y):
    desktop_window_id = win32gui.GetDesktopWindow()
    desktop_window_dc = win32gui.GetWindowDC(desktop_window_id)
    long_color = win32gui.GetPixel(desktop_window_dc, x, y)
    color = int(long_color)
    return (color & 0xff), ((color >> 8) & 0xff), ((color >> 16) & 0xff)


class Bot(object):
    def __init__(self, job_num, job_type, vehicle=None, parent=None):
        self.job_num = job_num
        self.job_type = job_type
        self.parent = parent

        if JobType(job_type.value) is JobType.SITE:
            print("site")
            self.proj_name = "J{:d}_Site".format(job_num)
        elif JobType(job_type.value) is JobType.VEHICLE:
            print("vehicle")
            self.proj_name = "J{:d}_{}".format(job_num, vehicle)

        self.worker = Bot.Worker(self)
        self.worker.run_on_ui.connect(_run_on_ui)
        self.loading_dlg = None

    def start(self):
        self.worker.start()

    def stop(self):
        self.worker.stop()
        self.worker.quit()

    def show_loading(self, message, title="Loading..."):
        self.loading_dlg = CustomWidgets.IndefiniteProgressDialog(title, message, self.parent)
        self.loading_dlg.show()

    def hide_loading(self):
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

    def show_license_unavailable(self):
        license_unavailable_dlg = CustomWidgets.NoLicensesDialog(self.parent)
        license_unavailable_dlg.show()

    class Worker(QThread):
        run_on_ui = Signal(object)

        def __init__(self, parent):
            super(Bot.Worker, self).__init__()
            self.parent = parent
            self.ignore_bitness_error = False
            self.app = None

        def run(self):
            self.run_on_ui.emit(lambda: self.parent.show_loading("Loading Pix4D..."))
            if not self.get_app():
                return

            pix4d_wnd = None

            t_end = time.time() + 10
            while time.time() < t_end:
                top_wnd = self.app.top_window()
                if top_wnd is not None:
                    pix4d_wnd = top_wnd
                    break

            self.run_on_ui.emit(self.parent.hide_loading)

            wnd_title = pix4d_wnd.WindowText()

            if wnd_title == "Pix4Ddesktop Login":
                self._login(pix4d_wnd)
                pix4d_wnd = self.app.window(title_re="Pix4Ddiscovery.*")
                try:
                    pix4d_wnd.wait("exists", 10)
                except TimeoutError:
                    print("Exiting")
                    return
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
                self.run_on_ui.emit(self.parent.hide_loading)

                warning_nums = re.findall(r"\d+", str(user_warning))
                pix4d_bitness = int(warning_nums[0])
                python_bitness = int(warning_nums[1])
                self.run_on_ui.emit(lambda: self.parent.show_bitness_error(pix4d_bitness, python_bitness))

                return False

        def _login(self, login_dlg):
            try:
                login_dlg.wait("exists", 10)
            except TimeoutError:
                self.run_on_ui.emit(self.parent.hide_loading)
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

            try:
                login_dlg.click_input(coords=(45, 220))
                login_dlg.wait_not("visible")

                license_dlg = self.app["Pix4Ddesktop Login"]
                license_dlg.wait("visible", 10)
                license_dlg.set_focus()

                time.sleep(1)

                no_license_location = license_dlg.ClientToScreen((237, 215))
                no_license_color = get_pixel_colour(no_license_location[0], no_license_location[1])

                if no_license_color[0] == 255 and no_license_color[1] < 255 and no_license_color[2] < 255:
                    self.run_on_ui.emit(self.parent.show_license_unavailable)
                else:
                    print("License available")

                try:
                    license_dlg.wait_not("exists", 120)
                except TimeoutError:
                    license_dlg.Close()
            except TimeoutError:
                return

        def _new_project(self, main_wnd):
            main_wnd.set_focus()
            keyboard.SendKeys("^n")

            new_proj_wnd = self.app["New Project"]
            self.run_on_ui.emit(lambda: self.parent.show_loading("Loading New Project..."))
            new_proj_wnd.wait("exists", 10)
            self.run_on_ui.emit(self.parent.hide_loading)
            new_proj_wnd.set_focus()
            new_proj_wnd.click_input(coords=(90, 130))

            keyboard.SendKeys(self.parent.proj_name)

        def stop(self):
            if self.app is not None:
                self.app.kill_()
