from PyQt5.QtWidgets import QWidget


class SceneView(QWidget):
    def __init__(self, scene_ctrl):
        self.scene_ctrl = scene_ctrl
        super(SceneView, self).__init__()
        self.build_ui()

    def build_ui(self):
        self.ui = None
