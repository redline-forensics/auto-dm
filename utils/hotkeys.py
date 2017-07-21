from PySide.QtCore import QThread, Signal

from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent

curr_id = 0
hotkeys = {}


def add_hotkey(key, modifiers, action):
    global curr_id, hotkeys, hk
    hotkeys[curr_id] = {"keys": set([key] + modifiers), "action": action}
    curr_id += 1


def unhook():
    hk.stop()
    hotkey_runner.quit()
    hotkey_runner.wait()


class HotkeyRunner(QThread):
    hk_activated = Signal(object)

    def run(self):
        global hk
        hk = Hook()
        hk.handler = self._on_event
        hk.hook()

    def _on_event(self, args):
        global hotkeys
        if isinstance(args, KeyboardEvent):
            if args.event_type != "key down":
                return

            pressed_keys = set(args.pressed_key)

            for hotkey in hotkeys.itervalues():
                if pressed_keys == hotkey["keys"]:
                    self.hk_activated.emit(hotkey["action"])
                    hk.pressed_keys = []


hotkey_runner = HotkeyRunner()
hotkey_runner.hk_activated.connect(lambda fn: fn())
hotkey_runner.start()
