from controllers.google_maps_earth_ctrl import GoogleMapsEarthController
from utils.desktop_utils import open_path


class GoogleEarthController(GoogleMapsEarthController):
    def __init__(self, google_maps_model):
        super(GoogleEarthController, self).__init__(google_maps_model)

        self.google_maps_earth_model.starting_captures.connect(self.on_starting_captures)
        self.google_maps_earth_model.update_progress.connect(self.on_progress_update)
        self.google_maps_earth_model.finished_captures.connect(self.on_finished_captures)

    def init_ui(self, google_maps_view):
        super(GoogleEarthController, self).init_ui(google_maps_view)

    def get_user_exe_path(self):
        return self.google_maps_earth_view.show_google_earth_exe_picker()

    def start_capturing(self):
        point_a, point_b = self.google_maps_earth_view.map_rectangle
        self.google_maps_earth_model.start_capturing(point_a, point_b, self.google_maps_earth_view.overlap,
                                                     self.google_maps_earth_view.interval)
        self.google_maps_earth_view.minimize()

    def cancel_captures(self):
        self.google_maps_earth_model.cancel_captures()

    def on_starting_captures(self, start_time, end_time):
        self.google_maps_earth_view.show_capture_progress_dialog(start_time, end_time)

    def on_progress_update(self, progress):
        self.google_maps_earth_view.update_capture_progress_dialog(progress)

    def on_finished_captures(self):
        self.google_maps_earth_view.close_capture_progress_dialog()
        open_path(self.google_maps_earth_model.screenshots_folder)
