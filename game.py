#!venv/bin/python3
import os
import random
import sys
import time

from solver import sat_inspect_generator, Solution
from solver_implementation import check_solution
import game_state as gs
from rendering import *

if False:
    boards = set()
    for i in range(1000):
        initial = random.randrange(13), random.randrange(13)
        boards.add(frozenset(gs.generate_fair_board(13, 13, 30 + random.randrange(6), initial, max_depth=1, remainder_cutoff=16, max_attempts=1000).get_mines()))
    print(boards)
    sys.exit(0)

def get_move() -> tuple[int, int]:
    while True:
        try:
            move = input("Move [x,y]: ")
            x, y = move.split(",")
            x = int(x.strip())
            y = int(y.strip())
            return y, x
        except EOFError:
            raise
        except Exception as err:
            print(f"{err.__class__.__name__}: {err}", flush=True)


def init_game_state():
    gs.n_rows = 13
    gs.n_cols = 13
    gs.n_mines = gs.n_rows * gs.n_cols // 6
    gs.new_state()

USE_RGB_MATRIX = not os.environ.get("DO_NOT_USE_RGB_MATRIX")
if USE_RGB_MATRIX:
    matrix = create_rgbmatrix()
    offscreen_canvas = matrix.CreateFrameCanvas()
else:
    matrix = None
    offscreen_canvas = None

highlighted_pos: None | tuple[int, int] = None


if offscreen_canvas is not None:
    def draw_pixel(pos: tuple[int, int], colour: tuple[int, int, int]) -> None:
        x, y = pos
        offscreen_canvas.SetPixel(x, y, *colour)
else:
    from PIL import Image
    image = Image.new("RGB", size=(64, 64))
    def draw_pixel(pos: tuple[int, int], colour: tuple[int, int, int]) -> None:
        # print(f"draw_pixel({pos}, {colour})")
        image.putpixel(pos, colour)


def draw_board():
    global offscreen_canvas

    if offscreen_canvas is not None:
        offscreen_canvas.Fill(0, 0, 0)
    else:
        for x in range(64):
            for y in range(64):
                image.putpixel((x, y), (0, 0, 0))

    self = gs.player_solution
    for i in range(self.n_rows):
        x = i * 5
        for j in range(self.n_cols):
            y = j * 5
            node = self.grid.nodes[i, j]
            if node['flagged']:
                draw_4x4_flag(x, y, drawpx=draw_pixel)
            elif node['solved']:
                if node['value'] == -1:
                    draw_4x4_mine(x, y, drawpx=draw_pixel)
                else:
                    draw_4x4_number(x, y, node['value'], drawpx=draw_pixel)
            else:
                # draw empty
                for dx in range(4):
                    for dy in range(4):
                        draw_pixel((x + dx, y + dy), (22, 22, 22))


    if highlighted_pos:
        (x, y) = highlighted_pos
        x *= 5
        y *= 5
        start_x = max(x - 1, 0)
        start_y = max(y - 1, 0)
        end_x = min(x + 4, 63)
        end_y = min(y + 4, 63)
        draw_pixel((start_x, start_y), WHITE)
        draw_pixel((end_x, start_y), WHITE)
        draw_pixel((start_x, end_y), WHITE)
        draw_pixel((end_x, end_y), WHITE)

    if matrix is not None:
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
    else:
        image.save("frame.png")


def run_interactive_game_round():
    global highlighted_pos
    init_game_state()

    while gs.state == 0:
        draw_board()

        move = get_move()

        highlighted_pos = move

        gs.do_player_move(move)

        gs.state = check_solution(gs.board, gs.player_solution)
        time.sleep(1e-6)  # small sleep

    while True:
        draw_board()
        time.sleep(1e-6)  # small sleep

        if gs.state == 1:
            print("won")
        if gs.state == -1:
            print("lost")


def run_automatic_game_round():
    global highlighted_pos
    init_game_state()

    _time = time.perf_counter()

    while gs.state == 0:
        draw_board()

        try:
            move = next(sat_inspect_generator(gs.solver_solution))
        except StopIteration:
            print("sat_inspect did not find move")
            move = (random.randrange(gs.board.n_cols), random.randrange(gs.board.n_rows))

        highlighted_pos = move

        is_flag = gs.board.value_at(move) == -1
        gs.do_player_move(move, flag=is_flag)

        gs.state = check_solution(gs.board, gs.player_solution)
        took = time.perf_counter() - _time
        if took < 1:
            time.sleep(1 - took)
        else:
            print(f"took {took}s")
        _time = time.perf_counter()


    draw_board()
    if gs.state == 1:
        print("won")
    if gs.state == -1:
        print("lost")

    time.sleep(10)  # small sleep


if __name__ == "__main__":
    while True:
        run_automatic_game_round()
        # run_interactive_game_round()
