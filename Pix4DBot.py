import os
import re
import shutil
import time
import warnings
import win32gui
from win32api import GetSystemMetrics

from PySide.QtCore import QThread, Signal, Qt
from PySide.QtGui import QMessageBox, QFileDialog, QProgressDialog
from pywinauto import Application, keyboard, clipboard
from pywinauto.timings import TimeoutError

import CustomWidgets
import Preferences
from Main import JobType

warnings.filterwarnings("error")
pix4d_path = os.path.expanduser("~/Documents/pix4d")


def _run_on_ui(fn):
    fn()


def get_pixel_colour(x, y, window=None):
    if window is not None:
        point = window.ClientToScreen((x, y))
        x = point[0]
        y = point[1]
    desktop_window_id = win32gui.GetDesktopWindow()
    desktop_window_dc = win32gui.GetWindowDC(desktop_window_id)
    long_color = win32gui.GetPixel(desktop_window_dc, x, y)
    color = int(long_color)
    return (color & 0xff), ((color >> 8) & 0xff), ((color >> 16) & 0xff)


class Bot(object):
    def __init__(self, parent, job_type, vehicle=None):
        self.job_num = parent.job_num
        self.drone_dir = parent.drone_dir
        self.job_type = job_type
        self.parent = parent

        if JobType(job_type.value) is JobType.SITE:
            print("site")
            self.proj_name = "J{:d}_Site".format(self.job_num)
        elif JobType(job_type.value) is JobType.VEHICLE:
            print("vehicle")
            self.proj_name = "J{:d}_{}".format(self.job_num, vehicle)
        self.proj_path = os.path.join(pix4d_path, self.proj_name)

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

    def show_project_already_exists(self):
        flags = QMessageBox.StandardButton.Yes
        flags |= QMessageBox.StandardButton.No
        response = QMessageBox.warning(self.drone_tool, "Project Already Exists",
                                       "The project folder \"{}\" already exists. Would you like to "
                                       "overwrite it?".format(self.proj_name), flags)
        if response == QMessageBox.StandardButton.Yes:
            if os.path.exists(self.proj_path + ".p4d"):
                backup_path = self.proj_path + "_bak"
                if os.path.exists(backup_path + ".p4d"):
                    for x in range(0, 99):
                        try:
                            os.rename(self.proj_path + ".p4d", backup_path + str(x) + ".p4d")
                            break
                        except OSError:
                            continue
                else:
                    os.rename(self.proj_path + ".p4d", backup_path + ".p4d")
            self.worker.new_project()

    def show_unable_to_select_images(self):
        QMessageBox.warning(self.drone_tool, "Image Selection Error",
                            "Unable to add images. Please complete the New Project wizard manually.")

    def show_drone_tool(self):
        self.drone_tool = CustomWidgets.DroneTool(self.job_type, self.parent)
        self.drone_tool.copy_pictures_button.clicked.connect(self.copy_pictures)
        self.drone_tool.new_proj_button.clicked.connect(self.worker.new_project)
        self.drone_tool.show()
        self.drone_tool.setGeometry(GetSystemMetrics(0) - self.drone_tool.width() * 1.1, 200, self.drone_tool.width(),
                                    self.drone_tool.height())

    def hide_drone_tool(self):
        if self.drone_tool is not None:
            self.drone_tool.done(0)
            self.drone_tool = None

    def copy_pictures(self):
        if not os.path.exists(self.proj_path):
            os.makedirs(self.proj_path)
        pic_files = QFileDialog.getOpenFileNames(self.drone_tool, "Select Drone Pictures", self.drone_dir,
                                                 "All supported image formats (*.jpg *.jpeg *.tif *.tiff)"
                                                 ";;JPEG images (*.jpg *.jpeg);;TIFF images (*.tif *.tiff)")[0]
        num_pic_files = len(pic_files)
        if num_pic_files == 0:
            return

        self.picture_copier = self.PictureCopier(pic_files, self)
        progress_dlg = QProgressDialog("Copying images...", "Cancel", 0, num_pic_files, self.drone_tool)
        progress_dlg.setWindowTitle("Copying...")
        progress_dlg.setWindowModality(Qt.WindowModal)
        progress_dlg.canceled.connect(self.picture_copier.cancel)
        self.picture_copier.update_progress.connect(progress_dlg.setValue)

        progress_dlg.show()
        self.picture_copier.start()

    class PictureCopier(QThread):
        update_progress = Signal(int)

        def __init__(self, pic_files, parent):
            super(Bot.PictureCopier, self).__init__()
            self.pic_files = pic_files
            self.canceled = False
            self.parent = parent

        def run(self):
            print(self.pic_files)
            for index, pic_file in enumerate(self.pic_files):
                self.update_progress.emit(index)
                if self.canceled:
                    break
                shutil.copy(pic_file, self.parent.proj_path)
            self.update_progress.emit(len(self.pic_files))

        def cancel(self):
            self.canceled = True

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

            self.pix4d_wnd = None

            t_end = time.time() + 10
            while time.time() < t_end:
                top_wnd = self.app.top_window()
                if top_wnd is not None:
                    self.pix4d_wnd = top_wnd
                    break

            self.run_on_ui.emit(self.parent.hide_loading)

            wnd_title = self.pix4d_wnd.WindowText()

            if wnd_title == "Pix4Ddesktop Login":
                self._login(self.pix4d_wnd)
                self.pix4d_wnd = self.app.window(title_re="Pix4Ddiscovery.*")
                try:
                    self.pix4d_wnd.wait("exists", 10)
                except TimeoutError:
                    print("Exiting")
                    return
                self.run_on_ui.emit(self.parent.show_drone_tool)
            elif "Pix4Ddiscovery" in wnd_title:
                self.run_on_ui.emit(self.parent.show_drone_tool)

            self.pix4d_wnd.wait_not("exists", 86400)
            self.run_on_ui.emit(self.parent.hide_drone_tool)

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

                no_license_color = get_pixel_colour(237, 215, license_dlg)

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

        def copy_pictures(self):
            pass

        def new_project(self):
            # self.run_on_ui.emit(lambda: self.parent.show_loading("Loading New Project..."))
            self.pix4d_wnd.set_focus()
            keyboard.SendKeys("^n")

            new_proj_wnd = self.app["New Project"]
            new_proj_wnd.wait("exists", 10)
            new_proj_wnd.set_focus()
            new_proj_wnd.click_input(coords=(90, 130))

            keyboard.SendKeys(self.parent.proj_name)
            keyboard.SendKeys("{ENTER}")
            already_exists_color = get_pixel_colour(28, 110, new_proj_wnd)
            if already_exists_color[0] == 255 and already_exists_color[1] < 255 and already_exists_color[2] < 255:
                # keyboard.SendKeys("{TAB 7}{ENTER}")
                new_proj_wnd.close()
                self.run_on_ui.emit(self.parent.show_project_already_exists)
                return

            keyboard.SendKeys("{TAB}{TAB}{ENTER}")
            select_dirs_dlg = self.app["Select Directories"]
            select_dirs_dlg.wait("exists", 10)
            keyboard.SendKeys(self.parent.proj_name)
            keyboard.SendKeys("{ENTER}")
            not_enough_images_color = get_pixel_colour(40, 92, new_proj_wnd)  # red = (237,28,36), green = (108,164,56)
            if not_enough_images_color[0] > 220 and not_enough_images_color[1] < 50 and not_enough_images_color[2] < 50:
                self.run_on_ui.emit(self.parent.show_unable_to_select_images)
                return
            keyboard.SendKeys("{UP 9}{ENTER}")

            time.sleep(5)
            keyboard.SendKeys("{TAB 5}{ENTER}")
            keyboard.SendKeys("f")
            keyboard.SendKeys("{TAB 5}{ENTER}")
            keyboard.SendKeys("{HOME}{ENTER}")

        def stop(self):
            if self.app is not None:
                self.app.kill_()
