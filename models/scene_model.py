import os
import time
import warnings
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal
from pywinauto import Application
from pywinauto.application import TimeoutError

from models.model import Model
from utils.desktop_utils import open_path

long_wait_time = 7200


def queued(fn):
    def wrapper(self):
        self.queue.put(lambda: fn(self))

    return wrapper


class SceneModel(Model):
    auto_place_scans_finished = pyqtSignal(bool)
    manual_place_scans_finished = pyqtSignal(bool)

    def __init__(self, assets_folder, job_name, scans_folder, scene_exe, vehicle_name=None):
        self.assets_folder = assets_folder
        self.vehicle_name = vehicle_name
        self.proj_name = "{}_{}".format(job_name, vehicle_name if vehicle_name else "Site")
        self.scans_folder = scans_folder
        self.scene_exe = scene_exe
        super(SceneModel, self).__init__()

        self.application = None
        self.main_window = None

        self.queue = Queue()
        self.scene_worker = SceneWorker(self.scene_exe, self.queue)
        self.scene_worker.start()
        self.start_scene()

    @queued
    def start_scene(self):
        warnings.simplefilter("ignore", UserWarning)
        self.application = Application().start(self.scene_exe)
        self.main_window = self.application.window(title_re=".*SCENE.*")

    @queued
    def new_project(self):
        self.main_window.menu_select("File->New->Project")
        new_project_dlg = self.application["Create New Scan Project"]
        new_project_dlg.wait("visible")
        new_project_dlg["Edit1"].set_edit_text(self.proj_name)
        new_project_dlg["Button1"].click()

    @queued
    def import_scans(self):
        open_path(self.scans_folder)

    @queued
    def load_scans(self):
        self.get_scans_menu().item("Load All Scans").click_input()

    @queued
    def place_scans_auto(self):
        self.place_scans("Top View Based")
        success = self.place_scans("Cloud to Cloud")
        self.auto_place_scans_finished.emit(success)

    @queued
    def place_scans_manual(self):
        success = self.place_scans("Target Based")
        self.manual_place_scans_finished.emit(success)

    def place_scans(self, type):
        place_scans_dlg = self.get_place_scans_dialog()
        place_scans_dlg["ComboBox1"].select(type)
        place_scans_dlg["SysTabControl"].select("General")
        place_scans_dlg["Enable auto clustering"].uncheck()
        place_scans_dlg["OK"].click()

        timeout = time.time() + long_wait_time

        top_window = self.application.top_window()
        top_window_text = top_window.window_text().lower() if top_window.window_text() else None
        while time.time() < timeout and (not top_window_text or (
                        top_window_text and top_window_text != "scene" and top_window_text != "/scans/scanmanager ")):
            print(top_window_text)
            top_window = self.application.top_window()
            top_window_text = top_window.window_text().lower() if top_window.window_text() else None
            time.sleep(1)

        if top_window_text == "scene":
            success = False
            top_window["OK"].click()
            top_window.wait_not("visible")
        else:
            success = True
        done_dlg = self.application["/Scans/ScanManager"]
        done_dlg["OK"].click()
        return success

    def get_place_scans_dialog(self):
        self.get_scans_menu().get_menu_path("Operations->Registration->Place Scans")[-1].click_input()
        place_scans_dlg = self.application["Place Scans"]
        place_scans_dlg.wait("visible")
        return place_scans_dlg

    def get_place_scans_loading_dialog(self):
        place_scans_loading_dlg = self.application["Place Scans"]
        place_scans_loading_dlg.wait("visible")
        return place_scans_loading_dlg

    @queued
    def create_point_cloud(self):
        self.get_scans_menu().get_menu_path("Operations->Point Cloud Tools->Create Scan Point Clouds")[-1].click_input()
        point_cloud_dlg = self.application["Project Point Cloud / Scan Point Cloud Settings"]
        point_cloud_dlg.wait("visible")
        point_cloud_dlg["OK"].click()

        point_cloud_loading_dlg = self.application.window(title_re="Create Scan Point Clouds.*")
        point_cloud_loading_dlg.wait_not("visible", long_wait_time)

    @queued
    def delete_point_cloud(self):
        self.get_scans_menu().get_menu_path("Operations->Point Cloud Tools->Delete Scan Point Clouds")[-1].click_input()
        confirmation_dlg = self.application["SCENE"]
        confirmation_dlg["OK"].click()

    @queued
    def place_clipping_box(self):
        self.main_window["Standard Toolbar"].button(10).click()
        time.sleep(3)
        self.main_window["3D Toolbar"].button(42).click()

        try:
            warning_dialog = self.application["Information"]
            warning_dialog.wait("visible", 5)
            warning_dialog["OK"].click()
        except TimeoutError:
            pass

    @queued
    def apply_pictures(self):
        self.get_scans_menu().get_menu_path("Operations->Color/Pictures->Apply Pictures")[-1].click_input()
        colorize_progress_dlg = self.application.window(title_re="Colorize scans")
        colorize_progress_dlg.wait_not("visible", long_wait_time)

    @queued
    def take_intensity_ortho(self):
        self.take_ortho("Intensity")

    @queued
    def take_color_ortho(self):
        self.take_ortho("Color")

    def take_ortho(self, type):
        ortho_dlg = self.get_ortho_dialog()
        ortho_dlg["Edit1"].set_edit_text(200 if self.vehicle_name else 20)
        ortho_dlg["ComboBox1"].select("Imperial Units")
        ortho_dlg["Show scale"].check()
        ortho_dlg["Create Orthophoto"].click()

        save_dlg = self.application["Save As"]
        ortho_name = "{}_Ortho_{}".format(self.proj_name, type)
        save_dlg["Edit1"].set_edit_text(os.path.join(self.assets_folder, ortho_name))
        save_dlg["Save"].click()

        ortho_progress_dlg = self.application["Creating Orthophoto..."]
        ortho_progress_dlg.wait_not("visible", long_wait_time)

    def get_ortho_dialog(self):
        self.main_window["Orthophoto Toolbar"].button(0).click()
        ortho_dlg = self.application["Create Orthophoto"]
        ortho_dlg.wait("visible")

    def get_scans_menu(self):
        tree_view = self.main_window["TreeView"]
        if not tree_view:
            return None

        scans_item = tree_view.get_item([self.proj_name, "Scans"])
        if not scans_item:
            return None

        scans_item.click_input(button="right")
        scans_menu = self.application.PopupMenu
        try:
            scans_menu.wait("visible", 10)
        except TimeoutError:
            return None
        return scans_menu.menu()


class SceneWorker(QThread):
    def __init__(self, scene_exe, queue):
        self.scene_exe = scene_exe
        self.queue = queue
        super(SceneWorker, self).__init__()
        self.running = True

    def run(self):
        while self.running:
            if self.queue.empty():
                continue

            fn = self.queue.get()
            fn()

    def quit(self):
        self.running = False
