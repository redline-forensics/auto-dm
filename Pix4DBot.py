import os
import re
import shutil
import time
import warnings
import win32gui

from PySide.QtCore import QThread, Signal
from PySide.QtGui import QMessageBox, QProgressDialog, QFileDialog
from pywinauto import Application, keyboard
from pywinauto.timings import TimeoutError

import Preferences
from CustomWidgets import IndefiniteProgressDialog, NoLicensesDialog, DroneTool
from JobType import JobType

warnings.filterwarnings("error")
pix4d_path = os.path.expanduser("~/Documents/pix4d")


def get_pixel_color(x, y, window=None):
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
    def __init__(self, parent, job_type, vehicle=None, standalone=False):
        self.job_num = parent.job_num
        self.drone_dir = parent.drone_dir
        self.job_type = JobType(job_type.value)
        self.parent = parent
        if self.job_type is JobType.SITE:
            self.proj_name = "J{:d}_Site".format(self.job_num)
        elif self.job_type is JobType.VEHICLE:
            self.proj_name = "J{:d}_{}".format(self.job_num, vehicle)
        self.proj_path = os.path.join(pix4d_path, self.proj_name)

        self.copy_pictures_progress_dialog = None

        self.init_threads()
        self.init_dialogs()

        if standalone:
            try:
                self.set_app()
                self.show_tool_window()
            except UserWarning as e:
                bitness = re.findall(r"\d+", str(e))
                pix4d_bitness = int(bitness[0])
                python_bitness = int(bitness[1])
                self.show_bitness_error_dialog(pix4d_bitness, python_bitness, True)
        else:
            self.app = None
            self.open_pix4d()

    def set_app(self, ignore_bitness_error=False):
        if ignore_bitness_error:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.app = Application().connect(path=Pix4DOpenWorker.get_pix4d_exe())
        else:
            self.app = Application().connect(path=Pix4DOpenWorker.get_pix4d_exe())

    def init_threads(self):
        self.pix4d_open_worker = Pix4DOpenWorker()
        self.pix4d_open_worker.bitness_error.connect(self.show_bitness_error_dialog)
        self.pix4d_open_worker.opened.connect(self.on_pix4d_opened)
        self.pix4d_open_worker.timed_out.connect(self.on_timed_out)

        self.pix4d_login_worker = Pix4DLoginWorker()
        self.pix4d_login_worker.logged_in.connect(self.on_logged_in)
        self.pix4d_login_worker.no_license_available.connect(self.on_no_license_available)
        self.pix4d_login_worker.timed_out.connect(self.on_timed_out)

        self.copy_pictures_worker = CopyPicturesWorker(self.proj_path)
        # self.copy_pictures_worker.update_progress.connect(self.copy_pictures_progress_dialog.setValue)

        self.new_project_worker = NewProjectWorker(self.proj_path, self.proj_name)
        self.new_project_worker.already_exists.connect(self.on_new_project_already_exists)
        self.new_project_worker.created.connect(self.on_new_project_created)
        self.new_project_worker.timed_out.connect(self.on_timed_out)

        self.start_processing_worker = StartProcessingWorker()
        self.start_processing_worker.started.connect(self.on_processing_started)

        self.mosaic_editor_worker = MosaicEditorWorker()
        self.mosaic_editor_worker.opened.connect(self.on_mosaic_editor_opened)

    def init_dialogs(self):
        self.pix4d_open_progress_dialog = IndefiniteProgressDialog("Opening...", "Opening Pix4D...", self.parent)
        self.pix4d_login_progress_dialog = IndefiniteProgressDialog("Logging in...", "Logging in to Pix4D...",
                                                                    self.parent)
        self.no_license_available_dialog = NoLicensesDialog()

        self.drone_tool = DroneTool(self.job_type)
        self.drone_tool.copy_pictures_button.clicked.connect(self.copy_pictures)
        self.drone_tool.new_proj_button.clicked.connect(self.new_project)
        self.drone_tool.start_proc_button.clicked.connect(self.start_processing)
        self.drone_tool.edit_mosaic_button.clicked.connect(self.open_mosaic_editor)

        self.copy_pictures_progress_dialog = QProgressDialog("Copying pictures...", "Cancel", 0, 0, self.drone_tool)
        self.copy_pictures_progress_dialog.setWindowTitle("Copying...")
        self.copy_pictures_progress_dialog.setModal(True)
        self.copy_pictures_progress_dialog.canceled.connect(self.copy_pictures_worker.cancel)
        self.copy_pictures_worker.update_progress.connect(self.copy_pictures_progress_dialog.setValue)

        self.new_project_progress_dialog = IndefiniteProgressDialog("Creating...", "Creating new project...",
                                                                    self.drone_tool)

        self.start_processing_progress_dialog = IndefiniteProgressDialog("Starting...", "Starting processing...",
                                                                         self.drone_tool)

        self.mosaic_editor_progress_dialog = IndefiniteProgressDialog("Opening...", "Opening mosaic editor...",
                                                                      self.drone_tool)

    def open_pix4d(self):
        self.pix4d_open_worker.start()
        self.pix4d_open_progress_dialog.show()

    def on_pix4d_opened(self, app):
        self.pix4d_open_progress_dialog.hide()
        self.pix4d_login_progress_dialog.show()
        self.app = app
        self.pix4d_login_worker.start(self.app)

    def show_bitness_error_dialog(self, pix4d_bitness, python_bitness, standalone=False):
        if standalone:
            connect_string = "attach to"
        else:
            connect_string = "start"

        flags = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        response = QMessageBox.warning(self.parent, "Warning",
                                       "Attempting to {} {:d}-bit Pix4D using {:d}-bit Python. "
                                       "Unexpected behavior may occur. Proceed?"
                                       .format(connect_string, pix4d_bitness, python_bitness),
                                       flags)
        if response == QMessageBox.StandardButton.Yes:
            if standalone:
                self.set_app(True)
                self.show_tool_window()
            else:
                self.pix4d_open_worker.ignore_bitness_error = True
                self.open_pix4d()
        elif response == QMessageBox.StandardButton.No:
            if not standalone:
                self.pix4d_open_progress_dialog.hide()

    def on_logged_in(self):
        self.pix4d_login_progress_dialog.hide()

        pix4d_window = None
        t_end = time.time() + 10
        while time.time() < t_end and pix4d_window is None:
            pix4d_window = self.app.top_window()
        if pix4d_window is None:
            self.on_timed_out()
            return
        pix4d_window_title = pix4d_window.WindowText()
        if "Pix4D" not in pix4d_window_title:  # If window isn't the main Pix4D window
            # TODO: better error handling
            print("ERROR: not correct window")
            return

        self.show_tool_window()

    def show_tool_window(self):
        self.drone_tool.show()

    def hide_tool_window(self):
        self.drone_tool.hide()

    def on_no_license_available(self):
        self.no_license_available_dialog.show()

    def on_timed_out(self):
        self.pix4d_open_progress_dialog.hide()
        self.pix4d_login_progress_dialog.hide()
        self.new_project_progress_dialog.hide()

        print("Timed out")

    def copy_pictures(self):
        pic_files = QFileDialog.getOpenFileNames(self.drone_tool, "Select Drone Pictures", self.drone_dir,
                                                 "All supported image formats (*.jpg *.jpeg *.tif *.tiff)"
                                                 ";;JPEG images (*.jpg *.jpeg);;TIFF images (*.tif *.tiff)")[0]
        num_pic_files = len(pic_files)
        if num_pic_files == 0:
            return

        self.copy_pictures_progress_dialog.setMaximum(num_pic_files)
        self.copy_pictures_progress_dialog.show()
        self.copy_pictures_worker.start(pic_files)

    def new_project(self):
        self.new_project_progress_dialog.show()
        self.new_project_worker.start(self.app)

    def on_new_project_already_exists(self):
        flags = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        response = QMessageBox.warning(self.drone_tool, "Project Already Exists",
                                       "The project {} already exists. Would you like to overwrite it?"
                                       .format(self.proj_name),
                                       flags)
        if response == QMessageBox.StandardButton.Yes:
            self.new_project_worker.start(self.app, True)
        elif response == QMessageBox.StandardButton.No:
            self.new_project_progress_dialog.hide()

    def on_new_project_created(self):
        self.new_project_progress_dialog.hide()

    def start_processing(self):
        self.start_processing_progress_dialog.show()
        self.start_processing_worker.start(self.app)

    def on_processing_started(self):
        self.start_processing_progress_dialog.hide()

    def open_mosaic_editor(self):
        self.mosaic_editor_progress_dialog.show()
        self.mosaic_editor_worker.start(self.app)

    def on_mosaic_editor_opened(self):
        self.mosaic_editor_progress_dialog.hide()


class Pix4DOpenWorker(QThread):
    timed_out = Signal()
    bitness_error = Signal(int, int)
    opened = Signal(object)

    def __init__(self, ignore_bitness_error=False):
        super(Pix4DOpenWorker, self).__init__()
        self.ignore_bitness_error = ignore_bitness_error

    def run(self):
        try:
            if self.ignore_bitness_error:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    app = self.start_pix4d()
            else:
                app = self.start_pix4d()

            pix4d_window = None
            t_end = time.time() + 10
            while time.time() < t_end and pix4d_window is None:
                pix4d_window = app.top_window()
            if pix4d_window is None:
                self.timed_out.emit()
                return

            self.opened.emit(app)
        except UserWarning as e:
            bitness = re.findall(r"\d+", str(e))
            pix4d_bitness = int(bitness[0])
            python_bitness = int(bitness[1])
            self.bitness_error.emit(pix4d_bitness, python_bitness)

    @staticmethod
    def get_pix4d_exe():
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

        return pix4d_exe

    def start_pix4d(self):
        return Application().start(self.get_pix4d_exe())


class Pix4DLoginWorker(QThread):
    timed_out = Signal()
    no_license_available = Signal()
    logged_in = Signal()

    def __init__(self):
        super(Pix4DLoginWorker, self).__init__()
        self.app = None

    def start(self, app):
        self.app = app
        super(Pix4DLoginWorker, self).start()

    def run(self):
        if self.app is None:
            return

        pix4d_window = self.app.top_window()
        pix4d_window_title = pix4d_window.WindowText()
        if pix4d_window_title != "Pix4Ddesktop Login":  # If window isn't the login window
            self.logged_in.emit()
            return
        if not self.log_in(pix4d_window):
            return

        pix4d_window = None
        t_end = time.time() + 10
        while time.time() < t_end and pix4d_window is None:
            pix4d_window = self.app.top_window()
        if pix4d_window is None:
            self.timed_out.emit()
            return
        pix4d_window_title = pix4d_window.WindowText()
        if pix4d_window_title != "Pix4Ddesktop Login":  # If window isn't the license window
            self.logged_in.emit()
            return
        if not self.choose_license(pix4d_window):
            return

        self.logged_in.emit()

    def log_in(self, log_in_window):
        log_in_window.set_focus()

        email = Preferences.get_pix4d_email()
        if email != "":
            log_in_window.click_input(coords=(45, 170))  # Email (textbox)
            keyboard.SendKeys("^a")  # Ctrl + A
            keyboard.SendKeys(email)  # Type email

        password = Preferences.get_pix4d_password()
        if password != "":
            log_in_window.click_input(coords=(45, 195))  # Password (textbox)
            keyboard.SendKeys("^a")
            keyboard.SendKeys(password)

        if email != "" and password != "":
            log_in_window.click_input(coords=(45, 220))  # Login (button)

        try:
            log_in_window.wait_not("visible", 120)
            return True
        except TimeoutError:
            self.timed_out.emit()
            return False

    def choose_license(self, license_window):
        license_window.set_focus()

        no_license_color = get_pixel_color(237, 215, license_window)  # Check area where "no license available" shows
        if no_license_color[0] == 255 and no_license_color[1] < 255 and no_license_color[2] < 255:  # If area is red
            self.no_license_available.emit()
            available_license = False
        else:
            # TODO: automatically choose license
            available_license = True

        try:
            license_window.wait_not("exists", 120)
            return True
        except TimeoutError:
            self.timed_out.emit()
            return False


class CopyPicturesWorker(QThread):
    update_progress = Signal(int)

    def __init__(self, proj_path):
        super(CopyPicturesWorker, self).__init__()
        self.proj_path = proj_path
        self.canceled = False

    def start(self, pic_files):
        self.pic_files = pic_files
        super(CopyPicturesWorker, self).start()

    def run(self):
        if not os.path.exists(self.proj_path):
            os.makedirs(self.proj_path)

        for index, pic_file in enumerate(self.pic_files):
            self.update_progress.emit(index)
            if self.canceled:
                break
            shutil.copy(pic_file, self.proj_path)
        self.update_progress.emit(len(self.pic_files))

    def cancel(self):
        self.canceled = True


class NewProjectWorker(QThread):
    already_exists = Signal()
    not_enough_images = Signal()
    created = Signal()
    timed_out = Signal()

    def __init__(self, proj_path, proj_name):
        super(NewProjectWorker, self).__init__()
        self.proj_path = proj_path
        self.proj_name = proj_name
        self.app = None

    def start(self, app, overwrite=False):
        self.app = app
        self.overwrite = overwrite
        super(NewProjectWorker, self).start()

    def run(self):
        if self.app is None:
            return

        if self.overwrite:
            proj_p4d_path = self.proj_path + ".p4d"
            proj_p4d_backup_path = self.proj_path + "_bak.p4d"
            if os.path.exists(proj_p4d_path):
                if os.path.isfile(proj_p4d_backup_path):
                    os.remove(proj_p4d_backup_path)
                os.rename(proj_p4d_path, proj_p4d_backup_path)

        pix4d_window = self.app.window(title_re="Pix4D.*")
        pix4d_window.set_focus()
        keyboard.SendKeys("^n")

        new_proj_wnd = self.app["New Project"]
        try:
            new_proj_wnd.wait("exists", 10)
        except TimeoutError:
            self.timed_out.emit()
            return
        new_proj_wnd.set_focus()
        new_proj_wnd.click_input(coords=(90, 130))
        keyboard.SendKeys("^a")
        keyboard.SendKeys(self.proj_name)
        keyboard.SendKeys("{ENTER}")

        already_exists_color = get_pixel_color(28, 110, new_proj_wnd)
        if already_exists_color[0] == 255 and already_exists_color[1] < 255 and already_exists_color[2] < 255:
            self.already_exists.emit()
            return

        keyboard.SendKeys("{TAB 2}{ENTER}")
        select_dirs_dlg = self.app["Select Directories"]
        try:
            select_dirs_dlg.wait("exists", 10)
        except TimeoutError:
            self.timed_out.emit()
            return
        keyboard.SendKeys(self.proj_name)
        keyboard.SendKeys("{ENTER}")

        not_enough_images_color = get_pixel_color(40, 92, new_proj_wnd)
        if not_enough_images_color[0] > 220 and not_enough_images_color[1] < 50 and not_enough_images_color[2] < 50:
            self.not_enough_images.emit()
            return

        keyboard.SendKeys("{UP 9}{ENTER}")

        time.sleep(5)

        keyboard.SendKeys("{TAB 5}{ENTER}")
        keyboard.SendKeys("f")
        keyboard.SendKeys("{TAB 5}{ENTER}")
        keyboard.SendKeys("{HOME}{ENTER}")

        time.sleep(1)

        pix4d_window_height = int(pix4d_window.rectangle().height())
        pix4d_window.click_input(coords=(209, pix4d_window_height - 129))  # 2. Point Cloud and Mesh (checkbox)
        pix4d_window.click_input(coords=(354, pix4d_window_height - 129))  # 3. DSM, Orthomosaic and Index (checkbox)
        pix4d_window.click_input(coords=(38, pix4d_window_height - 64))  # Processing Options (button)
        proc_opt_wnd = self.app["Processing Options"]
        try:
            proc_opt_wnd.wait("exists", 10)
        except TimeoutError:
            self.timed_out.emit()
            return
        proc_opt_wnd.set_focus()
        proc_opt_wnd.click_input(coords=(309, 154))  # Custom (radio)
        proc_opt_wnd.click_input(coords=(334, 179))  # cm/pixel (textbox)
        keyboard.SendKeys("^a")  # Ctrl+A (select all)
        keyboard.SendKeys("2")
        keyboard.SendKeys("{ENTER}")

        self.created.emit()


class StartProcessingWorker(QThread):
    started = Signal()

    def __init__(self):
        super(StartProcessingWorker, self).__init__()
        self.app = None

    def start(self, app):
        self.app = app
        super(StartProcessingWorker, self).start()

    def run(self):
        if self.app is None:
            return

        pix4d_window = self.app.window(title_re="Pix4D.*")
        pix4d_window.set_focus()
        pix4d_window.click_input(coords=(704, pix4d_window.rectangle().height() - 49))  # Start (button)

        self.started.emit()


class MosaicEditorWorker(QThread):
    opened = Signal()

    def __init__(self):
        super(MosaicEditorWorker, self).__init__()
        self.app = None

    def start(self, app):
        self.app = app
        super(MosaicEditorWorker, self).start()

    def run(self):
        if self.app is None:
            return

        pix4d_window = self.app.window(title_re="Pix4D.*")
        pix4d_window.set_focus()
        pix4d_window.click_input(coords=(39, 313))  # Mosaic Editor (button)

        self.opened.emit()
