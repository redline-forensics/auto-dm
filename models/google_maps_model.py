import math
import os
import time
from io import BytesIO

import requests
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from models.model import Model
from utils.map_utils import lon_to_px, px_to_deg, earth_pix, pix_rad, lat_to_px, calculate_dimensions_in_ft, \
    points_to_coords

tile_width = 640
tile_height = 616
url_base = "https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&center={lat},{lon}&zoom={zoom}" \
           "&size={tile_pix}x{tile_pix}&key={key}"
zoom = 21


class GoogleMapsModel(Model):
    begin_stitching = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    done_stitching = pyqtSignal(object, str)

    def __init__(self, assets_folder, js_api_key, static_api_key):
        self.assets_folder = assets_folder
        self.js_api_key = js_api_key
        self.static_api_key = static_api_key
        super(GoogleMapsModel, self).__init__()

        self.image = None

    def create_image(self, point_a, point_b, interval):
        self.google_maps_stitcher = GoogleMapsStitcher(self.static_api_key, point_a, point_b, interval)
        self.google_maps_stitcher.begin_stitching.connect(self.begin_stitching.emit)
        self.google_maps_stitcher.update_progress.connect(self.update_progress.emit)
        self.google_maps_stitcher.done_stitching.connect(self.on_done_stitching)
        self.google_maps_stitcher.start()

    def cancel_image_create(self):
        self.google_maps_stitcher.cancel()

    def on_done_stitching(self, image, tfw):
        self.google_maps_stitcher = None
        self.done_stitching.emit(image, tfw)


class GoogleMapsStitcher(QThread):
    begin_stitching = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    done_stitching = pyqtSignal(object, str)

    def __init__(self, static_api_key, point_a, point_b, interval):
        self.static_api_key = static_api_key
        self.lat, self.lon = points_to_coords(point_a, point_b)
        self.interval = interval
        super(GoogleMapsStitcher, self).__init__()
        self.canceled = False

    def run(self):
        def generate_tfw():
            width_px, height_px = image.size
            width, height = calculate_dimensions_in_ft(self.lat, self.lon, width_px, height_px)
            return "{}\n{}\n{}\n{}\n{}\n{}".format(
                str(abs(float(width) / width_px)),
                0,
                0,
                str(-abs(float(height) / height_px)),
                0,
                0
            )

        num_tiles_width = int(math.ceil(abs(lon_to_px(self.lon[1]) - lon_to_px(self.lon[0])) / tile_width))
        num_tiles_height = int(math.ceil(abs(lat_to_px(self.lat[1]) - lat_to_px(self.lat[0])) / tile_height))
        num_tiles = num_tiles_width * num_tiles_height
        self.begin_stitching.emit(num_tiles)

        image = Image.new("RGB", (num_tiles_width * tile_width, num_tiles_height * tile_height))

        cur_tile = 0
        for i in range(num_tiles_width):
            lon = self.pix_to_lon(i)
            for j in range(num_tiles_height):
                cur_tile += 1
                self.update_progress.emit(cur_tile)

                lat = self.pix_to_lat(j)
                tile = self.fetch_tile(lat, lon)
                image.paste(tile, (i * tile_width, j * tile_height))
        self.done_stitching.emit(image, generate_tfw())

    def fetch_tile(self, lat, lon):
        file_name = os.path.join("map_stitch_cache", "{}_{}.jpg".format(lat, lon))
        if os.path.isfile(file_name):
            return Image.open(file_name)

        url = url_base.format(lat=lat, lon=lon, zoom=zoom, tile_pix=tile_width, key=self.static_api_key)
        r = requests.get(url)
        tile = Image.open(BytesIO(r.content)).convert("RGB")
        if not os.path.exists("map_stitch_cache"):
            os.mkdir("map_stitch_cache")
        tile.save(file_name)
        time.sleep(self.interval)
        return tile

    def cancel(self):
        self.canceled = True

    def pix_to_lon(self, n):
        return math.degrees(
            (lon_to_px(self.lon[0]) + px_to_deg(n * tile_width, zoom) - earth_pix) / pix_rad
        )

    def pix_to_lat(self, n):
        return math.degrees(math.pi / 2 - 2 * math.atan(
            math.exp(
                (lat_to_px(self.lat[0]) + px_to_deg(n * tile_height, zoom) - earth_pix) / pix_rad
            )
        ))
