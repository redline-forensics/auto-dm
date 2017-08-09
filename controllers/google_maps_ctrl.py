import os

from controllers.google_maps_earth_ctrl import GoogleMapsEarthController
from utils.desktop_utils import open_path


class GoogleMapsController(GoogleMapsEarthController):
    def __init__(self, google_maps_model):
        super(GoogleMapsController, self).__init__(google_maps_model)

        self.google_maps_earth_model.begin_stitching.connect(self.on_begin_image_creation)
        self.google_maps_earth_model.update_progress.connect(self.on_image_creation_progress_update)
        self.google_maps_earth_model.done_stitching.connect(self.on_image_created)

    def init_ui(self, google_maps_view):
        super(GoogleMapsController, self).init_ui(google_maps_view)

    def create_image(self):
        point_a, point_b = self.google_maps_earth_view.rectangle
        self.google_maps_earth_model.create_image(point_a, point_b, self.google_maps_earth_view.interval)

    def cancel_image_create(self):
        self.google_maps_earth_model.cancel_image_create()

    def on_begin_image_creation(self, max):
        self.google_maps_earth_view.show_stitching_progress_dialog(max)

    def on_image_creation_progress_update(self, progress):
        self.google_maps_earth_view.update_stitching_progress_dialog(progress)

    def on_image_created(self, image, tfw):
        self.google_maps_earth_view.close_stitching_progress_dialog()

        image_file = None
        while not image_file:
            image_file = self.google_maps_earth_view.show_image_save_dialog(self.google_maps_earth_model.assets_folder)
            if not image_file:
                discard = self.google_maps_earth_view.show_discard_confirmation_dialog()
                if discard:
                    return
        image.save(image_file)

        tfw_file = os.path.splitext(image_file)[0] + ".tfw"
        with open(tfw_file, "w") as f:
            f.write(tfw)

        open_path(image_file)
