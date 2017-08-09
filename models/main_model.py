import ntpath
import os

from PyQt5.QtCore import QThread, pyqtSignal

from models.model import Model
from resources import paths


class MainModel(Model):
    begin_job_fetch = pyqtSignal(int)
    update_job_fetch_progress = pyqtSignal(int)
    fetched_job = pyqtSignal(int, str)

    def __init__(self, settings_model, hotkey_model):
        self.settings_model = settings_model
        self.hotkey_model = hotkey_model
        super(MainModel, self).__init__()
        self.jobs = {}
        self.job_fetcher = JobFetcher()
        self.job_fetcher.begin_fetch.connect(self.begin_job_fetch.emit)
        self.job_fetcher.update_progress.connect(self.update_job_fetch_progress.emit)
        self.job_fetcher.fetched_job.connect(self.fetched_job.emit)

    def fetch_job(self, job_num):
        self.job_fetcher.start(job_num)

    def cancel_job_fetch(self):
        self.job_fetcher.cancel()

    def job_exists(self, job_num):
        return job_num in self.jobs


class JobFetcher(QThread):
    begin_fetch = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    fetched_job = pyqtSignal(int, str)

    def start(self, job_num, priority=None):
        self.job_num = job_num
        self.canceled = False
        if priority is None:
            super(JobFetcher, self).start()
        else:
            super(JobFetcher, self).start(priority)

    def cancel(self):
        self.canceled = True

    def run(self):
        dirs = [os.path.join(paths.dv_jobs_path, path) for path in os.listdir(paths.dv_jobs_path)] \
               + [os.path.join(paths.nashville_path, path) for path in os.listdir(paths.nashville_path)]
        self.begin_fetch.emit(len(dirs))
        base_folder = ""
        for i, dir_ in enumerate(dirs):
            if self.canceled:
                return

            self.update_progress.emit(i)
            if self.matches(dir_):
                base_folder = dir_
                break
        self.fetched_job.emit(self.job_num, base_folder)

    def matches(self, path):
        if not os.path.isdir(path):
            return False
        if not ntpath.basename(path).startswith("J" + str(self.job_num)):
            return False
        return True
