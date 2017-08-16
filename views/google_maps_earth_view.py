from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QApplication

from views.gen.ui_google_maps_earth_view import Ui_google_maps_earth_view


class GoogleMapsEarthView(QWidget):
    @property
    def latitude(self):
        return float(self.ui.latitude_edit.text())

    @property
    def longitude(self):
        return float(self.ui.longitude_edit.text())

    @property
    def interval(self):
        return self.ui.interval_spn.value()

    @property
    def overlap(self):
        return float(self.ui.overlap_spn.value()) / 100

    @property
    def map_rectangle(self):
        # {'b': {'b': -78.649, 'f': -78.44299999999998}, 'f': {'b': 44.49, 'f': 44.599}}
        bounds_js = self.eval_javascript("rectangle.getBounds()", True)
        point_a = (bounds_js["f"]["b"], bounds_js["b"]["b"])
        point_b = (bounds_js["f"]["f"], bounds_js["b"]["f"])
        return point_a, point_b

    @map_rectangle.setter
    def map_rectangle(self, value):
        lat = value[0]
        lon = value[1]

        west = lon - 0.001
        east = lon + 0.001
        north = lat - 0.001
        south = lat + 0.001

        self.eval_javascript(
            "rectangle.setBounds({{east: {:f}, north: {:f}, south: {:f}, west: {:f}}})".format(east, north, south,
                                                                                               west), False)

    @property
    def map_center(self):
        return self.eval_javascript("map.getCenter()")

    @map_center.setter
    def map_center(self, value):
        lat = value[0]
        lon = value[1]
        self.eval_javascript("map.setCenter({{lat: {:f}, lng: {:f}}})".format(lat, lon), False)

    def __init__(self, google_maps_earth_ctrl, parent=None):
        self.google_maps_earth_ctrl = google_maps_earth_ctrl
        super(GoogleMapsEarthView, self).__init__(parent=parent, flags=Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.build_ui()

    def build_ui(self):
        self.ui = Ui_google_maps_earth_view()
        self.ui.setupUi(self)

        # Modify UI
        self.ui.web_view = QWebEngineView()
        self.ui.google_maps_earth_layout.insertWidget(0, self.ui.web_view)
        self.ui.latitude_edit.setValidator(QDoubleValidator(-90.0, 90.0, 6))
        self.ui.longitude_edit.setValidator(QDoubleValidator(-180.0, 180.0, 6))
        self.ui.latitude_edit.setText("35.1339428")
        self.ui.longitude_edit.setText("-80.9137203")

        # Tell controller that UI modifications are done
        self.google_maps_earth_ctrl.init_ui(self)

        # Signals/Slots
        self.ui.go_btn.clicked.connect(self.google_maps_earth_ctrl.move_map)

    def eval_javascript(self, js, expect_result):
        result = None

        def finished(f):
            nonlocal result
            result = f

        self.ui.web_view.page().runJavaScript(js, finished)
        if not expect_result:
            return
        while result is None:
            QApplication.instance().processEvents(
                QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers | QEventLoop.WaitForMoreEvents)
        return result
