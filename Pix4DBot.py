import os
import re
import warnings
import Preferences

from PySide.QtGui import QMessageBox
from pywinauto import Application

warnings.filterwarnings("error")


def run(parent):
    program_files_32 = os.environ["ProgramW6432"]
    program_files_64 = os.environ["ProgramFiles(x86)"]

    pix4d_exe_32 = os.path.join(program_files_32, *["Pix4Dmapper", "pix4dmapper.exe"])
    pix4d_exe_64 = os.path.join(program_files_64, *["Pix4Dmapper", "pix4dmapper.exe"])

    if os.path.isfile(pix4d_exe_64):
        pix4d_exe = pix4d_exe_64
    elif os.path.isfile(pix4d_exe_32):
        pix4d_exe = pix4d_exe_32
    else:
        raise IOError("Pix4D installation not found")
        # TODO: Manual entry of Pix4D location

    try:
        app = Application().start(pix4d_exe)
    except UserWarning as user_warning:
        warning_nums = re.findall(r"\d+", str(user_warning))

        pix4d_bitness = int(warning_nums[0])
        python_bitness = int(warning_nums[1])

        flags = QMessageBox.StandardButton.Yes
        flags |= QMessageBox.StandardButton.No
        response = QMessageBox.warning(parent, "Warning",
                                       "Attempting to start {:d}-bit Pix4D using {:d}-bit Python. Unexpected behavior "
                                       "may occur. Proceed?".format(pix4d_bitness, python_bitness),
                                       flags)
        if response == QMessageBox.StandardButton.Yes:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                app = Application().start(pix4d_exe)
        else:
            return

    print(app)
