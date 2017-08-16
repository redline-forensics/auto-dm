from PyQt5.QtCore import QThread, pyqtSignal
from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent

from models.model import Model


class HotkeyModel(Model):
    def __init__(self):
        super(Model, self).__init__()
        self.hotkey_runner = HotkeyRunner()
        self.hotkey_runner.hk_activated.connect(lambda fn: fn())

    def start_detection(self):
        self.hotkey_runner.start()

    def stop_detection(self):
        self.hotkey_runner.stop()

    def add_hotkey(self, keys, action):
        self.hotkey_runner.add_hotkey(keys, action)


class HotkeyRunner(QThread):
    hk_activated = pyqtSignal(object)

    def __init__(self):
        super(HotkeyRunner, self).__init__()
        self.hook = Hook()
        self.hook.handler = self._on_event
        self.hotkeys = []

    def add_hotkey(self, keys, action):
        self.hotkeys.append({"keys": set(keys), "action": action})

    def run(self):
        self.hook.hook()

    def stop(self):
        self.hook.stop()

    def _on_event(self, args):
        if isinstance(args, KeyboardEvent):
            if args.event_type == "key up":
                self.hook.pressed_keys = list(set(self.hook.pressed_keys) - set(args.pressed_key))
            if args.event_type != "key down":
                return

            pressed_keys = set(args.pressed_key)
            print(args.event_type, pressed_keys)

            for hotkey in self.hotkeys:
                if hotkey["keys"].issubset(pressed_keys):
                    self.hk_activated.emit(hotkey["action"])
                    # self.hook.pressed_keys = []
