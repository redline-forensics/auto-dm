import os

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


def open_url(url):
    QDesktopServices.openUrl(QUrl(url, QUrl.TolerantMode))


def open_path(path):
    QDesktopServices.openUrl(QUrl("file:{}".format(path), QUrl.TolerantMode))


def get_exe_path(path_from_program_files):
    program_files_32 = os.environ["ProgramW6432"]
    program_files_64 = os.environ["ProgramFiles(x86)"]

    exe_32 = os.path.join(program_files_32, path_from_program_files)
    exe_64 = os.path.join(program_files_64, path_from_program_files)

    if os.path.isfile(exe_64):
        return exe_64
    elif os.path.isfile(exe_32):
        return exe_32
    return None
