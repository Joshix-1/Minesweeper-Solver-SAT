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

_draw_everything: bool = False
_powers = False
def has_powers() -> bool:
    return _powers

def get_draw_everything() -> bool:
    global _draw_everything
    value = _draw_everything
    _draw_everything = False
    return value

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

device: "evdev.InputDevice | None" = None

def _input_handling():
    global dx, dy, _powers, _draw_everything, device

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
                if event.value:
                    buffer.append(event.code * event.value)
                sleep = 1e-2
            elif event.code == evdev.ecodes.ABS_HAT0Y:
                dy = int(event.value)
                if event.value:
                    buffer.append(event.code * event.value)
                sleep = 1e-2
            else:
                pass # print(f"abs {event.code=} {event.value=}")
        else:
            pass # print(event)

        if buffer in _SEQUENCES:
            buffer.clear()
            _powers = not _powers
            if not _powers:
                _draw_everything = True

        time.sleep(sleep)


def vibrate_controller(
    duration_ms: int = 1000,
    repeat_count: int = 1,
    strong_magnitude: int = 0x0000,
    weak_magnitude: int = 0xffff,
):
    if not device:
        return

    try:
        # SEE: https://python-evdev.readthedocs.io/en/latest/tutorial.html#injecting-an-ff-event-into-first-ff-capable-device-found
#
        from evdev import ff, ecodes

        rumble = ff.Rumble(strong_magnitude=strong_magnitude, weak_magnitude=weak_magnitude)
        effect_type = ff.EffectType(ff_rumble_effect=rumble)

        effect = ff.Effect(
            ecodes.FF_RUMBLE, -1, 0,
            ff.Trigger(0, 0),
            ff.Replay(duration_ms, 0),
            effect_type
        )

        effect_id = device.upload_effect(effect)


        device.write(ecodes.EV_FF, effect_id, repeat_count)

        def erase_effect():
            time.sleep(duration_ms / 1000)
            device.erase_effect(effect_id)

        threading.Thread(target=erase_effect, daemon=True).start()
    except Exception:
        traceback.print_exc()


def start() -> threading.Thread:
    thread = threading.Thread(target=input_handling, daemon=True)
    thread.start()
    return thread
