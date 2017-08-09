from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QWidget, QProgressDialog, QMessageBox, QSystemTrayIcon, QMenu, QApplication

from resources.resource_manager import resources
from views.gen.ui_main_view import Ui_main_view


class MainView(QWidget):
    @property
    def job_num(self):
        return int(self.ui.job_num_edit.text())

    def __init__(self, main_ctrl, settings_view):
        self.main_ctrl = main_ctrl
        self.settings_view = settings_view
        super(MainView, self).__init__()
        self.build_ui()
        self.init_systray()

    def build_ui(self):
        self.ui = Ui_main_view()
        self.ui.setupUi(self)

        # Modify UI
        self.ui.job_num_edit.setValidator(QIntValidator())

        # Tell controller that UI modifications are done
        self.main_ctrl.init_ui(self)

        # Signals/Slots
        self.ui.settings_btn.clicked.connect(self.settings_view.show)
        self.ui.jobs_tab_widget.tabCloseRequested.connect(self.main_ctrl.remove_job)

        self.ui.add_job_btn.clicked.connect(self.main_ctrl.fetch_job)
        self.ui.job_num_edit.returnPressed.connect(self.main_ctrl.fetch_job)

    def init_systray(self):
        systray_menu = QMenu()
        show_action = systray_menu.addAction("Show")
        show_action.triggered.connect(lambda: self.focus_window())
        quit_action = systray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit)
        systray_menu.setDefaultAction(show_action)

        self.systray_icon = QSystemTrayIcon(QIcon(resources["icons"]["icons8-Traffic Jam-80.png"]))
        self.systray_icon.setContextMenu(systray_menu)
        self.systray_icon.activated.connect(self.focus_window)
        self.systray_icon.show()

    def focus_job_num_edit(self):
        self.focus_window()
        self.ui.job_num_edit.selectAll()
        self.ui.job_num_edit.focusWidget()

    def open_current_job_folder(self):
        curr_tab = self.ui.jobs_tab_widget.currentWidget()
        if curr_tab is not None:
            curr_tab.job_ctrl.open_base_folder()

    def focus_window(self, reason=None):
        if reason != QSystemTrayIcon.DoubleClick and reason is not None:
            return

        self.showMinimized()
        self.showNormal()

    def quit(self):
        self.systray_icon.hide()
        self.systray_icon.deleteLater()
        QApplication.quit()

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def add_tab(self, tab, name):
        self.ui.jobs_tab_widget.insertTab(0, tab, name)
        self.ui.jobs_tab_widget.setCurrentIndex(0)

    def remove_tab(self, index):
        tab = self.ui.jobs_tab_widget.widget(index)
        if tab:
            tab.deleteLater()
        self.ui.jobs_tab_widget.removeTab(index)

    def show_job_already_exists_dialog(self):
        QMessageBox.warning(self, "Already Exists", "The job already exists.", QMessageBox.Ok, QMessageBox.NoButton)

    def show_job_fetch_progress_dialog(self, max):
        self.job_fetch_progress_dialog = QProgressDialog("Searching for job folder...", "Cancel", 0, 100, self)
        self.job_fetch_progress_dialog.setWindowTitle("Searching...")
        self.job_fetch_progress_dialog.setMaximum(max)
        self.job_fetch_progress_dialog.setModal(True)
        self.job_fetch_progress_dialog.canceled.connect(self.main_ctrl.cancel_job_fetch)
        self.job_fetch_progress_dialog.show()

    def update_job_fetch_progress_dialog(self, progress):
        self.job_fetch_progress_dialog.setValue(progress)

    def close_job_fetch_progress_dialog(self):
        self.job_fetch_progress_dialog.hide()
        self.job_fetch_progress_dialog.deleteLater()

    def show_job_not_found_dialog(self):
        response = QMessageBox.warning(self, "Not Found",
                                       "Could not find job. Would you like to open the job anyway?",
                                       QMessageBox.Yes, QMessageBox.No)
        return response == QMessageBox.Yes
