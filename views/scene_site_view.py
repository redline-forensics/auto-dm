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
