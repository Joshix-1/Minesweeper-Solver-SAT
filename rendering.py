from collections.abc import Callable
from rgbmatrix import *

WHITE = (255, 255, 255)

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
    #options.pwm_lsb_nanoseconds = 400
    # options.led_rgb_sequence = self.args.led_rgb_sequence
    # options.pixel_mapper_config = self.args.led_pixel_mapper
    # options.panel_type = self.args.led_panel_type
    # options.pwm_dither_bits = self.args.led_pwm_dither_bits
    options.limit_refresh_rate_hz = 0  # no limit

    options.show_refresh_rate = 0

    # options.gpio_slowdown = self.args.led_slowdown_gpio
    options.disable_hardware_pulsing = False
    options.drop_privileges=False

    matrix = RGBMatrix(options = options)
    return matrix


def draw_4x4_flag(x: int, y: int, drawpx: DrawPixelFn) -> None:
    drawpx((x + 1, y + 1), (255, 0, 0))
    drawpx((x + 2, y + 1), WHITE)
    drawpx((x + 2, y + 2), WHITE)
