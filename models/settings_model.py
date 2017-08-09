from PyQt5.QtCore import QSettings

from models.model import Model
from utils.desktop_utils import get_exe_path

basecamp = "basecamp"
pix4d = "pix4d"
email = "email"
password = "password"

google_maps = "google_maps"
js_api_key = "js_api_key"
static_api_key = "static_api_key"

google_earth = "google_earth"
exe_path = "exe_path"


class SettingsModel(Model):
    @property
    def basecamp_email(self):
        return self.settings.value("{}/{}".format(basecamp, email))

    @basecamp_email.setter
    def basecamp_email(self, value):
        self.settings.setValue("{}/{}".format(basecamp, email), value)

    @property
    def basecamp_password(self):
        return self.settings.value("{}/{}".format(basecamp, password))

    @basecamp_password.setter
    def basecamp_password(self, value):
        self.settings.setValue("{}/{}".format(basecamp, password), value)

    @property
    def pix4d_email(self):
        return self.settings.value("{}/{}".format(pix4d, email))

    @pix4d_email.setter
    def pix4d_email(self, value):
        self.settings.setValue("{}/{}".format(pix4d, email), value)

    @property
    def pix4d_password(self):
        return self.settings.value("{}/{}".format(pix4d, password))

    @pix4d_password.setter
    def pix4d_password(self, value):
        self.settings.setValue("{}/{}".format(pix4d, password), value)

    @property
    def google_maps_js_api_key(self):
        return self.settings.value("{}/{}".format(google_maps, js_api_key))

    @google_maps_js_api_key.setter
    def google_maps_js_api_key(self, value):
        self.settings.setValue("{}/{}".format(google_maps, js_api_key), value)

    @property
    def google_maps_static_api_key(self):
        return self.settings.value("{}/{}".format(google_maps, static_api_key))

    @google_maps_static_api_key.setter
    def google_maps_static_api_key(self, value):
        self.settings.setValue("{}/{}".format(google_maps, static_api_key), value)

    @property
    def google_earth_exe_path(self):
        path = self.settings.value("{}/{}".format(google_earth, exe_path))
        if path is not None:
            return path
        else:
            path = get_exe_path("Google\Google Earth Pro\client\googleearth.exe")
            if path is not None:
                self.google_earth_exe_path = path
                return path
        return None

    @google_earth_exe_path.setter
    def google_earth_exe_path(self, value):
        self.settings.setValue("{}/{}".format(google_earth, exe_path), value)

    def __init__(self):
        super(SettingsModel, self).__init__()
        self.settings = QSettings("RedLine Forensic Studios", "AutoDM")
