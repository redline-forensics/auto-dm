from resources.resource_manager import resources


class GoogleMapsEarthController(object):
    def __init__(self, google_maps_earth_model):
        self.google_maps_earth_view = None
        self.google_maps_earth_model = google_maps_earth_model

    def init_ui(self, google_maps_earth_view):
        self.google_maps_earth_view = google_maps_earth_view

        with open(resources["html"]["google_map.html"], "r") as f:
            self.google_maps_earth_view.ui.web_view.setHtml(
                f.read().format(api_key=self.google_maps_earth_model.js_api_key))

    def move_map(self):
        new_coords = (self.google_maps_earth_view.latitude, self.google_maps_earth_view.longitude)
        self.google_maps_earth_view.map_center = new_coords
        self.google_maps_earth_view.map_rectangle = new_coords
