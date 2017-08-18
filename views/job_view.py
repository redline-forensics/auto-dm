import os.path

from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import pyqtSignal

from custom_widgets.animated_button import AnimatedButton
from resources.resource_manager import resources
from views.gen.ui_job_view import Ui_job_tab


class JobView(QWidget):
    # region Properties
    @property
    def base_folder(self):
        return self.ui.base_folder_edit.text()

    @base_folder.setter
    def base_folder(self, value):
        self.ui.base_folder_open_btn.setEnabled(os.path.isdir(value))
        self.ui.base_folder_edit.setText(value)

    @property
    def drone_folder(self):
        return self.ui.drone_folder_edit.text()

    @drone_folder.setter
    def drone_folder(self, value):
        self.ui.drone_folder_open_btn.setEnabled(os.path.isdir(value))
        self.ui.drone_folder_edit.setText(value)

    @property
    def scans_folder(self):
        return self.ui.scans_folder_edit.text()

    @scans_folder.setter
    def scans_folder(self, value):
        self.ui.scans_folder_open_btn.setEnabled(os.path.isdir(value))
        self.ui.scans_folder_edit.setText(value)

    @property
    def assets_folder(self):
        return self.ui.assets_folder_edit.text()

    @assets_folder.setter
    def assets_folder(self, value):
        self.ui.assets_folder_open_btn.setEnabled(os.path.isdir(value))
        self.ui.assets_folder_edit.setText(value)

    # endregion

    request_minimize = pyqtSignal()

    def __init__(self, job_ctrl):
        self.job_ctrl = job_ctrl
        super(JobView, self).__init__()
        self.dialogs = []
        self.build_ui()

    def build_ui(self):
        self.ui = Ui_job_tab()
        self.ui.setupUi(self)

        # Modify UI
        self.ui.basecamp_btn = AnimatedButton("Basecamp")
        self.ui.basecamp_btn.set_movie(QMovie(resources["icons"]["loading.gif"]))
        self.ui.tools_grp_layout.insertWidget(2, self.ui.basecamp_btn)

        # Tell controller that UI modifications are done
        self.job_ctrl.init_ui(self)

        # Signals/Slots
        self.ui.base_folder_edit.returnPressed.connect(
            lambda: self.job_ctrl.change_base_folder(show_file_picker=False))
        self.ui.drone_folder_edit.returnPressed.connect(
            lambda: self.job_ctrl.change_drone_folder(show_file_picker=False))
        self.ui.scans_folder_edit.returnPressed.connect(
            lambda: self.job_ctrl.change_scans_folder(show_file_picker=False))
        self.ui.assets_folder_edit.returnPressed.connect(
            lambda: self.job_ctrl.change_assets_folder(show_file_picker=False))

        self.ui.base_folder_set_btn.clicked.connect(lambda: self.job_ctrl.change_base_folder(show_file_picker=True))
        self.ui.drone_folder_set_btn.clicked.connect(lambda: self.job_ctrl.change_drone_folder(show_file_picker=True))
        self.ui.scans_folder_set_btn.clicked.connect(lambda: self.job_ctrl.change_scans_folder(show_file_picker=True))
        self.ui.assets_folder_set_btn.clicked.connect(lambda: self.job_ctrl.change_assets_folder(show_file_picker=True))

        self.ui.base_folder_open_btn.clicked.connect(self.job_ctrl.open_base_folder)
        self.ui.drone_folder_open_btn.clicked.connect(self.job_ctrl.open_drone_folder)
        self.ui.scans_folder_open_btn.clicked.connect(self.job_ctrl.open_scans_folder)
        self.ui.assets_folder_open_btn.clicked.connect(self.job_ctrl.open_assets_folder)

        self.ui.scene_site_btn.clicked.connect(self.job_ctrl.open_scene_site_dialog)
        self.ui.scene_vehicle_btn.clicked.connect(self.job_ctrl.open_scene_vehicle_dialog)

        self.ui.google_maps_btn.clicked.connect(self.job_ctrl.open_google_maps_dialog)
        self.ui.google_earth_btn.clicked.connect(self.job_ctrl.open_google_earth_dialog)
        self.ui.basecamp_btn.clicked.connect(self.job_ctrl.open_basecamp)

    def show_dialog(self, dialog):
        dialog.show()
        self.dialogs.append(dialog)

    def show_file_picker(self, starting_directory):
        return QFileDialog.getExistingDirectory(self, directory=starting_directory)

    def show_invalid_folder_warning(self, path):
        QMessageBox.warning(self, "Invalid Folder", "The path \"{}\" is invalid.".format(path),
                            QMessageBox.Ok, QMessageBox.NoButton)

    def show_update_job_folders_dialog(self):
        response = QMessageBox.question(self, "Update Folders", "Would you like to update the other job folders?",
                                        QMessageBox.Yes, QMessageBox.No)
        return response == QMessageBox.Yes

    def minimize(self):
        self.request_minimize.emit()

    def show_vehicle_name_input_dialog(self):
        text, ok = QInputDialog.getText(self, "Vehicle Name", "Enter vehicle name:")
        if ok:
            return text
