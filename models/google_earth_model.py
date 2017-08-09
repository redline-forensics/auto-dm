import math
import os
import re
import time
import warnings
from threading import Timer

from PyQt5.QtCore import pyqtSignal, QThread
from pywinauto import Application, keyboard
from pywinauto.application import ProcessNotFoundError

from models.model import Model
from resources.paths import screenshots_path
from resources.resource_manager import resources
from utils.map_utils import points_to_coords, lon_to_px, lat_to_px, px_to_lat, px_to_lon


class GoogleEarthModel(Model):
    starting_captures = pyqtSignal(int, int)
    update_progress = pyqtSignal(int)
    finished_captures = pyqtSignal()

    def __init__(self, job_name, js_api_key, google_earth_exe):
        self.job_name = job_name
        self.js_api_key = js_api_key
        self.google_earth_exe = google_earth_exe
        super(GoogleEarthModel, self).__init__()

    def start_capturing(self, point_a, point_b, overlap, interval):
        self.google_earth_worker = GoogleEarthWorker(point_a, point_b, overlap, interval, self.job_name,
                                                     self.google_earth_exe)
        self.google_earth_worker.starting_captures.connect(self.starting_captures.emit)
        self.google_earth_worker.update_progress.connect(self.update_progress.emit)
        self.google_earth_worker.finished_captures.connect(self.on_finished_captures)
        self.google_earth_worker.start()

    def cancel_captures(self):
        self.google_earth_worker.cancel()

    def on_finished_captures(self):
        self.google_earth_worker = None
        self.finished_captures.emit()


class GoogleEarthWorker(QThread):
    starting_captures = pyqtSignal(int, int)
    update_progress = pyqtSignal(int)
    finished_captures = pyqtSignal()

    def __init__(self, point_a, point_b, overlap, interval, job_name, google_earth_exe):
        self.lat, self.lon = points_to_coords(point_a, point_b)
        self.overlap = overlap
        self.interval = interval
        self.screenshots_folder = os.path.join(screenshots_path, job_name)
        self.exe = google_earth_exe
        super(GoogleEarthWorker, self).__init__()
        self.canceled = False
        self.timers = []

    def run(self):
        def open_earth():
            warnings.simplefilter("ignore", UserWarning)
            application = Application()
            try:
                return application.connect(path=self.exe)
            except ProcessNotFoundError:
                return application.start(self.exe)

        def get_main_window():
            window = app["Google Earth"]
            window.wait("visible", 30)
            return window

        def get_map_area():
            area = main_window["Qt5QWindowIcon9"]
            area.wait("visible", 30)
            return area

        def get_bottom_margin(width):
            return int(36.6428 + 0.0344658 * width)

        def get_screenshot_rect():
            map_rect = [int(item) for item in re.sub("[(LTRB)]", "", str(map_area.rectangle())).split(", ")]
            return Rectangle(map_rect[0] + 5, map_rect[1] + 5, map_rect[2] - 84,
                             map_rect[3] - max(76, get_bottom_margin(map_rect[2] - map_rect[0])))

        def generate_coords_list():
            tile_width = screenshot_rect.width()
            tile_height = screenshot_rect.height()

            left_px = lon_to_px(self.lon[0])
            top_px = lat_to_px(self.lat[0])

            horiz_px_step = tile_width * (1.0 - self.overlap)
            vert_px_step = tile_height * (1.0 - self.overlap)

            num_tiles_width = int(math.ceil((lon_to_px(self.lon[1]) - lon_to_px(self.lon[0])) / horiz_px_step))
            num_tiles_height = int(math.ceil((lat_to_px(self.lat[1]) - lat_to_px(self.lat[0])) / vert_px_step))

            coords = []
            for j in range(num_tiles_height):
                curr_vert_px = top_px + j * vert_px_step
                for k in range(num_tiles_width):
                    curr_horiz_px = left_px + k * horiz_px_step
                    coords.append((px_to_lat(curr_vert_px), px_to_lon(curr_horiz_px)))
            return coords

        def generate_kml():
            kml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\" xmlns:gx=" \
                  "\"http://www.google.com/kml/ext/2.2\"><gx:Tour><name>Earth Bot</name><gx:Playlist>"
            kml += "<gx:Wait><gx:duration>{wait}</gx:duration></gx:Wait>".format(wait=self.interval).join([
                "<gx:FlyTo><LookAt><longitude>{lon_str}</longitude><latitude>{lat_str}</latitude><altitude>100"
                "</altitude><heading>0</heading><tilt>0</tilt><range>0</range><gx:altitudeMode>relativeToGround"
                "</gx:altitudeMode></LookAt></gx:FlyTo>".format(lat_str=a_lat, lon_str=a_lon)
                for (a_lat, a_lon) in tile_coords
            ])
            kml += "</gx:Playlist></gx:Tour></kml>"

            kml_file = resources["kml"]["earth.kml"]
            with open(kml_file, "w") as file:
                file.write(kml)

            return kml_file

        def open_kml():
            main_window.set_focus()
            map_area.click_input(coords=(
                355,
                [int(item) for item in re.sub("[(LTRB)]", "", str(map_area.client_rect())).split(", ")][3] - 68)
            )
            keyboard.SendKeys("^o")
            open_dialog = app["Open"]
            open_dialog.wait("visible", 30)
            open_dialog.set_focus()
            keyboard.SendKeys(kml_file.replace("/", "\\"), pause=0)
            keyboard.SendKeys("{ENTER}")
            open_dialog.wait_not("exists", 30)

        def screenshot(lat, lon):
            if not os.path.isdir(self.screenshots_folder):
                os.mkdir(self.screenshots_folder)
            file_name = "{}_{}.jpg".format(lat, lon)
            map_area.set_focus()
            print(lat, lon)
            image = map_area.CaptureAsImage(rect=screenshot_rect)
            image.save(os.path.join(self.screenshots_folder, file_name))
            if time.time() < end_time:
                self.update_progress.emit(time.time())

        app = open_earth()
        main_window = get_main_window()
        map_area = get_map_area()
        screenshot_rect = get_screenshot_rect()

        if self.canceled:
            return

        tile_coords = generate_coords_list()
        kml_file = generate_kml()

        if self.canceled:
            return

        time.sleep(1)
        open_kml()

        if self.canceled:
            return

        initial_wait = self.interval - 1.0
        timer = Timer(initial_wait, screenshot, args=(tile_coords[0][0], tile_coords[0][1]))
        timer.start()
        self.timers.append(timer)
        for i, coord in enumerate(tile_coords):
            if self.canceled:
                return

            if i == 0:
                continue

            timer = Timer(initial_wait + self.interval * i, screenshot, args=(coord[0], coord[1]))
            timer.start()
            self.timers.append(timer)

        if self.canceled:
            return

        start_time = time.time()
        end_time = start_time + len(tile_coords) * self.interval
        self.starting_captures.emit(start_time, end_time)
        self.update_progress.emit(time.time())
        while time.time() < end_time:
            if self.canceled:
                return
        self.finished_captures.emit()

    def cancel(self):
        self.canceled = True
        for timer in self.timers:
            if timer is not None:
                timer.cancel()


class Rectangle(object):
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def width(self):
        return abs(self.right - self.left)

    def height(self):
        return abs(self.top - self.bottom)

    def __repr__(self):
        return "Rectangle(left={}, top={}, right={}, bottom={})".format(self.left, self.top, self.right, self.bottom)
