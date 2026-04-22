from collections.abc import Callable
from rgbmatrix import *

type DrawPixelFn = Callable[[tuple[int, int], tuple[int, int, int]], None]

def draw_pixel(x: int, y: int, colour: tuple[int, int, int]) -> None:
    # TODO
    matrix = RGBMatrix()
    matrix.SetPixel(x, y, *colour)

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
