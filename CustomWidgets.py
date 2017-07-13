import pyttsx
from PySide.QtCore import Qt
from PySide.QtGui import QDialog, QProgressBar, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


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


class NoLicensesDialog(QDialog):
    def __init__(self, parent=None):
        super(NoLicensesDialog, self).__init__(parent)
        self.setWindowTitle("No Licenses")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.init_ui()

        # self.setWindowFlags(self.windowFlags() | ~Qt.WindowContextHelpButtonHint)
        # self.setWindowFlags(self.windowFlags() | ~Qt.WindowStaysOnBottomHint)
        self.setModal(True)

    def init_ui(self):
        message_lbl = QLabel("No Pix4D licenses available. Would you like to ask for one?")

        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(self.ask_for_license)

        no_btn = QPushButton("No")
        no_btn.clicked.connect(lambda: self.done(0))

        main_layout = QVBoxLayout()
        main_layout.addWidget(message_lbl)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def ask_for_license(self):
        tts = pyttsx.init()
        tts.say("Hey fellas, does anyone have picks four dee open?")
        tts.runAndWait()
        self.done(0)
