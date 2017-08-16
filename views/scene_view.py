from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QMessageBox


class SceneView(QWidget):
    def __init__(self, scene_ctrl):
        self.scene_ctrl = scene_ctrl
        super(SceneView, self).__init__(flags=Qt.WindowStaysOnTopHint)
        self.build_ui()

    def build_ui(self):
        self.ui = None

    def show_auto_place_scans_failed_dialog(self):
        QMessageBox.warning(self, "Place Scans Failed", "Failed to automatically place scans. Try manual placement.",
                            QMessageBox.Ok, QMessageBox.NoButton)

    def show_manual_place_scans_failed_dialog(self):
        QMessageBox.warning(self, "Place Scans Failed",
                            "Failed to manually place scans. Try matching points or planes.", QMessageBox.Ok,
                            QMessageBox.NoButton)
