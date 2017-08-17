from controllers.job_ctrl import JobController
from models.job_model import JobModel
from views.job_view import JobView


class MainController(object):
    def __init__(self, main_model):
        self.main_view = None
        self.main_model = main_model

        self.main_model.begin_job_fetch.connect(self.on_begin_job_fetch)
        self.main_model.update_job_fetch_progress.connect(self.on_job_fetch_update)
        self.main_model.fetched_job.connect(self.on_fetched_job)

    def init_ui(self, main_view):
        self.main_view = main_view
        self.init_hotkeys()

    def init_hotkeys(self):
        self.main_model.hotkey_model.add_hotkey(["Lcontrol", "Lmenu", "J"], self.main_view.focus_job_num_edit)
        self.main_model.hotkey_model.add_hotkey(["Lcontrol", "Lmenu", "O"], self.main_view.open_current_job_folder)
        self.main_model.hotkey_model.add_hotkey(["Lcontrol", "Lmenu", "B"], self.main_view.open_current_job_basecamp)
        self.main_model.hotkey_model.start_detection()

    def fetch_job(self):
        job_num = self.main_view.job_num
        if self.main_model.job_exists(job_num):
            self.main_view.show_job_already_exists_dialog()
            return

        self.main_model.fetch_job(job_num)

    def cancel_job_fetch(self):
        self.main_model.cancel_job_fetch()

    def on_begin_job_fetch(self, max):
        self.main_view.show_job_fetch_progress_dialog(max)

    def on_job_fetch_update(self, progress):
        self.main_view.update_job_fetch_progress_dialog(progress)

    def on_fetched_job(self, job_num, base_folder):
        job = JobModel(job_num,
                       base_folder,
                       self.main_model.settings_model.basecamp_email,
                       self.main_model.settings_model.basecamp_password,
                       self.main_model.settings_model.google_maps_js_api_key,
                       self.main_model.settings_model.google_maps_static_api_key,
                       self.main_model.settings_model.google_earth_exe_path,
                       self.main_model.settings_model.scene_exe_path)
        self.main_model.jobs[job.job_num] = job
        found = bool(job.base_folder)

        self.main_view.close_job_fetch_progress_dialog()

        if not found:
            open_anyway = self.main_view.show_job_not_found_dialog()
            if not open_anyway:
                return
        job_view = JobView(JobController(job))
        job_view.request_minimize.connect(self.main_view.close)
        self.main_view.add_tab(job_view, job.job_name)

    def remove_job(self, index):
        job_num = int(self.main_view.ui.jobs_tab_widget.tabText(index)[1:])
        self.main_model.jobs.pop(job_num, None)
        self.main_view.remove_tab(index)
