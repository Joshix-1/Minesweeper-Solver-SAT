from collections.abc import Callable
from rgbmatrix import *

type DrawPixelFn = Callable[[tuple[int, int], tuple[int, int, int]], None]

def create_rgbmatrix() -> RGBMatrix:
    options = RGBMatrixOptions()

    # options.hardware_mapping = self.args.led_gpio_mapping
    options.rows = 64
    options.cols = 64
    # options.chain_length = self.args.led_chain
    # options.parallel = self.args.led_parallel
    # options.row_address_type = self.args.led_row_addr_type
    # options.multiplexing = self.args.led_multiplexing
    # options.pwm_bits = self.args.led_pwm_bits
    # options.brightness = self.args.led_brightness
    # options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
    # options.led_rgb_sequence = self.args.led_rgb_sequence
    # options.pixel_mapper_config = self.args.led_pixel_mapper
    # options.panel_type = self.args.led_panel_type
    # options.pwm_dither_bits = self.args.led_pwm_dither_bits
    # options.limit_refresh_rate_hz = self.args.led_limit_refresh

    options.show_refresh_rate = 1

    # options.gpio_slowdown = self.args.led_slowdown_gpio
    options.disable_hardware_pulsing = True
    options.drop_privileges=False

    matrix = RGBMatrix(options = options)
    return matrix




def draw_4x4_flag(x: int, y: int, drawpx: DrawPixelFn) -> None:
    pass

def draw_4x4_mine(x: int, y: int, drawpx: DrawPixelFn) -> None:
    pass

def draw_4x4_number(x: int, y: int, number: int, drawpx: DrawPixelFn) -> None:
    # SEE: https://deathsythe.itch.io/smallpxnumbers
    coloured: set[tuple[int, int]]
    colour = (255, 255, 255)
    if number == 1:
        pass # blue
        coloured = {
            (1, 0),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 3),
        }
    elif number == 2:
        pass # green
        coloured = {
            (1, 0),
            (2, 0),
            (3, 0),
            (3, 1),
            (1, 2),
            (1, 3),
            (2, 3),
            (3, 3),
        }
    elif number == 3:
        pass # red
        coloured = {
            (1, 0),
            (2, 0),
            (3, 1),
            (3, 2),
            (3, 3),
            (1, 3),
            (2, 2),
            (2, 3),
        }
    elif number == 4:
        pass # dark blue / purple
        coloured = {
            (0, 0),
            (2, 0),
            (0, 1),
            (2, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (3, 2),
            (2, 3),
        }
    elif number == 5:
        pass # dark red
    elif number == 6:
        pass # türkis
    else:
        coloured = set()

    bg_colour = (0, 0, 0)

    y_range = range(y, y + 4)
    for x in range(x, x + 4):
        for y in y_range:
            if (x, y) in coloured:
                drawpx((x, y), colour)
            else:
                drawpx((x, y), bg_colour)
