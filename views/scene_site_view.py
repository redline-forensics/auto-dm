from views.gen.ui_scene_site_view import Ui_scene_site_view
from views.scene_view import SceneView


class SceneSiteView(SceneView):
    def build_ui(self):
        super(SceneSiteView, self).build_ui()
        self.ui = Ui_scene_site_view()
        self.ui.setupUi(self)

        # Tell controller that UI modifications are done
        self.scene_ctrl.init_ui(self)

        # Signals/Slots
        self.ui.new_project_btn.clicked.connect(self.scene_ctrl.new_project)
        self.ui.import_scans_btn.clicked.connect(self.scene_ctrl.import_scans)
        self.ui.load_scans_btn.clicked.connect(self.scene_ctrl.load_scans)
        self.ui.place_scans_auto_btn.clicked.connect(self.scene_ctrl.place_scans_auto)
        self.ui.place_scans_manual_btn.clicked.connect(self.scene_ctrl.place_scans_manual)
        self.ui.intensity_point_cloud_btn.clicked.connect(self.scene_ctrl.create_point_cloud)
        self.ui.color_point_cloud_btn.clicked.connect(self.scene_ctrl.create_point_cloud)
        self.ui.delete_point_cloud_btn.clicked.connect(self.scene_ctrl.delete_point_cloud)
        self.ui.clipping_box_btn.clicked.connect(self.scene_ctrl.place_clipping_box)
        self.ui.apply_pictures_btn.clicked.connect(self.scene_ctrl.apply_pictures)
        self.ui.intensity_ortho_btn.clicked.connect(self.scene_ctrl.take_intensity_ortho)
        self.ui.color_ortho_btn.clicked.connect(self.scene_ctrl.take_color_ortho)
