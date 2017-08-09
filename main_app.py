import sys

from PyQt5.QtWidgets import QApplication

from controllers.main_ctrl import MainController
from controllers.settings_ctrl import SettingsController
from models.hotkey_model import HotkeyModel
from models.main_model import MainModel
from models.settings_model import SettingsModel
from views.main_view import MainView
from views.settings_view import SettingsView


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        settings_model = SettingsModel()
        settings_ctrl = SettingsController(settings_model)
        settings_view = SettingsView(settings_ctrl)

        hotkey_model = HotkeyModel()

        main_model = MainModel(settings_model, hotkey_model)
        main_ctrl = MainController(main_model)
        self.main_view = MainView(main_ctrl, settings_view)
        self.main_view.show()


if __name__ == "__main__":
    sys._excepthook = sys.excepthook


    def my_exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = my_exception_hook

    app = App(sys.argv)
    sys.exit(app.exec_())
