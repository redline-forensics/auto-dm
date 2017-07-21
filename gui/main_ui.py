import os.path
import os.path

from PySide.QtGui import QWidget, QSystemTrayIcon, QIcon, QApplication, QMenu, QLineEdit, QIntValidator, QPushButton, \
    QTabWidget, QHBoxLayout, QVBoxLayout, QMessageBox, QLabel, QFileDialog, QGroupBox, QGridLayout, QDesktopServices

from bots import pix_4d_bot
from custom_widgets import GoogleMapsStitcherDialog
from utils import hotkeys, basecamp
from utils.job_dir_finder import *
from utils.job_type import JobType
from resources.resource_manager import resources


class MainUI(QWidget):
    def __init__(self):
        super(MainUI, self).__init__()
        self.jobs_dict = dict()
        self.init_ui()
        self.init_hotkeys()

    def init_ui(self):
        main_icon = QIcon(resources['icons']['main.png'])
        self.init_systray(main_icon)
        self.setWindowTitle("AutoDM")
        self.setWindowIcon(main_icon)
        self.resize(660, 362)

        self.create_controls()
        self.create_layout()
        self.make_connections()

        self.show()

    def init_systray(self, icon):
        self.tray_icon = QSystemTrayIcon(icon)

        menu = QMenu()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.restore_window)
        menu.setDefaultAction(show_action)
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit)

        self.tray_icon.setContextMenu(menu)

    def quit(self):
        hotkeys.unhook()
        QApplication.quit()

    def init_hotkeys(self):
        # Format: Hotkeys.add_hotkey("J", ["Lcontrol", "Lwin"], self.woi)
        hotkeys.add_hotkey("J", ["Lcontrol", "Lmenu"], self.add_job_hotkey)
        hotkeys.add_hotkey("O", ["Lcontrol", "Lmenu"], self.restore_window)
        hotkeys.add_hotkey("M", ["Lcontrol", "Lmenu"], self.showMinimized)
        hotkeys.add_hotkey("T", ["Lcontrol", "Lmenu"], self.test)

    def test(self):
        self.restore_window()
        test_tab = self.add_job(4086, "N:\\J4086 Darby Trucking")
        if test_tab is not None:
            test_tab.run_pix4d_bot_site()

    def add_job_hotkey(self):
        self.showMinimized()
        self.restore_window()
        self.job_num_edit.setFocus()
        self.job_num_edit.selectAll()

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

        job_dir_finder = FindJobDir(job_num)
        job_dir_finder.finished.connect(self.add_job)
        try:
            job_dir_finder.start()
        except IOError:
            QMessageBox.critical(self, "J{:d} Not Found".format(job_num),
                                 "Could not find J{:d} on the server".format(job_num))

    def add_job(self, num, job_dir):
        if self.jobs_dict.get(num, 0) > 0:
            flags = QMessageBox.StandardButton.Yes
            flags |= QMessageBox.StandardButton.No
            response = QMessageBox.warning(self, "J{:d} Already Open".format(num),
                                           "J{:d} is already open. Open a new instance anyway?".format(num), flags)
            if response == QMessageBox.StandardButton.No:
                return

        self.jobs_dict[num] = self.jobs_dict.get(num, 0) + 1
        tab_page = TabPage(num, job_dir, self)
        self.jobs_tab_widget.insertTab(0, tab_page, "J" + str(num))
        self.jobs_tab_widget.setCurrentIndex(0)
        return tab_page

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
            hotkeys.unhook()
            event.accept()
        else:
            self.tray_icon.show()
            self.hide()
            event.ignore()

    def restore_window(self, reason=None):
        if reason == QSystemTrayIcon.DoubleClick or reason is None:
            self.tray_icon.hide()
            self.showNormal()
            self.activateWindow()


class TabPage(QWidget, object):
    # region job_dir
    @property
    def job_dir(self):
        return self.__job_dir

    @job_dir.setter
    def job_dir(self, value):
        self.__job_dir = value
        self.base_job_folder.setText(value)

    # endregion
    # region drone_dir
    @property
    def drone_dir(self):
        return self.__drone_dir

    @drone_dir.setter
    def drone_dir(self, value):
        self.__drone_dir = value

        if self.drone_folder_edit.text() != value:
            self.drone_folder_edit.setText(value)

        if os.path.isdir(value):
            self.drone_folder_open_button.setVisible(True)
        else:
            self.drone_folder_open_button.setVisible(False)

    # endregion
    # region scans_dir
    @property
    def scans_dir(self):
        return self.__scans_dir

    @scans_dir.setter
    def scans_dir(self, value):
        self.__scans_dir = value

        if self.scans_folder_edit.text() != value:
            self.scans_folder_edit.setText(value)

        if os.path.isdir(value):
            self.scans_folder_open_button.setVisible(True)
        else:
            self.scans_folder_open_button.setVisible(False)

    # endregion
    # region assets_dir
    @property
    def assets_dir(self):
        return self.__assets_dir

    @assets_dir.setter
    def assets_dir(self, value):
        self.__assets_dir = value

        if self.assets_folder_edit.text() != value:
            self.assets_folder_edit.setText(value)

        if value == "":
            self.assets_folder_add_button.setVisible(True)
        else:
            if os.path.isdir(value):
                self.assets_folder_open_button.setVisible(True)
            else:
                self.assets_folder_open_button.setVisible(False)
            self.assets_folder_add_button.setVisible(False)

    # endregion

    def __init__(self, job_num, job_dir, main_window):
        super(TabPage, self).__init__()
        self.basecamp_url = basecamp.get_basecamp_page(job_num)
        self.init_bots()
        self.init_ui()
        self.find_dirs(job_dir)
        self.job_num = job_num
        self.main_window = main_window

    def init_bots(self):
        self.pix4d_bot = None

    def init_ui(self):
        self.create_controls()
        self.create_layout()
        self.make_connections()

    def create_controls(self):
        # region Job Folders
        edit_icon = QIcon(resources['icons']['edit.png'])
        open_icon = QIcon(resources['icons']['open.png'])

        self.base_job_folder_label = QLabel("Base:")
        self.base_job_folder = QLineEdit()
        self.base_job_folder.setReadOnly(True)
        self.base_job_folder.setFrame(False)

        folder_str = "Folder"
        drone_str = "Drone"
        self.drone_folder_label = QLabel("{}:".format(drone_str))
        self.drone_folder_edit = QLineEdit()
        self.drone_folder_edit.setPlaceholderText("{} {}".format(drone_str, folder_str))
        self.drone_folder_edit_button = QPushButton(edit_icon, "")
        self.drone_folder_open_button = QPushButton(open_icon, "")

        scans_str = "Scans"
        self.scans_folder_label = QLabel("{}:".format(scans_str))
        self.scans_folder_edit = QLineEdit()
        self.scans_folder_edit.setPlaceholderText("{} {}".format(scans_str, folder_str))
        self.scans_folder_edit_button = QPushButton(edit_icon, "")
        self.scans_folder_open_button = QPushButton(open_icon, "")

        assets_str = "Assets"
        self.assets_folder_label = QLabel("{}:".format(assets_str))
        self.assets_folder_edit = QLineEdit()
        self.assets_folder_edit.setPlaceholderText("{} {}".format(assets_str, folder_str))
        self.assets_folder_edit_button = QPushButton(edit_icon, "")
        self.assets_folder_open_button = QPushButton(open_icon, "")
        self.assets_folder_add_button = QPushButton(QIcon(resources['icons']['new_dir.png']), "")
        # endregion
        # region Job Controls
        self.open_job_folder_button = QPushButton("Open Job Folder")
        self.open_basecamp_page_button = QPushButton("Open Basecamp Page")
        if self.basecamp_url is None:
            self.open_basecamp_page_button.setDisabled(True)
        self.add_to_open_air_button = QPushButton("Add to Open Air")
        self.add_to_open_air_button.setDisabled(True)
        # endregion

        tool_icon = QIcon(resources['icons']['tool.png'])
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
        job_folders_layout.addWidget(self.base_job_folder, 0, 1)

        job_folders_layout.addWidget(self.drone_folder_label, 1, 0)
        drone_folder_layout = QHBoxLayout()
        drone_folder_layout.addWidget(self.drone_folder_edit)
        drone_folder_layout.addWidget(self.drone_folder_edit_button)
        drone_folder_layout.addWidget(self.drone_folder_open_button)
        drone_folder_layout.setStretch(0, 1)
        drone_folder_layout.setStretch(1, 0)
        job_folders_layout.addLayout(drone_folder_layout, 1, 1)

        job_folders_layout.addWidget(self.scans_folder_label, 2, 0)
        scans_folder_layout = QHBoxLayout()
        scans_folder_layout.addWidget(self.scans_folder_edit)
        scans_folder_layout.addWidget(self.scans_folder_edit_button)
        scans_folder_layout.addWidget(self.scans_folder_open_button)
        scans_folder_layout.setStretch(0, 1)
        scans_folder_layout.setStretch(1, 0)
        job_folders_layout.addLayout(scans_folder_layout, 2, 1)

        job_folders_layout.addWidget(self.assets_folder_label, 3, 0)
        assets_folder_layout = QHBoxLayout()
        assets_folder_layout.addWidget(self.assets_folder_edit)
        assets_folder_layout.addWidget(self.assets_folder_edit_button)
        assets_folder_layout.addWidget(self.assets_folder_open_button)
        assets_folder_layout.addWidget(self.assets_folder_add_button)
        assets_folder_layout.setStretch(0, 1)
        assets_folder_layout.setStretch(1, 0)
        assets_folder_layout.setStretch(2, 0)
        job_folders_layout.addLayout(assets_folder_layout, 3, 1)

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

        main_layout.setStretch(0, 100)
        main_layout.setStretch(1, 75)
        main_layout.setStretch(2, 75)

        self.setLayout(main_layout)

    def make_connections(self):
        self.drone_folder_edit.returnPressed.connect(lambda: setattr(self, "drone_dir", self.drone_folder_edit.text()))
        self.scans_folder_edit.returnPressed.connect(lambda: setattr(self, "scans_dir", self.scans_folder_edit.text()))
        self.assets_folder_edit.returnPressed.connect(
            lambda: setattr(self, "assets_dir", self.assets_folder_edit.text()))

        self.drone_folder_edit_button.clicked.connect(
            lambda: setattr(self, "drone_dir", self.choose_dir(self.drone_dir)))
        self.scans_folder_edit_button.clicked.connect(
            lambda: setattr(self, "scans_dir", self.choose_dir(self.scans_dir)))
        self.assets_folder_edit_button.clicked.connect(
            lambda: setattr(self, "assets_dir", self.choose_dir(self.assets_dir)))

        self.assets_folder_add_button.clicked.connect(self.create_assets_dir)

        self.drone_folder_open_button.clicked.connect(lambda: self.open_folder(self.drone_dir))
        self.scans_folder_open_button.clicked.connect(lambda: self.open_folder(self.scans_dir))
        self.assets_folder_open_button.clicked.connect(lambda: self.open_folder(self.assets_dir))

        self.open_job_folder_button.clicked.connect(lambda: self.open_folder(self.job_dir))
        self.open_basecamp_page_button.clicked.connect(self.open_basecamp_page)

        self.pix4d_site_button.clicked.connect(self.run_pix4d_bot_site)
        self.pix4d_site_tool_button.clicked.connect(self.show_pix4d_site_tool_window)

        self.google_maps_stitcher_button.clicked.connect(self.show_google_maps_stitcher)

    def find_dirs(self, job_dir):
        def find_drone_dir():
            charlotte_drone_path = os.path.join(self.job_dir, "Drone")
            if os.path.isdir(charlotte_drone_path):
                self.drone_dir = charlotte_drone_path
                return

            nashville_drone_path = os.path.join(self.job_dir, *["Photographs", "Drone"])
            if os.path.isdir(nashville_drone_path):
                self.drone_dir = nashville_drone_path
                return

            self.drone_dir = ""

        def find_scans_dir():
            charlotte_scans_path = os.path.join(self.job_dir, "Scans")
            if os.path.isdir(charlotte_scans_path):
                self.scans_dir = charlotte_scans_path
                return

            nashville_scans_path_0 = os.path.join(self.job_dir, "Scan Data")
            if os.path.isdir(nashville_scans_path_0):
                self.scans_dir = nashville_scans_path_0
                return

            nashville_scans_path_1 = os.path.join(self.job_dir, "Scanned Data")
            if os.path.isdir(nashville_scans_path_1):
                self.scans_dir = nashville_scans_path_1
                return

            self.scans_dir = ""

        def find_assets_dir():
            charlotte_drawings_path = os.path.join(self.job_dir, "Drawings")
            charlotte_drawing_path = os.path.join(self.job_dir, "Drawing")
            if os.path.isdir(charlotte_drawings_path):
                drawings_path = charlotte_drawings_path
            elif os.path.isdir(charlotte_drawing_path):
                drawings_path = charlotte_drawing_path
            else:
                self.assets_dir = ""
                return

            charlotte_assets_path = os.path.join(drawings_path, "Assets")
            charlotte_asset_path = os.path.join(drawings_path, "Asset")
            if os.path.isdir(charlotte_assets_path):
                self.assets_dir = charlotte_assets_path
            elif os.path.isdir(charlotte_asset_path):
                self.assets_dir = charlotte_asset_path
            else:
                self.assets_dir = drawings_path
                return

        self.job_dir = job_dir
        find_drone_dir()
        find_scans_dir()
        find_assets_dir()

    def create_assets_dir(self):
        charlotte_drawings_path = os.path.join(self.job_dir, "Drawings")
        charlotte_drawing_path = os.path.join(self.job_dir, "Drawing")
        if os.path.isdir(charlotte_drawings_path):
            drawings_path = charlotte_drawings_path
        elif os.path.isdir(charlotte_drawing_path):
            drawings_path = charlotte_drawing_path
        else:
            os.makedirs(charlotte_drawings_path)
            drawings_path = charlotte_drawings_path

        charlotte_assets_path = os.path.join(drawings_path, "Assets")
        charlotte_asset_path = os.path.join(drawings_path, "Asset")
        if os.path.isdir(charlotte_assets_path):
            self.assets_dir = charlotte_assets_path
        elif os.path.isdir(charlotte_asset_path):
            self.assets_dir = charlotte_asset_path
        else:
            os.makedirs(charlotte_assets_path)
            self.assets_dir = charlotte_assets_path

    def choose_dir(self, dir_var):
        if dir_var == self.drone_dir:
            dir_str = "Drone"
        elif dir_var == self.scans_dir:
            dir_str = "Scans"
        elif dir_var == self.assets_dir:
            dir_str = "Assets"
        else:
            dir_str = ""

        choose_dir = QFileDialog.getExistingDirectory(self, "Choose {} Folder".format(dir_str), self.job_dir)
        if choose_dir == "":
            return dir_var
        return choose_dir

    @staticmethod
    def open_folder(folder):
        QDesktopServices.openUrl(QUrl("file:{}".format(folder), QUrl.TolerantMode))

    def open_basecamp_page(self):
        QDesktopServices.openUrl(QUrl(self.basecamp_url))

    def run_pix4d_bot_site(self):
        self.pix4d_bot = pix_4d_bot.Bot(self, JobType["SITE"])

    def show_pix4d_site_tool_window(self):
        self.pix4d_bot = pix_4d_bot.Bot(self, JobType["SITE"], standalone=True)

    def show_google_maps_stitcher(self):
        self.google_maps_stitcher_dialog = GoogleMapsStitcherDialog(self.assets_dir)
        self.google_maps_stitcher_dialog.show()
