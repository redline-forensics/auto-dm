class SceneController(object):
    def __init__(self, scene_model):
        self.scene_view = None
        self.scene_model = scene_model

    def init_ui(self, scene_view):
        self.scene_view = scene_view
