from collections import deque
import traceback
import os
import time
import threading
import pathlib

dx = 0
dy = 0

buffer = deque(maxlen=10)
BTN_01 = 288
BTN_02 = 289
BTN_03 = 290
BTN_04 = 291
BTN_09 = 296
BTN_10 = 297
BUTTONS = frozenset((
    BTN_01,
    BTN_02,
    BTN_03,
    BTN_04,
    BTN_09,
    BTN_10,
))
BUTTON_PRESSES: dict[int, bool] = {}

_powers = False
def has_powers() -> bool:
    return _powers

def get_movement() -> tuple[int, int]:
    global dx, dy
    value = (dx, dy)
    dx = 0
    dy = 0
    return value


def get_button(button: int) -> bool:
    return BUTTON_PRESSES.pop(button, False)


def clear_inputs():
    global dx, dy
    BUTTON_PRESSES.clear()
    dx = 0
    dy = 0

_SEQUENCES = (
    deque([-17, -17, 17, 17, -16, 16, -16, 16, 289, 290]),
    deque([-17, -17, 17, 17, -16, 16, -16, 16, 290, 289]),
)

def has_any_input() -> bool:
    global dx, dy
    value = any(BUTTON_PRESSES.values()) or get_movement() != (0, 0)
    BUTTON_PRESSES.clear()
    return bool(value)


def input_handling():
    while True:
        try:
            _input_handling()
        except Exception:
            traceback.print_exc()
            time.sleep(1)


def _input_handling():
    global dx, dy, _powers

    import evdev

    while True:
        try:
            path = next(pathlib.Path("/dev/input/").glob("event*"))
            break
        except StopIteration:
            time.sleep(1)

    device = evdev.InputDevice(path.as_posix())

    print("Starting listening to joysticks")

    for event in device.read_loop():
        sleep = 1e-6
        if event.type == evdev.ecodes.EV_KEY:
            if event.value == 0 and event.code in BUTTONS:
                # has left key go
                BUTTON_PRESSES[event.code] = True
                buffer.append(event.code)
                sleep = 1e-2
        elif event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_HAT0X:
                dx = int(event.value)
                buffer.append(event.code * event.value)
                sleep = 1e-2
            elif event.code == evdev.ecodes.ABS_HAT0Y:
                dy = int(event.value)
                buffer.append(event.code * event.value)
                sleep = 1e-2
            else:
                print(f"abs {event.code=} {event.value=}")
        else:
            pass # print(event)

        if buffer in _SEQUENCES:
            _powers = not _powers
            import game
            game.draw_everything = True
            game.matrix.Clear()

        time.sleep(sleep)


def vibrate_controller():
    pass


def start() -> threading.Thread:
    thread = threading.Thread(target=input_handling, daemon=True)
    thread.start()
    return thread
