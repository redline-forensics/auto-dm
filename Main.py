import os.path
import sys

from PySide.QtGui import *

from JobDirFinder import *

resource_path = os.path.join(os.path.split(__file__)[0], "resources")
icon_path = os.path.join(resource_path, "icons")


class MainUI(QWidget):
    def __init__(self):
        super(MainUI, self).__init__()
        self.jobs_dict = dict()
        self.init_ui()

    def init_ui(self):
        main_icon = QIcon(os.path.join(icon_path, "main.png"))
        self.tray_icon = QSystemTrayIcon(main_icon)
        self.setWindowTitle("AutoDM")
        self.setWindowIcon(main_icon)
        self.resize(644, 405)

        self.create_controls()
        self.create_layout()
        self.make_connections()

        self.show()

    def create_controls(self):
        self.job_num_edit = QLineEdit()
        self.job_num_edit.setValidator(QIntValidator())
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
        self.job_num_edit.returnPressed.connect(self.job_num_add_button.click)
        self.job_num_add_button.clicked.connect(self.find_job)
        self.jobs_tab_widget.tabCloseRequested.connect(self.remove_job)
        self.tray_icon.activated.connect(self.restore_window)

    def find_job(self):
        job_num = self.job_num_edit.text()
        if job_num == "":
            return
        else:
            job_num = int(job_num)

        if self.jobs_dict.get(job_num, 0) > 0:
            flags = QMessageBox.StandardButton.Yes
            flags |= QMessageBox.StandardButton.No
            response = QMessageBox.warning(self, "J{:d} Already Open".format(job_num),
                                           "J{:d} is already open. Open a new instance anyway?".format(job_num), flags)
            if response == QMessageBox.StandardButton.No:
                return

        job_dir_finder = FindJobDir(job_num)
        job_dir_finder.finished.connect(self.add_job)
        try:
            job_dir_finder.start()
        except IOError:
            QMessageBox.critical(self, "J{:d} Not Found".format(job_num),
                                 "Could not find J{:d} on the server".format(job_num))

    def add_job(self, num, job_dir):
        self.jobs_dict[num] = self.jobs_dict.get(num, 0) + 1
        tab_page = TabPage(job_dir)
        self.jobs_tab_widget.addTab(tab_page, "J" + str(num))

    def remove_job(self, index):
        job_num = int(self.jobs_tab_widget.tabText(index)[1:])
        self.jobs_dict[job_num] = self.jobs_dict.get(job_num) - 1

        widget = self.jobs_tab_widget.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.jobs_tab_widget.removeTab(index)

    def event(self, event):
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.setWindowFlags(self.windowFlags() & ~Qt.Tool)
            self.tray_icon.show()
            return True
        else:
            return super(MainUI, self).event(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message", "Are you sure you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            self.tray_icon.show()
            self.hide()
            event.ignore()

    def restore_window(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.tray_icon.hide()
            self.showNormal()


class TabPage(QWidget):
    def __init__(self, job_dir):
        super(TabPage, self).__init__()
        self.job_dir = job_dir
        self.find_drone_dir()

        self.init_ui()

    def find_drone_dir(self):
        charlotte_drone_path = os.path.join(self.job_dir, "Drone")
        if os.path.isdir(charlotte_drone_path):
            self.drone_dir = charlotte_drone_path
            return

        nashville_drone_path = os.path.join(self.job_dir, *["Photographs", "Drone"])
        if os.path.isdir(nashville_drone_path):
            self.drone_dir = nashville_drone_path
            return

        self.drone_dir = ""

    def init_ui(self):
        self.create_controls()
        self.create_layout()

    def create_controls(self):
        # region Job Folders
        open_icon = QIcon(os.path.join(icon_path, "open.png"))

        self.base_job_folder_label = QLabel(self.job_dir)

        self.drone_folder_edit = QLineEdit(self.drone_dir)
        self.drone_folder_edit.setPlaceholderText("Drone Folder")

        self.drone_folder_button = QPushButton(open_icon, "")

        self.scans_folder_edit = QLineEdit()
        self.scans_folder_edit.setPlaceholderText("Scans Folder")

        self.scans_folder_button = QPushButton(open_icon, "")

        self.drawings_folder_edit = QLineEdit()
        self.drawings_folder_edit.setPlaceholderText("Drawings Folder")

        self.drawings_folder_button = QPushButton(open_icon, "")
        # endregion
        # region Job Controls
        self.open_job_folder_button = QPushButton("Open Job Folder")
        self.open_basecamp_page_button = QPushButton("Open Basecamp Page")
        self.open_basecamp_page_button.setDisabled(True)
        self.add_to_open_air_button = QPushButton("Add to Open Air")
        self.add_to_open_air_button.setDisabled(True)
        # endregion

        tool_icon = QIcon(os.path.join(icon_path, "tool.png"))
        # region SCENE
        self.scene_vehicle_button = QPushButton("Vehicle Scan")
        self.scene_vehicle_tool_button = QPushButton(tool_icon, "")
        self.scene_site_button = QPushButton("Site Scan")
        self.scene_site_tool_Button = QPushButton(tool_icon, "")
        self.scene_copy_folder_button = QPushButton("Copy Files to Job Folder")
        # endregion
        # region Pix4D
        self.pix4d_vehicle_button = QPushButton("Vehicle Drone Tool")
        self.pix4d_vehicle_tool_button = QPushButton(tool_icon, "")
        self.pix4d_site_button = QPushButton("Site Drone Tool")
        self.pix4d_site_tool_button = QPushButton(tool_icon, "")
        self.pix4d_copy_folder_button = QPushButton("Copy Files to Job Folder")
        # endregion
        # region Tools
        self.google_maps_stitcher_button = QPushButton("Google Maps Stitcher")
        # endregion

    def create_layout(self):
        main_layout = QHBoxLayout()

        first_column = QVBoxLayout()
        # region Job Folders
        job_folders_group = QGroupBox("Job Folders")
        job_folders_layout = QGridLayout()
        job_folders_layout.addWidget(self.base_job_folder_label, 0, 0)
        job_folders_layout.addWidget(self.drone_folder_edit, 1, 0)
        job_folders_layout.addWidget(self.drone_folder_button, 1, 1)
        job_folders_layout.addWidget(self.scans_folder_edit, 2, 0)
        job_folders_layout.addWidget(self.scans_folder_button, 2, 1)
        job_folders_layout.addWidget(self.drawings_folder_edit, 3, 0)
        job_folders_layout.addWidget(self.drawings_folder_button, 3, 1)
        job_folders_group.setLayout(job_folders_layout)
        first_column.addWidget(job_folders_group)
        # endregion
        # region Job Controls
        job_controls_group = QGroupBox("Job Controls")
        job_controls_layout = QVBoxLayout()
        job_controls_layout.addWidget(self.open_job_folder_button)
        job_controls_layout.addWidget(self.open_basecamp_page_button)
        job_controls_layout.addWidget(self.add_to_open_air_button)
        job_controls_group.setLayout(job_controls_layout)
        first_column.addWidget(job_controls_group)
        # endregion
        main_layout.addLayout(first_column)

        second_column = QVBoxLayout()
        # region SCENE
        scene_group = QGroupBox("SCENE")
        scene_layout = QVBoxLayout()

        scene_vehicle_layout = QHBoxLayout()
        scene_vehicle_layout.addWidget(self.scene_vehicle_button)
        scene_vehicle_layout.addWidget(self.scene_vehicle_tool_button)
        scene_vehicle_layout.setStretch(0, 1)
        scene_vehicle_layout.setStretch(1, 0)
        scene_layout.addLayout(scene_vehicle_layout)

        scene_site_layout = QHBoxLayout()
        scene_site_layout.addWidget(self.scene_site_button)
        scene_site_layout.addWidget(self.scene_site_tool_Button)
        scene_site_layout.setStretch(0, 1)
        scene_site_layout.setStretch(1, 0)
        scene_layout.addLayout(scene_site_layout)

        scene_layout.addWidget(self.scene_copy_folder_button)
        scene_group.setLayout(scene_layout)
        second_column.addWidget(scene_group)
        # endregion
        # region Pix4D
        pix4d_group = QGroupBox("Pix4D")
        pix4d_layout = QVBoxLayout()

        pix4d_vehicle_layout = QHBoxLayout()
        pix4d_vehicle_layout.addWidget(self.pix4d_vehicle_button)
        pix4d_vehicle_layout.addWidget(self.pix4d_vehicle_tool_button)
        pix4d_vehicle_layout.setStretch(0, 1)
        pix4d_vehicle_layout.setStretch(1, 0)
        pix4d_layout.addLayout(pix4d_vehicle_layout)

        pix4d_site_layout = QHBoxLayout()
        pix4d_site_layout.addWidget(self.pix4d_site_button)
        pix4d_site_layout.addWidget(self.pix4d_site_tool_button)
        pix4d_site_layout.setStretch(0, 1)
        pix4d_site_layout.setStretch(1, 0)
        pix4d_layout.addLayout(pix4d_site_layout)

        pix4d_layout.addWidget(self.pix4d_copy_folder_button)
        pix4d_group.setLayout(pix4d_layout)
        second_column.addWidget(pix4d_group)
        # endregion
        main_layout.addLayout(second_column)

        third_column = QVBoxLayout()
        # region Tools
        tools_group = QGroupBox("Tools")
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.google_maps_stitcher_button)
        tools_group.setLayout(tools_layout)
        third_column.addWidget(tools_group)
        # endregion
        main_layout.addLayout(third_column)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
