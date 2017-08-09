from PyQt5.QtWidgets import QProgressDialog, QFileDialog, QMessageBox

from views.google_maps_earth_view import GoogleMapsEarthView

default_sleep_time = 25000 / (8 * 60 * 60)  # 25000 free requests per day / # of seconds per day


class GoogleMapsView(GoogleMapsEarthView):
    def build_ui(self):
        super(GoogleMapsView, self).build_ui()

        # Modify UI
        self.setWindowTitle("Google Maps Tool")
        self.ui.overlap_lbl.setVisible(False)
        self.ui.overlap_spn.setVisible(False)
        self.ui.interval_spn.setMinimum(0.0)
        self.ui.interval_spn.setValue(default_sleep_time)

        # Signals/Slots
        self.ui.start_btn.clicked.connect(self.google_maps_earth_ctrl.create_image)

    def show_stitching_progress_dialog(self, max):
        self.stitching_progress_dialog = QProgressDialog("Starting map stitcher...", "Cancel", 0, max, self)
        self.stitching_progress_dialog.setWindowTitle("Stitching...")
        self.stitching_progress_dialog.setModal(True)
        self.stitching_progress_dialog.canceled.connect(self.google_maps_earth_ctrl.cancel_image_create)
        self.stitching_progress_dialog.show()

    def update_stitching_progress_dialog(self, progress):
        self.stitching_progress_dialog.setLabelText(
            "Fetching tile {:d} of {:d}...".format(progress, self.stitching_progress_dialog.maximum()))
        self.stitching_progress_dialog.setValue(progress)

    def close_stitching_progress_dialog(self):
        self.stitching_progress_dialog.hide()
        self.stitching_progress_dialog.deleteLater()

    def show_image_save_dialog(self, starting_directory):
        return QFileDialog.getSaveFileName(self, "Save Image", starting_directory, "TIFF (*.tif *.tiff)")[0]

    def show_discard_confirmation_dialog(self):
        response = QMessageBox.warning(self, "Discard Map", "Are you sure you want to discard the stitched map?",
                                       QMessageBox.Yes, QMessageBox.No)
        return response == QMessageBox.Yes
