import cStringIO
import math
import os
import time
import urllib

from PIL import Image
from PySide.QtCore import QThread, Signal

from prefs import preferences

api_key = preferences.get_google_maps_static_api_key()
tile_width = 640
tile_height = 616
url_base = "https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&center={lat},{lon}&zoom={zoom}" \
           "&size={tile_pix}x{tile_pix}&key={key}"
earth_pix = 268435456
pix_rad = earth_pix / math.pi
sleep_time = 3.456
zoom = 21


def lat_to_pix(lat):
    sin_lat = math.sin(math.radians(lat))
    return earth_pix - pix_rad * math.log((1 + sin_lat) / (1 - sin_lat)) / 2


def pix_to_lat(pix):
    r = math.exp(2 * earth_pix / pix_rad)
    x = math.exp(2 * pix / pix_rad)
    return math.degrees(math.asin((r - x) / (r + x)))


def lon_to_pix(lon):
    return earth_pix + lon * math.radians(pix_rad)


def pix_to_lon(pix):
    return math.degrees((pix - earth_pix) / pix_rad)


def _pixels_to_degrees(pixels):
    return pixels * 2 ** (21 - zoom)


def fetch_tile(lat, lon):
    filename = os.path.join("map_stitch_cache", "{}_{}.jpg".format(lat, lon))
    if os.path.isfile(filename):
        tile = Image.open(filename)
    else:
        url = url_base.format(lat=lat, lon=lon, zoom=zoom, tile_pix=tile_width, key=api_key)
        result = urllib.urlopen(url).read()
        tile = Image.open(cStringIO.StringIO(result)).convert("RGB")
        if not os.path.exists("map_stitch_cache"):
            os.mkdir("map_stitch_cache")
        tile.save(filename)
        time.sleep(sleep_time)
    return tile


class MapStitcher(QThread):
    update_progress = Signal(int, int)
    image_created = Signal(object, list, list)
    memory_error = Signal()

    def start(self, coord_a, coord_b):
        self.set_coords(coord_a, coord_b)
        super(MapStitcher, self).start()

    def run(self):
        num_tiles_width = int(math.ceil((lon_to_pix(self.lon[1]) - lon_to_pix(self.lon[0])) / tile_width))
        num_tiles_height = int(math.ceil((lat_to_pix(self.lat[1]) - lat_to_pix(self.lat[0])) / tile_height))
        try:
            image = Image.new("RGB", (num_tiles_width * tile_width, num_tiles_height * tile_height))
        except MemoryError:
            self.memory_error.emit()
            return

        num_tiles = num_tiles_width * num_tiles_height
        cur_tile = 0
        for i in range(num_tiles_width):
            lon = self.pix_to_lon(i)
            for j in range(num_tiles_height):
                cur_tile += 1
                self.update_progress.emit(cur_tile, num_tiles)

                lat = self.pix_to_lat(j)
                tile = fetch_tile(lat, lon)

                image.paste(tile, (i * tile_width, j * tile_height))
        self.image_created.emit(image, self.lat, self.lon)

    def set_coords(self, coord_a, coord_b):
        lat_a = coord_a[0]
        lat_b = coord_b[0]
        self.lat = sorted([lat_a, lat_b], key=abs, reverse=True)

        lon_a = coord_a[1]
        lon_b = coord_b[1]
        self.lon = sorted([lon_a, lon_b], key=abs, reverse=True)

    def pix_to_lon(self, n):
        return math.degrees(
            (lon_to_pix(self.lon[0]) + _pixels_to_degrees(n * tile_width) - earth_pix) / pix_rad
        )

    def pix_to_lat(self, n):
        return math.degrees(math.pi / 2 - 2 * math.atan(
            math.exp(
                ((lat_to_pix(self.lat[0]) + _pixels_to_degrees(n * tile_height) - earth_pix) / pix_rad)
            )
        ))


if __name__ == "__main__":
    map_stitcher = MapStitcher([35.062821, -80.819439], [35.061241, -80.817513])
    map_stitcher.image.save("test.jpg")
