from collections.abc import Callable
from rgbmatrix import *

type DrawPixelFn = Callable[[tuple[int, int], tuple[int, int, int]], None]

def create_rgbmatrix() -> RGBMatrix:
    options = RGBMatrixOptions()

    # options.hardware_mapping = self.args.led_gpio_mapping
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    # options.row_address_type = self.args.led_row_addr_type
    # options.multiplexing = self.args.led_multiplexing
    # options.pwm_bits = self.args.led_pwm_bits
    # options.brightness = self.args.led_brightness
    # options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
    # options.led_rgb_sequence = self.args.led_rgb_sequence
    # options.pixel_mapper_config = self.args.led_pixel_mapper
    # options.panel_type = self.args.led_panel_type
    # options.pwm_dither_bits = self.args.led_pwm_dither_bits
    options.limit_refresh_rate_hz = 0  # no limit

    options.show_refresh_rate = 1

    # options.gpio_slowdown = self.args.led_slowdown_gpio
    options.disable_hardware_pulsing = True
    options.drop_privileges=False

    matrix = RGBMatrix(options = options)
    return matrix


def draw_4x4_flag(x: int, y: int, drawpx: DrawPixelFn) -> None:
    drawpx((x + 1, y + 1), (255, 0, 0))
    drawpx((x + 2, y + 1), (255, 255, 255))
    drawpx((x + 2, y + 2), (255, 255, 255))


def draw_4x4_mine(x: int, y: int, drawpx: DrawPixelFn) -> None:
    # fill with red for now
    y_range = range(y, y + 4)
    for x in range(x, x + 4):
        for y in y_range:
            drawpx((x, y), (255, 0, 0))


EMPTY_SET: frozenset[tuple[int, int]] = frozenset()
# SEE: https://deathsythe.itch.io/smallpxnumbers
NUMBER_COLOURED_PIXELS: dict[int, frozenset[tuple[int, int]]] = {
    0: EMPTY_SET,
    1: frozenset((
        (1, 0),
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
    )),
    2: frozenset((
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 1),
        (1, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    )),
    3: frozenset((
        (1, 0),
        (2, 0),
        (3, 1),
        (3, 2),
        (3, 3),
        (1, 3),
        (2, 2),
        (2, 3),
    )),
    4: frozenset((
        (0, 0),
        (2, 0),
        (0, 1),
        (2, 1),
        (0, 2),
        (1, 2),
        (2, 2),
        (3, 2),
        (2, 3),
    )),
    5: frozenset((
        (1, 0),
        (2, 0),
        (3, 0),
        (1, 1),
        (3, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    )),
    6: frozenset((
        (3, 0),
        (2, 0),
        (1, 1),
        (1, 2),
        (3, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    )),
    7: frozenset((
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 1),
        (2, 2),
        (1, 3),
    )),
    8: frozenset((
        (0, 0),
        (1, 0),
        (2, 0),
        (0, 1),
        (2, 1),
        (0, 2),
        (1, 2),
        (3, 2),
        (1, 3),
        (2, 3),
        (3, 3),
    )),
    9: frozenset((
        (1, 0),
        (2, 0),
        (3, 0),
        (1, 1),
        (3, 1),
        (3, 2),
        (2, 3),
    )),
}

def draw_4x4_number(x: int, y: int, number: int, drawpx: DrawPixelFn) -> None:
    bg_colour = (42, 42, 42)
    colour = (255, 255, 255)

    if number == 1:
        colour = (24, 22, 198) # blue
    elif number == 2:
        colour = (2, 120, 18) # green
    elif number == 3:
        colour = (216, 7, 18) # red
    elif number == 4:
        colour = (10, 5, 115) # dark blue / purple
    elif number == 5:
        colour = (110, 12, 18) # dark red
    elif number == 6:
        colour = (11, 92, 147) # türkis
    elif number == 7:
        colour = (66, 88, 40) # dark green
    elif number == 8:
        colour = (255, 255, 255) # black is hard with leds
    elif number == 9:
        colour = (239, 219, 35) # yellow

    coloured = NUMBER_COLOURED_PIXELS.get(number, EMPTY_SET)

    y_range = range(y, y + 4)
    for x in range(x, x + 4):
        for y in y_range:
            if (x, y) in coloured:
                drawpx((x, y), colour)
            else:
                drawpx((x, y), bg_colour)
