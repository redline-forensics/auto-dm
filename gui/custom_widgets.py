import math
import os

import pyttsx
from PySide.QtCore import Qt
from PySide.QtGui import QDialog, QProgressBar, QVBoxLayout, QLabel, QHBoxLayout, QTabWidget, QWidget, \
    QMainWindow, QLineEdit, QPushButton, QProgressDialog, QFileDialog, QMessageBox
from PySide.QtWebKit import QWebView

from prefs import preferences
from utils.job_type import JobType
from utils.map_stitcher import MapStitcher, lat_to_pix, lon_to_pix, pix_to_lat, pix_to_lon


class IndefiniteProgressDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super(IndefiniteProgressDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.message = message

        self.init_ui()

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

    def init_ui(self):
        message_lbl = QLabel(self.message)
        message_lbl.setAlignment(Qt.AlignHCenter)

        progress = QProgressBar()
        progress.setTextVisible(False)
        progress.setRange(0, 0)

        layout = QVBoxLayout()
        layout.addWidget(message_lbl)
        layout.addWidget(progress)
        self.setLayout(layout)


class NoLicensesDialog(QDialog):
    def __init__(self, parent=None):
        super(NoLicensesDialog, self).__init__(parent)
        self.setWindowTitle("No Licenses")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.init_ui()

        # self.setWindowFlags(self.windowFlags() | ~Qt.WindowContextHelpButtonHint)
        # self.setWindowFlags(self.windowFlags() | ~Qt.WindowStaysOnBottomHint)
        self.setModal(True)

    def init_ui(self):
        message_lbl = QLabel("No Pix4D licenses available. Would you like to ask for one?")

        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(self.ask_for_license)

        no_btn = QPushButton("No")
        no_btn.clicked.connect(lambda: self.done(0))

        main_layout = QVBoxLayout()
        main_layout.addWidget(message_lbl)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def ask_for_license(self):
        tts = pyttsx.init()
        tts.say("Hey fellas, does anyone have picks four dee open?")
        tts.runAndWait()
        self.done(0)


class DroneTool(QMainWindow):
    def __init__(self, job_type, parent=None):
        super(DroneTool, self).__init__()
        self.job_type = job_type
        if JobType(job_type.value) is JobType.SITE:
            print("site")
            self.setWindowTitle("Drone Site Tool")
        elif JobType(job_type.value) is JobType.VEHICLE:
            print("vehicle")
            self.setWindowTitle("Drone Vehicle Tool")
        self.setWindowFlags(self.windowFlags() | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.init_ui()

    def init_ui(self):
        self.copy_pictures_button = QPushButton("Copy Pictures From Server")
        self.new_proj_button = QPushButton("New Project")
        self.start_proc_button = QPushButton("Start Processing")
        self.edit_mosaic_button = QPushButton("Edit Mosaic")

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_tab = QTabWidget()
        manual_widget = QWidget()
        manual_layout = QVBoxLayout()
        manual_layout.addWidget(self.copy_pictures_button)
        manual_layout.addWidget(self.new_proj_button)
        manual_layout.addWidget(self.start_proc_button)
        manual_layout.addWidget(self.edit_mosaic_button)
        manual_widget.setLayout(manual_layout)
        main_tab.addTab(manual_widget, "Manual")
        main_layout.addWidget(main_tab)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)


class GoogleMapsStitcherDialog(QDialog):
    setup_progress = 10
    fetch_progress = 1000
    save_progress = 100
    progress_total = setup_progress + fetch_progress + save_progress

    def __init__(self, assets_dir=""):
        super(GoogleMapsStitcherDialog, self).__init__()

        self.assets_dir = assets_dir
        self.map_stitcher = MapStitcher()

        self.setWindowTitle("Google Maps Stitcher")
        self.create_controls()
        self.create_layout()
        self.make_connections()

    def create_controls(self):
        self.latitude_label = QLabel("Latitude:")
        self.latitude_edit = QLineEdit()
        self.longitude_label = QLabel("Longitude:")
        self.longitude_edit = QLineEdit()

        self.map_view = QWebView()
        with open("google_map.html", "r") as f:
            html = f.read()
            html = html.format(api_key=preferences.get_google_maps_js_api_key())
            self.map_view.setHtml(html)
        self.create_image_button = QPushButton("Create Image")
        self.create_image_button.setAutoDefault(False)

        self.progress_dialog = QProgressDialog(parent=self)
        self.progress_dialog.setWindowTitle("Create Map")
        self.progress_dialog.setMinimum(0)
        self.progress_dialog.setMaximum(self.progress_total)
        self.progress_dialog.setWindowModality(Qt.WindowModal)

    def create_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.map_view)

        coords_layout = QHBoxLayout()
        coords_layout.addWidget(self.latitude_label)
        coords_layout.addWidget(self.latitude_edit)
        coords_layout.addWidget(self.longitude_label)
        coords_layout.addWidget(self.longitude_edit)
        coords_layout.addSpacing(200)
        coords_layout.addWidget(self.create_image_button)
        layout.addLayout(coords_layout)

        self.setLayout(layout)

    def make_connections(self):
        self.create_image_button.clicked.connect(self.create_image)
        self.map_stitcher.update_progress.connect(self.on_progress_update)
        self.map_stitcher.image_created.connect(self.on_stitching_done)
        self.map_stitcher.memory_error.connect(self.on_memory_error)
        self.latitude_edit.returnPressed.connect(self.jump_to_latitude)
        self.longitude_edit.returnPressed.connect(self.jump_to_longitude)

    def get_map_bounds(self):
        frame = self.map_view.page().mainFrame()
        lat = frame.evaluateJavaScript("map.getCenter().lat()")
        lon = frame.evaluateJavaScript("map.getCenter().lng()")
        return lat, lon

    def move_map(self, lat, lon):
        self.map_view.page().mainFrame().evaluateJavaScript(
            "map.setCenter({{lat: {lat}, lng: {lon}}})".format(lat=lat, lon=lon))
        east = lon + 0.001
        west = lon - 0.001
        north = lat + 0.001
        south = lat - 0.001
        self.map_view.page().mainFrame().evaluateJavaScript("rectangle.setBounds({{"
                                                            "north: {:f}, "
                                                            "south: {:f}, "
                                                            "east: {:f}, "
                                                            "west: {:f}"
                                                            "}})".format(north, south, east, west))
        self.map_view.page().mainFrame().evaluateJavaScript("map.setZoom(17)")

    def jump_to_latitude(self):
        try:
            new_lat = float(self.latitude_edit.text())
        except ValueError:
            return
        lat, lon = self.get_map_bounds()
        self.move_map(new_lat, lon)

    def jump_to_longitude(self):
        try:
            new_lon = float(self.longitude_edit.text())
        except ValueError:
            return
        lat, lon = self.get_map_bounds()
        self.move_map(lat, new_lon)

    def create_image(self):
        self.progress_dialog.setLabelText("Setting up...")
        self.progress_dialog.show()

        frame = self.map_view.page().mainFrame()
        bounds = frame.evaluateJavaScript("rectangle.getBounds()")
        lat = bounds["f"]
        lon = bounds["b"]

        coord_a = [lat["b"], lon["b"]]
        coord_b = [lat["f"], lon["f"]]

        self.progress_dialog.setValue(self.setup_progress)
        self.map_stitcher.start(coord_a, coord_b)

    def on_progress_update(self, curr, max):
        self.progress_dialog.setLabelText("Fetching tile {:d} of {:d}...".format(curr, max))
        self.progress_dialog.setValue(self.setup_progress + (float(curr) / max) * self.fetch_progress)

    def on_stitching_done(self, image, lat, lon):
        self.progress_dialog.setValue(self.setup_progress + self.fetch_progress)
        self.progress_dialog.setLabelText("Saving image...")
        image_file = QFileDialog.getSaveFileName(self, "Save Image", self.assets_dir, "TIFF (*.tif *.tiff)")[0]
        if image_file is None:
            return
        image.save(image_file)

        width_px, height_px = image.size
        width, height = self.calculate_dimensions_in_ft(lat, lon, width_px, height_px)

        tfw_file = os.path.splitext(image_file)[0] + ".tfw"
        with open(tfw_file, "w") as f:
            f.write(str(abs(float(width) / width_px)) + "\n")
            f.write("0\n")
            f.write("0\n")
            f.write(str(-abs(float(height) / height_px)) + "\n")
            f.write("0\n")
            f.write("0\n")

        self.progress_dialog.setValue(self.setup_progress + self.fetch_progress + self.save_progress)

    def on_memory_error(self):
        QMessageBox.critical(self, "Memory Error",
                             "I can't create a map that big! Either give me more memory or choose a smaller area.",
                             QMessageBox.Ok, QMessageBox.NoButton)
        self.progress_dialog.hide()

    def calculate_dimensions_in_ft(self, lat, lon, width_px, height_px):
        x1_px = lon_to_pix(lon[1])
        x2_px = x1_px + width_px
        x1 = lon[1]
        x2 = pix_to_lon(x2_px)
        width = self.distance((lat[1], x1), (lat[1], x2))

        y1_px = lat_to_pix(lat[1])
        y2_px = y1_px + height_px
        y1 = lat[1]
        y2 = pix_to_lat(y2_px)
        height = self.distance((y1, lon[1]), (y2, lon[1]))

        return width, height

    @staticmethod
    def distance(origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        radius = 3959 * 5280  # radius in feet

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c

        return d
