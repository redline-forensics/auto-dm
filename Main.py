import sys

from PySide.QtGui import *


class MainUI(QWidget):
    def __init__(self):
        super(MainUI, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.create_controls()
        self.create_layout()
        self.make_connections()

        self.setWindowTitle("AutoDM")
        self.show()

    def create_controls(self):
        self.job_num_edit = QLineEdit()

        self.job_num_add_button = QPushButton("Add")

        self.jobs_tab_widget = QTabWidget()
        self.jobs_tab_widget.setTabsClosable(True)

    def create_layout(self):
        main_layout = QVBoxLayout()

        job_num_layout = QHBoxLayout()
        job_num_layout.addWidget(self.job_num_edit)
        job_num_layout.addWidget(self.job_num_add_button)
        main_layout.addLayout(job_num_layout)

        main_layout.addWidget(self.jobs_tab_widget)

        self.setLayout(main_layout)

    def make_connections(self):
        self.job_num_add_button.clicked.connect(self.add_job)
        self.jobs_tab_widget.tabCloseRequested.connect(self.remove_job)

    def add_job(self):
        job_num = self.job_num_edit.text()
        tab_page = TabPage()

        self.jobs_tab_widget.addTab(tab_page, job_num)

    def remove_job(self, index):
        widget = self.jobs_tab_widget.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.jobs_tab_widget.removeTab(index)


class TabPage(QWidget):
    def __init__(self):
        super(TabPage, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.create_controls()
        self.create_layout()

    def create_controls(self):
        # region Job Folders
        self.base_job_folder_edit = QLineEdit()
        self.base_job_folder_edit.setPlaceholderText("Base Job Folder")

        self.base_job_folder_button = QPushButton(
            QIcon("C:/Users/Crohlfing/PycharmProjects/AutoDM/resources/icons/open.png"), "")

        self.drone_folder_edit = QLineEdit()
        self.drone_folder_edit.setPlaceholderText("Drone Folder")

        self.drone_folder_button = QPushButton(
            QIcon("C:/Users/Crohlfing/PycharmProjects/AutoDM/resources/icons/open.png"), "")

        self.scans_folder_edit = QLineEdit()
        self.scans_folder_edit.setPlaceholderText("Scans Folder")

        self.scans_folder_button = QPushButton(
            QIcon("C:/Users/Crohlfing/PycharmProjects/AutoDM/resources/icons/open.png"), "")

        self.drawings_folder_edit = QLineEdit()
        self.drawings_folder_edit.setPlaceholderText("Drawings Folder")

        self.drawings_folder_button = QPushButton(
            QIcon("C:/Users/Crohlfing/PycharmProjects/AutoDM/resources/icons/open.png"), "")
        # endregion

        # region Job Controls
        self.open_job_folder_button = QPushButton("Open Job Folder")
        self.open_basecamp_page_button = QPushButton("Open Basecamp Page")
        self.open_basecamp_page_button.setDisabled(True)
        self.add_to_open_air_button = QPushButton("Add to Open Air")
        self.add_to_open_air_button.setDisabled(True)
        # endregion

        # region SCENE
        self.scene_vehicle = QPushButton("Vehicle Scan")
        self.scene_site = QPushButton("Site Scan")
        self.scene_copy_folder = QPushButton("Copy Files to Job Folder")
        # endregion

        # region Pix4D
        self.pix4d_vehicle = QPushButton("Vehicle Drone")
        self.pix4d_site = QPushButton("Site Drone")
        self.pix4d_copy_folder = QPushButton("Copy Files to Job Folder")
        # endregion

    def create_layout(self):
        main_layout = QHBoxLayout()

        first_column = QVBoxLayout()

        job_folders_group = QGroupBox("Job Folders")
        job_folders_layout = QGridLayout()
        job_folders_layout.addWidget(self.base_job_folder_edit, 0, 0)
        job_folders_layout.addWidget(self.base_job_folder_button, 0, 1)
        job_folders_layout.addWidget(self.drone_folder_edit, 1, 0)
        job_folders_layout.addWidget(self.drone_folder_button, 1, 1)
        job_folders_layout.addWidget(self.scans_folder_edit, 2, 0)
        job_folders_layout.addWidget(self.scans_folder_button, 2, 1)
        job_folders_layout.addWidget(self.drawings_folder_edit, 3, 0)
        job_folders_layout.addWidget(self.drawings_folder_button, 3, 1)
        job_folders_group.setLayout(job_folders_layout)
        first_column.addWidget(job_folders_group)

        job_controls_group = QGroupBox("Job Controls")
        job_controls_layout = QVBoxLayout()
        job_controls_layout.addWidget(self.open_job_folder_button)
        job_controls_layout.addWidget(self.open_basecamp_page_button)
        job_controls_layout.addWidget(self.add_to_open_air_button)
        job_controls_group.setLayout(job_controls_layout)
        first_column.addWidget(job_controls_group)

        main_layout.addLayout(first_column)

        second_column = QVBoxLayout()

        scene_group = QGroupBox("SCENE")
        scene_layout = QVBoxLayout()
        scene_layout.addWidget(self.scene_vehicle)
        scene_layout.addWidget(self.scene_site)
        scene_layout.addWidget(self.scene_copy_folder)
        scene_group.setLayout(scene_layout)
        second_column.addWidget(scene_group)

        pix4d_group = QGroupBox("Pix4D")
        pix4d_layout = QVBoxLayout()
        pix4d_layout.addWidget(self.pix4d_vehicle)
        pix4d_layout.addWidget(self.pix4d_site)
        pix4d_layout.addWidget(self.pix4d_copy_folder)
        pix4d_group.setLayout(pix4d_layout)
        second_column.addWidget(pix4d_group)

        main_layout.addLayout(second_column)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
