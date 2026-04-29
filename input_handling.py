import os
import time
import threading

dx = 0
dy = 0

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


def has_any_input() -> bool:
    global dx, dy
    value = any(BUTTON_PRESSES.values())
    BUTTON_PRESSES.clear()
    dx = 0
    dy = 0
    return bool(value)


def input_handling():
    global dx, dy

    import evdev

    device = evdev.InputDevice('/dev/input/event0')

    print("Starting listening to joysticks")

    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            if event.value == 0 and event.code in BUTTONS:
                # has left key go
                BUTTON_PRESSES[event.code] = True
        elif event.type == evdev.ecodes.EV_ABS:
            if event.code == evdev.ecodes.ABS_HAT0X:
                dx = int(event.value)
            elif event.code == evdev.ecodes.ABS_HAT0Y:
                dy = int(event.value)
            else:
                print(f"abs {event.code=} {event.value=}")
        else:
            print(event)

        time.sleep(0.05)


def vibrate_controller():
    pass


def start() -> threading.Thread:
    thread = threading.Thread(target=input_handling)
    thread.daemon = True
    thread.start()
    return thread
