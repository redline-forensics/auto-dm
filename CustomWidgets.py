import pyttsx
from PySide.QtCore import Qt
from PySide.QtGui import QDialog, QProgressBar, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTabWidget, QWidget

from Main import JobType


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


class DroneTool(QDialog):
    def __init__(self, job_type, parent=None):
        super(DroneTool, self).__init__(parent)
        self.job_type = job_type
        if JobType(job_type.value) is JobType.SITE:
            print("site")
            self.setWindowTitle("Drone Site Tool")
        elif JobType(job_type.value) is JobType.VEHICLE:
            print("vehicle")
            self.setWindowTitle("Drone Vehicle Tool")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setModal(False)
        self.init_ui()

    def init_ui(self):
        self.copy_pictures_button = QPushButton("Copy Pictures From Server")
        self.new_proj_button = QPushButton("New Project")
        self.start_proc_button = QPushButton("Start Processing")
        self.edit_mosaic_button = QPushButton("Edit Mosaic")

        main_layout = QVBoxLayout()
        main_tab = QTabWidget()
        manual_widget = QWidget()
        manual_layout = QVBoxLayout()
        manual_layout.addWidget(self.copy_pictures_button)
        manual_layout.addWidget(self.new_proj_button)
        manual_layout.addWidget(self.start_proc_button)
        manual_layout.addWidget(self.edit_mosaic_button)
        manual_widget.setLayout(manual_layout)
        main_tab.addTab(manual_widget, "Manual")
        main_layout.addWidget(main_tab)
        self.setLayout(main_layout)
