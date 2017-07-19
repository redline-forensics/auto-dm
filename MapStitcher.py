import cStringIO
import math
import os
import time
import urllib

from PIL import Image

import Preferences

api_key = Preferences.get_google_maps_api_key()
tile_pix = 640
url_base = "https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&center={lat},{lon}&zoom={zoom}" \
           "&size={tile_pix}x{tile_pix}&key={key}"
earth_pix = 268435456
pix_rad = earth_pix / math.pi
sleep_time = 3.456
zoom = 21


def lat_to_pix(lat):
    sin_lat = math.sin(math.radians(lat))
    return earth_pix - pix_rad * math.log((1 + sin_lat) / (1 - sin_lat)) / 2


def lon_to_pix(lon):
    return earth_pix + lon * math.radians(pix_rad)


def _pixels_to_degrees(pixels):
    return pixels * 2 ** (21 - zoom)


def fetch_tile(lat, lon):
    filename = os.path.join("map_stitch_cache", "{}_{}.jpg".format(lat, lon))
    if os.path.isfile(filename):
        tile = Image.open(filename)
    else:
        url = url_base.format(lat=lat, lon=lon, zoom=zoom, tile_pix=tile_pix, key=api_key)
        result = urllib.urlopen(url).read()
        tile = Image.open(cStringIO.StringIO(result)).convert("RGB")
        if not os.path.exists("map_stitch_cache"):
            os.mkdir("map_stitch_cache")
        tile.save(filename)
        time.sleep(sleep_time)
    return tile


class MapStitcher(object):
    def __init__(self, coord_a, coord_b):
        self.set_coords(coord_a, coord_b)

        self.num_tiles_width = int(math.ceil((lon_to_pix(self.lon[1]) - lon_to_pix(self.lon[0])) / tile_pix))
        self.num_tiles_height = int(math.ceil((lat_to_pix(self.lat[1]) - lat_to_pix(self.lat[0])) / tile_pix))

        self.image = Image.new("RGB", (self.num_tiles_width * tile_pix, self.num_tiles_height * tile_pix))

        self.fetch()

    def set_coords(self, coord_a, coord_b):
        lat_a = coord_a[0]
        lat_b = coord_b[0]
        self.lat = sorted([lat_a, lat_b], key=abs, reverse=True)

        lon_a = coord_a[1]
        lon_b = coord_b[1]
        self.lon = sorted([lon_a, lon_b], key=abs, reverse=True)

    def fetch(self):
        num_tiles = self.num_tiles_width * self.num_tiles_height
        for i in range(self.num_tiles_width):
            lon = self.pix_to_lon(i)
            for j in range(self.num_tiles_height):
                print("Fetching tile {:d}/{:d}".format(i * self.num_tiles_width + j, num_tiles))

                lat = self.pix_to_lat(j)
                tile = fetch_tile(lat, lon)

                self.image.paste(tile, (i * tile_pix, j * tile_pix))

    def pix_to_lon(self, n):
        return math.degrees(
            (lon_to_pix(self.lon[0]) + _pixels_to_degrees(n * tile_pix) - earth_pix) / pix_rad
        )

    def pix_to_lat(self, n):
        return math.degrees(math.pi / 2 - 2 * math.atan(
            math.exp(
                ((lat_to_pix(self.lat[0]) + _pixels_to_degrees(n * tile_pix) - earth_pix) / pix_rad)
            )
        ))


if __name__ == "__main__":
    map_stitcher = MapStitcher([35.063724, -80.821108], [35.058168, -80.812432])
    map_stitcher.image.save("test.jpg")
