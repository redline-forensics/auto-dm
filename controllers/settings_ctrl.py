class SettingsController(object):
    def __init__(self, settings_model):
        self.settings_view = None
        self.settings_model = settings_model

    def init_ui(self, settings_view):
        self.settings_view = settings_view

        self.settings_view.ui.apply_btn.setEnabled(False)

        self.settings_view.basecamp_email = self.settings_model.basecamp_email
        self.settings_view.basecamp_password = self.settings_model.basecamp_password
        self.settings_view.pix4d_email = self.settings_model.pix4d_email
        self.settings_view.pix4d_password = self.settings_model.pix4d_password
        self.settings_view.google_maps_js_api_key = self.settings_model.google_maps_js_api_key
        self.settings_view.google_maps_static_api_key = self.settings_model.google_maps_static_api_key
        self.settings_view.google_earth_exe_path = self.settings_model.google_earth_exe_path
        self.settings_view.scene_exe_path = self.settings_model.scene_exe_path

    def settings_changed(self):
        self.settings_view.ui.apply_btn.setEnabled(True)

    def apply_changes(self):
        self.settings_model.basecamp_email = self.settings_view.basecamp_email
        self.settings_model.basecamp_password = self.settings_view.basecamp_password
        self.settings_model.pix4d_email = self.settings_view.pix4d_email
        self.settings_model.pix4d_password = self.settings_view.pix4d_password
        self.settings_model.google_maps_js_api_key = self.settings_view.google_maps_js_api_key
        self.settings_model.google_maps_static_api_key = self.settings_view.google_maps_static_api_key
        self.settings_model.google_earth_exe_path = self.settings_view.google_earth_exe_path
        self.settings_model.scene_exe_path = self.settings_view.scene_exe_path
        self.settings_view.ui.apply_btn.setEnabled(False)
