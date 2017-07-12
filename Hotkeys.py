from threading import Thread

from pywinauto.win32_hooks import Hook
from pywinauto.win32_hooks import KeyboardEvent

curr_id = 0
hotkeys = {}


def add_hotkey(key, modifiers, action):
    global curr_id, hotkeys, hk
    hotkeys[curr_id] = {"key": key, "modifiers": modifiers, "action": action}
    curr_id += 1


def unhook():
    hk.stop()


def _on_event(args):
    global hotkeys
    if isinstance(args, KeyboardEvent):
        if args.event_type != "key down":
            return

        for hotkey in hotkeys.itervalues():
            if args.current_key == hotkey["key"] and all(
                            modifier in args.pressed_key for modifier in hotkey["modifiers"]):
                hotkey["action"]()
                print(
                    "HOTKEY " + " + ".join(str(modifier) for modifier in hotkey["modifiers"]) + " + " + str(
                        hotkey["key"]))


hk = Hook()
hk.handler = _on_event
thread = Thread(target=hk.hook, args=())
thread.start()
