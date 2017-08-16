from PyQt5.QtWidgets import QDialog

from views.gen.ui_settings_view import Ui_settings_view


class SettingsView(QDialog):
    @property
    def basecamp_email(self):
        return self.ui.basecamp_email_edit.text()

    @basecamp_email.setter
    def basecamp_email(self, value):
        self.ui.basecamp_email_edit.setText(value)

    @property
    def basecamp_password(self):
        return self.ui.basecamp_password_edit.text()

    @basecamp_password.setter
    def basecamp_password(self, value):
        self.ui.basecamp_password_edit.setText(value)

    @property
    def pix4d_email(self):
        return self.ui.pix4d_email_edit.text()

    @pix4d_email.setter
    def pix4d_email(self, value):
        self.ui.pix4d_email_edit.setText(value)

    @property
    def pix4d_password(self):
        return self.ui.pix4d_password_edit.text()

    @pix4d_password.setter
    def pix4d_password(self, value):
        self.ui.pix4d_password_edit.setText(value)

    @property
    def google_maps_js_api_key(self):
        return self.ui.google_maps_js_api_key_edit.text()

    @google_maps_js_api_key.setter
    def google_maps_js_api_key(self, value):
        self.ui.google_maps_js_api_key_edit.setText(value)

    @property
    def google_maps_static_api_key(self):
        return self.ui.google_maps_static_api_key_edit.text()

    @google_maps_static_api_key.setter
    def google_maps_static_api_key(self, value):
        self.ui.google_maps_static_api_key_edit.setText(value)

    @property
    def google_earth_exe_path(self):
        return self.ui.google_earth_exe_path_edit.text()

    @google_earth_exe_path.setter
    def google_earth_exe_path(self, value):
        self.ui.google_earth_exe_path_edit.setText(value)

    @property
    def scene_exe_path(self):
        return self.ui.scene_exe_path_edit.text()

    @scene_exe_path.setter
    def scene_exe_path(self, value):
        self.ui.scene_exe_path_edit.setText(value)

    def __init__(self, settings_ctrl):
        self.settings_ctrl = settings_ctrl
        super(SettingsView, self).__init__()

        self.build_ui()

    def build_ui(self):
        self.ui = Ui_settings_view()
        self.ui.setupUi(self)

        # Tell the controller that UI modifications are done
        self.settings_ctrl.init_ui(self)

        # Signals/Slots
        self.ui.ok_btn.clicked.connect(self.accept)
        self.ui.cancel_btn.clicked.connect(self.reject)
        self.ui.apply_btn.clicked.connect(self.settings_ctrl.apply_changes)

        self.ui.basecamp_email_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.basecamp_password_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.pix4d_email_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.pix4d_password_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.google_maps_js_api_key_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.google_maps_static_api_key_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.google_earth_exe_path_edit.textEdited.connect(self.settings_ctrl.settings_changed)
        self.ui.scene_exe_path_edit.textEdited.connect(self.settings_ctrl.settings_changed)

    def accept(self):
        self.settings_ctrl.apply_changes()
        super(SettingsView, self).accept()
