import time
import threading
import pygame

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

    pygame.joystick.init()

    while pygame.joystick.get_count() == 0:
        time.sleep(1)

    joystick = pygame.joystick.Joystick(0)

    while True:
        print(f"({dx=}, {dy=}) {BUTTON_PRESSES=}")
        for axis in range(min(2, joystick.get_numaxes())):
            value = joystick.get_axis(axis)
            if abs(value) > 0.5:
                normed_value = 1 if value > 0 else -1
                if value == 0:
                    dx = normed_value
                else:
                    dy = normed_value

        for button in BUTTONS:
            if not (value := joystick.get_button(button)) and LAST_BUTTON_PRESSED.get(button, False):
                BUTTON_PRESSES[button] = True

            LAST_BUTTON_PRESSED[button] = value

        time.sleep(1e-3)


def vibrate_controller():
    for j in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(j)
        joystick.rumble(100, 400, 1)


def start() -> threading.Thread:
    thread = threading.Thread(target=input_handling)
    thread.daemon = True
    thread.start()
    return thread
