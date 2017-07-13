from PySide.QtGui import QDialog, QProgressBar, QVBoxLayout, QLabel
from PySide.QtCore import Qt


class IndefiniteProgressDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super(IndefiniteProgressDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.message = message
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.init_ui()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

    def init_ui(self):
        message_lbl = QLabel(self.message)
        message_lbl.setAlignment(Qt.AlignHCenter)

        progress = QProgressBar()
        progress.setTextVisible(False)
        progress.setRange(0, 0)

        layout = QVBoxLayout()
        layout.addWidget(message_lbl)
        layout.addWidget(progress)
        self.setLayout(layout)
