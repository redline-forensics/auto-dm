class SceneController(object):
    def __init__(self, scene_model):
        self.scene_view = None
        self.scene_model = scene_model

        self.scene_model.auto_place_scans_finished.connect(self.on_auto_place_scans_finished)
        self.scene_model.manual_place_scans_finished.connect(self.on_manual_place_scans_finished)

    def init_ui(self, scene_view):
        self.scene_view = scene_view

    def new_project(self):
        self.scene_model.new_project()

    def import_scans(self):
        self.scene_model.import_scans()

    def load_scans(self):
        self.scene_model.load_scans()

    def place_scans_auto(self):
        self.scene_model.place_scans_auto()

    def place_scans_manual(self):
        self.scene_model.place_scans_manual()

    def create_point_cloud(self):
        self.scene_model.create_point_cloud()

    def delete_point_cloud(self):
        self.scene_model.delete_point_cloud()

    def place_clipping_box(self):
        self.scene_model.place_clipping_box()

    def apply_pictures(self):
        self.scene_model.apply_pictures()

    def on_auto_place_scans_finished(self, success):
        if not success:
            self.scene_view.show_auto_place_scans_failed_dialog()

    def on_manual_place_scans_finished(self, success):
        if not success:
            self.scene_view.show_manual_place_scans_failed_dialog()
