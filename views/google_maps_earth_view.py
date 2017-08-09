from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget, QApplication

from views.gen.ui_google_maps_earth_view import Ui_google_maps_earth_view


class GoogleMapsEarthView(QWidget):
    @property
    def interval(self):
        return self.ui.interval_spn.value()

    @property
    def overlap(self):
        return float(self.ui.overlap_spn.value()) / 100

    @property
    def rectangle(self):
        # {'b': {'b': -78.649, 'f': -78.44299999999998}, 'f': {'b': 44.49, 'f': 44.599}}
        bounds_js = self.eval_javascript("rectangle.getBounds()")
        point_a = (bounds_js["f"]["b"], bounds_js["b"]["b"])
        point_b = (bounds_js["f"]["f"], bounds_js["b"]["f"])
        return point_a, point_b

    @property
    def latitude(self):
        return self.eval_javascript("map.getCenter().lat()")

    @property
    def longitude(self):
        return self.eval_javascript("map.getCenter().lng()")

    def __init__(self, google_maps_earth_ctrl, parent=None):
        self.google_maps_earth_ctrl = google_maps_earth_ctrl
        super(GoogleMapsEarthView, self).__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.build_ui()

    def build_ui(self):
        self.ui = Ui_google_maps_earth_view()
        self.ui.setupUi(self)

        # Modify UI
        self.ui.web_view = QWebEngineView()
        self.ui.google_maps_earth_layout.insertWidget(0, self.ui.web_view)

        # Tell controller that UI modifications are done
        self.google_maps_earth_ctrl.init_ui(self)

        # Signals/Slots

    def eval_javascript(self, js):
        result = None

        def finished(f):
            nonlocal result
            result = f

        self.ui.web_view.page().runJavaScript(js, finished)
        while result is None:
            QApplication.instance().processEvents(
                QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers | QEventLoop.WaitForMoreEvents)
        return result
