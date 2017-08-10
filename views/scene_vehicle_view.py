from views.gen.ui_scene_vehicle_view import Ui_scene_vehicle_view
from views.scene_view import SceneView


class SceneVehicleView(SceneView):
    def build_ui(self):
        super(SceneVehicleView, self).build_ui()
        self.ui = Ui_scene_vehicle_view()
        self.ui.setupUi(self)

        # Tell controller that UI modifications are done
        self.scene_ctrl.init_ui(self)

        # Signals/Slots
