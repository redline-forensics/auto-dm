import os.path

from controllers.google_earth_ctrl import GoogleEarthController
from controllers.google_maps_ctrl import GoogleMapsController
from controllers.scene_ctrl import SceneController
from models.google_earth_model import GoogleEarthModel
from models.google_maps_model import GoogleMapsModel
from models.scene_model import SceneModel
from resources.paths import dv_jobs_path
from utils.desktop_utils import open_url, open_path
from views.google_earth_view import GoogleEarthView
from views.google_maps_view import GoogleMapsView
from views.scene_site_view import SceneSiteView
from views.scene_vehicle_view import SceneVehicleView


class JobController(object):
    def __init__(self, job_model):
        self.job_view = None
        self.job_model = job_model

        self.job_model.basecamp_search_done.connect(self.on_basecamp_search_done)

    def init_ui(self, job_view):
        self.job_view = job_view

        self.job_view.base_folder = self.job_model.base_folder
        self.job_view.drone_folder = self.job_model.drone_folder
        self.job_view.scans_folder = self.job_model.scans_folder
        self.job_view.assets_folder = self.job_model.assets_folder

        self.job_view.ui.basecamp_btn.setEnabled(False)
        self.job_view.ui.openair_btn.setEnabled(False)

    def on_basecamp_search_done(self, found):
        self.job_view.ui.basecamp_btn.set_movie(None)
        self.job_view.ui.basecamp_btn.setEnabled(found)

    def change_base_folder(self, show_file_picker):
        if show_file_picker:
            starting_directory = self.job_model.base_folder if self.job_model.base_folder else dv_jobs_path
            new_folder = self.job_view.show_file_picker(starting_directory)
            if not new_folder:  # Was the file picker dialog cancelled?
                return
        else:
            new_folder = self.job_view.base_folder
        self.job_view.base_folder = new_folder

        if not os.path.isdir(new_folder):
            self.job_view.show_invalid_folder_warning(new_folder)
            return

        self.job_model.base_folder = new_folder

        update_other_folders = self.job_view.show_update_job_folders_dialog()
        if update_other_folders:
            self.job_model.find_job_folders()

    def change_drone_folder(self, show_file_picker):
        if show_file_picker:
            starting_directory = self.job_model.drone_folder if self.job_model.drone_folder else dv_jobs_path
            new_folder = self.job_view.show_file_picker(starting_directory)
            if not new_folder:  # Was the file picker dialog cancelled?
                return
        else:
            new_folder = self.job_view.drone_folder
        self.job_view.base_folder = new_folder

        if not os.path.isdir(new_folder):
            self.job_view.show_invalid_folder_warning(new_folder)
            return

        self.job_model.drone_folder = new_folder

    def change_scans_folder(self, show_file_picker):
        if show_file_picker:
            starting_directory = self.job_model.scans_folder if self.job_model.scans_folder else dv_jobs_path
            new_folder = self.job_view.show_file_picker(starting_directory)
            if not new_folder:  # Was the file picker dialog cancelled?
                return
        else:
            new_folder = self.job_view.scans_folder
        self.job_view.scans_folder = new_folder

        if not os.path.isdir(new_folder):
            self.job_view.show_invalid_folder_warning(new_folder)
            return

        self.job_model.scans_folder = new_folder

    def change_assets_folder(self, show_file_picker):
        if show_file_picker:
            starting_directory = self.job_model.assets_folder if self.job_model.assets_folder else dv_jobs_path
            new_folder = self.job_view.show_file_picker(starting_directory)
            if not new_folder:  # Was the file picker dialog cancelled?
                return
        else:
            new_folder = self.job_view.assets_folder
        self.job_view.assets_folder = new_folder

        if not os.path.isdir(new_folder):
            self.job_view.show_invalid_folder_warning(new_folder)
            return

        self.job_model.assets_folder = new_folder

    def open_google_maps_dialog(self):
        google_maps_model = GoogleMapsModel(self.job_model.assets_folder, self.job_model.google_maps_js_api_key,
                                            self.job_model.google_maps_static_api_key)
        google_maps_ctrl = GoogleMapsController(google_maps_model)
        google_maps_view = GoogleMapsView(google_maps_ctrl)
        self.job_view.show_dialog(google_maps_view)

    def open_google_earth_dialog(self):
        google_earth_model = GoogleEarthModel(self.job_model.job_name, self.job_model.google_maps_js_api_key,
                                              self.job_model.google_earth_exe)
        google_earth_ctrl = GoogleEarthController(google_earth_model)
        google_earth_view = GoogleEarthView(google_earth_ctrl)
        self.job_view.show_dialog(google_earth_view)

    def open_scene_site_dialog(self):
        scene_site_model = SceneModel(self.job_model.assets_folder, self.job_model.job_name,
                                      self.job_model.scans_folder, self.job_model.scene_exe)
        scene_site_ctrl = SceneController(scene_site_model)
        scene_site_view = SceneSiteView(scene_site_ctrl)
        self.job_view.show_dialog(scene_site_view)

    def open_scene_vehicle_dialog(self):
        scene_vehicle_model = SceneModel(self.job_model.assets_folder, self.job_model.job_name,
                                         self.job_model.scans_folder, self.job_model.scene_exe)
        scene_vehicle_ctrl = SceneController(scene_vehicle_model)
        scene_vehicle_view = SceneVehicleView(scene_vehicle_ctrl)
        self.job_view.show_dialog(scene_vehicle_view)

    def open_base_folder(self):
        open_path(self.job_model.base_folder)
        self.job_view.minimize()

    def open_drone_folder(self):
        open_path(self.job_model.drone_folder)
        self.job_view.minimize()

    def open_scans_folder(self):
        open_path(self.job_model.scans_folder)
        self.job_view.minimize()

    def open_assets_folder(self):
        open_path(self.job_model.assets_folder)
        self.job_view.minimize()

    def open_basecamp(self):
        open_url(self.job_model.basecamp_url)
        self.job_view.minimize()
