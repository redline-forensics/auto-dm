from models.model import Model


class SceneModel(Model):
    def __init__(self, scene_exe):
        self.scene_exe = scene_exe
        super(SceneModel, self).__init__()
