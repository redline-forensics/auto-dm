import sys

from PySide.QtGui import QApplication

from gui.main_ui import MainUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainUI()
    sys.exit(app.exec_())
