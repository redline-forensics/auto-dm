import os.path

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from requests.auth import HTTPBasicAuth

from models.model import Model


class JobModel(Model):
    basecamp_search_done = pyqtSignal(bool)

    @property
    def job_name(self):
        return "J{:d}".format(self.job_num)

    def __init__(self, job_num, base_folder, basecamp_email, basecamp_password, google_maps_js_api_key,
                 google_maps_static_api_key, google_earth_exe, scene_exe):
        self.job_num = job_num
        self.base_folder = base_folder
        self.basecamp_email = basecamp_email
        self.basecamp_password = basecamp_password
        self.google_maps_js_api_key = google_maps_js_api_key
        self.google_maps_static_api_key = google_maps_static_api_key
        self.google_earth_exe = google_earth_exe
        self.scene_exe = scene_exe

        super(JobModel, self).__init__()

        self.drone_folder = ""
        self.scans_folder = ""
        self.assets_folder = ""
        self.basecamp_url = None

        self.find_basecamp_url()
        self.find_job_folders()

    def find_job_folders(self):
        def find_drone_folder():
            charlotte_drone_path = os.path.join(self.base_folder, "Drone")
            if os.path.isdir(charlotte_drone_path):
                return charlotte_drone_path

            nashville_drone_path = os.path.join(self.base_folder, *["Photographs", "Drone"])
            if os.path.isdir(nashville_drone_path):
                return nashville_drone_path

            return ""

        def find_scans_folder():
            charlotte_scans_path = os.path.join(self.base_folder, "Scans")
            if os.path.isdir(charlotte_scans_path):
                return charlotte_scans_path

            nashville_scans_path_0 = os.path.join(self.base_folder, "Scan Data")
            if os.path.isdir(nashville_scans_path_0):
                return nashville_scans_path_0

            nashville_scans_path_1 = os.path.join(self.base_folder, "Scanned Data")
            if os.path.isdir(nashville_scans_path_1):
                return nashville_scans_path_1

            return ""

        def find_assets_folder():
            charlotte_drawings_path = os.path.join(self.base_folder, "Drawings")
            charlotte_drawing_path = os.path.join(self.base_folder, "Drawing")
            if os.path.isdir(charlotte_drawings_path):
                drawings_path = charlotte_drawings_path
            elif os.path.isdir(charlotte_drawing_path):
                drawings_path = charlotte_drawing_path
            else:
                return ""

            charlotte_assets_path = os.path.join(drawings_path, "Assets")
            charlotte_asset_path = os.path.join(drawings_path, "Asset")
            if os.path.isdir(charlotte_assets_path):
                return charlotte_assets_path
            elif os.path.isdir(charlotte_asset_path):
                return charlotte_asset_path
            else:
                return drawings_path

        self.drone_folder = find_drone_folder()
        self.scans_folder = find_scans_folder()
        self.assets_folder = find_assets_folder()

    def find_basecamp_url(self):
        email = self.basecamp_email
        password = self.basecamp_password

        self.basecamp_worker = BasecampWorker(self.job_name, email, password)
        self.basecamp_worker.page_found.connect(self.on_basecamp_page_found)
        self.basecamp_worker.page_not_found.connect(self.on_basecamp_page_not_found)
        self.basecamp_worker.start()

    def on_basecamp_page_found(self, basecamp_url):
        self.basecamp_url = basecamp_url
        self.basecamp_search_done.emit(True)

    def on_basecamp_page_not_found(self):
        self.basecamp_search_done.emit(False)


class BasecampWorker(QThread):
    page_found = pyqtSignal(str)
    page_not_found = pyqtSignal()

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        super(BasecampWorker, self).__init__()

    def run(self):
        jobs = requests.get("https://basecamp.com/2103842/api/v1/projects.json",
                            auth=HTTPBasicAuth(self.email, self.password))
        if not jobs:
            self.page_not_found.emit()
            return

        for job in jobs.json():
            if self.name in job["name"]:
                self.page_found.emit(job["app_url"])
                return
        self.page_not_found.emit()
