import os
import time
import threading

dx = 0
dy = 0

BUTTONS = [1, 0, 8, 9]
LAST_BUTTON_PRESSED: dict[int, bool] = {}
BUTTON_PRESSES: dict[int, bool] = {}

def get_movement() -> tuple[int, int]:
    global dx, dy
    value = (dx, dy)
    dx = 0
    dy = 0
    return value


def get_button(button: int) -> bool:
    return BUTTON_PRESSES.pop(button, False)


def has_any_input() -> bool:
    global dx, dy
    value = any(BUTTON_PRESSES.values()) or dx or dy
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
            print(f"key {event.code=} {event.value=}")
        elif event.type == evdev.ecodes.EV_ABS:
            print(f"abs {event.code=} {event.value=}")
        else:
            print(event)

        time.sleep(0.1)


def vibrate_controller():
    pass


def start() -> threading.Thread:
    thread = threading.Thread(target=input_handling)
    thread.daemon = True
    thread.start()
    return thread
