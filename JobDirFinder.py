import multiprocessing
import ntpath
import os.path

from PySide.QtCore import *

dv_jobs_path = "\\\\server1\\DV_Production\\DV_Jobs"
nashville_path = "\\\\Render-server\\r\\Nashville"


class FindJobDir(QObject):
    finished = Signal(int, str)

    def __init__(self, num, parent=None):
        super(FindJobDir, self).__init__(parent)

        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(multiprocessing.cpu_count())
        self.num = num

        self.is_found = False

    def start(self):
        for job_dir in os.listdir(dv_jobs_path):
            self.add_worker(dv_jobs_path, job_dir)
        for job_dir in os.listdir(nashville_path):
            self.add_worker(nashville_path, job_dir)

        self.pool.waitForDone()
        if not self.is_found:
            raise IOError("Could not find job directory")

    def add_worker(self, base_path, job_dir):
        check_job_worker = CheckJobWorker(self.num, os.path.join(base_path, job_dir), self.is_found, self)
        check_job_worker.found.connect(lambda job_path: self.found_dir(job_path))
        self.pool.start(check_job_worker)

    def found_dir(self, job_path):
        self.is_found = True
        self.finished.emit(self.num, job_path)


class CheckJobWorker(QObject, QRunnable):
    found = Signal(str)

    def __init__(self, num, job_path, is_found, parent=None):
        QObject.__init__(self, parent)
        QRunnable.__init__(self, parent)
        self.num = num
        self.job_path = job_path
        self.is_found = is_found
        self.parent = parent

    def run(self):
        if self.is_found:
            return

        if not os.path.isdir(self.job_path):
            return

        if not ntpath.basename(self.job_path).startswith("J" + str(self.num)):
            return

        self.parent.is_found = True
        self.found.emit(self.job_path)
