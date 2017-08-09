import os

from PyQt5.QtWidgets import QProgressDialog, QFileDialog

from utils.time_utils import convert_seconds
from views.google_maps_earth_view import GoogleMapsEarthView

default_interval = 5.0


class GoogleEarthView(GoogleMapsEarthView):
    def build_ui(self):
        super(GoogleEarthView, self).build_ui()

        # Modify UI
        self.setWindowTitle("Google Earth Tool")
        self.ui.interval_spn.setMinimum(1.0)
        self.ui.interval_spn.setValue(5.0)

        # Signals/Slots
        self.ui.start_btn.clicked.connect(self.google_maps_earth_ctrl.start_capturing)

    def show_google_earth_exe_picker(self):
        return QFileDialog.getOpenFileName(self, "Choose Google Earth Executable", os.environ["ProgramFiles(x86)"],
                                           "EXE (*.exe)")[0]

    def show_capture_progress_dialog(self, min_, max_):
        self.capture_progress_dialog = QProgressDialog("Starting screenshot capture...", "Cancel", min_, max_, self)
        self.capture_progress_dialog.setWindowTitle("Capturing...")
        self.capture_progress_dialog.setModal(True)
        self.capture_progress_dialog.canceled.connect(self.google_maps_earth_ctrl.cancel_captures)
        self.capture_progress_dialog.show()

    def update_capture_progress_dialog(self, progress):
        hours, minutes, seconds = convert_seconds(self.capture_progress_dialog.maximum() - progress)
        self.capture_progress_dialog.setLabelText(
            "Time remaining: {:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
        self.capture_progress_dialog.setValue(progress)

    def close_capture_progress_dialog(self):
        self.capture_progress_dialog.hide()
        self.capture_progress_dialog.deleteLater()
