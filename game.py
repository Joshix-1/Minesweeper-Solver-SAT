#!venv/bin/python3
import os
import random
import sys
import time

import input_handling
from solver import sat_inspect_generator, Solution
from solver_implementation import check_solution, update_solution
import game_state as gs
from rendering import *


if False:
    with open("test.py", "wt") as f:
        boards: list[set[frozenset[tuple[int, int]]]] = [set() for _ in range(13 * 13)]
        for i in range(6760):
            pos_idx = i % (13 * 13)
            initial = pos_idx // 13, pos_idx % 13
            boards[pos_idx].add(frozenset(gs.generate_fair_board(13, 13, 30 + random.randrange(6), initial, max_depth=1, remainder_cutoff=16, max_attempts=1000).get_mines()))
        print([list(b) for b in boards], file=f, flush=True)
    sys.exit(0)


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

    def draw_rect(pos: tuple[int, int], size: tuple[int, int], colour: tuple[int, int, int]) -> None:
        offscreen_canvas.SubFill(*pos, *size, *colour)
else:
    from PIL import Image
    image = Image.new("RGB", size=(64, 64))
    def draw_pixel(pos: tuple[int, int], colour: tuple[int, int, int]) -> None:
        # print(f"draw_pixel({pos}, {colour})")
        image.putpixel(pos, colour)

    def draw_rect(pos: tuple[int, int], size: tuple[int, int], colour: tuple[int, int, int]) -> None:
        (x, y) = pos
        (w, h) = size
        for dx in range(w):
            for dy in range(h):
                draw_pixel((x + dx, y + dy), colour)


def draw_board():
    global offscreen_canvas

    if offscreen_canvas is not None:
        offscreen_canvas.Clear()
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
                    draw_rect((x, y), (4, 4), (255, 0, 0))
                    # draw_4x4_mine(x, y, drawpx=draw_pixel)
                elif offscreen_canvas is not None:
                    offscreen_canvas.DrawNumber(x, y, node['value'])
                else:
                    draw_4x4_number(x, y, node['value'], drawpx=draw_pixel)
            else:
                draw_rect((x, y), (4, 4), (22, 22, 22))

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
    global highlighted_pos, is_automatic_game
    highlighted_pos = (0, 0)

    init_game_state()


    while gs.state == 0:
        draw_board()

        if (
            input_handling.get_button(input_handling.BTN_04)
            or input_handling.get_button(input_handling.BTN_04)
        ):
            gs.reveal_node(highlighted_pos)
        if (
            input_handling.get_button(input_handling.BTN_02)
            or input_handling.get_button(input_handling.BTN_03)
        ):
            gs.toggle_flag(highlighted_pos)
        if (
            input_handling.get_button(input_handling.BTN_09)
            or input_handling.get_button(input_handling.BTN_10)
        ): # cancel Game
            is_automatic_game = True
            return

        (dx, dy) = input_handling.get_movement()
        if dx or dy:
            highlighted_pos = (
                (highlighted_pos[0] + dx) % gs.n_cols,
                (highlighted_pos[1] + dy) % gs.n_rows,
            )

        gs.state = check_solution(gs.board, gs.player_solution)
        time.sleep(1e-3)  # small sleep

    if gs.state == 1:
        print("won")
    if gs.state == -1:
        print("lost")


    input_handling.vibrate_controller()
    draw_board()
    time.sleep(5)  # long sleep
    highlighted_pos = None

    if gs.state == -1:
        update_solution(gs.player_solution, gs.board.reveal_nodes(gs.player_solution.nodes))

    input_handling.clear_inputs()
    while not input_handling.has_any_input():
        draw_board()
        time.sleep(1e-3)


def run_automatic_game_round():
    global highlighted_pos, is_automatic_game
    highlighted_pos = None
    init_game_state()

    _time = time.perf_counter()

    while gs.state == 0:
        if input_handling.has_any_input():
            is_automatic_game = False
            return
        draw_board()
        # print(f"draw_board took {time.perf_counter() - _time}s")

        try:
            move = next(sat_inspect_generator(gs.solver_solution))
        except StopIteration:
            print("sat_inspect did not find move")
            nodes = gs.solver_solution.grid.nodes
            unsolved_nodes = [
                n for n in nodes if not nodes[n]['solved']
            ]
            if unsolved_nodes:
                move = random.choice(unsolved_nodes)
            else:
                move = (random.randrange(gs.board.n_cols), random.randrange(gs.board.n_rows))

        highlighted_pos = move

        is_flag = gs.board.value_at(move) == -1
        if is_flag:
            gs.add_flag(move)
        else:
            gs.reveal_node(move)

        gs.state = check_solution(gs.board, gs.player_solution)
        took = time.perf_counter() - _time
        if took < 2:
            time.sleep(2 - took)
        else:
            print(f"took {took}s")
        _time = time.perf_counter()


    draw_board()
    time.sleep(10)

    if gs.state == 1:
        print("won")
    if gs.state == -1:
        print("lost")

    highlighted_pos = None
    draw_board()

    time.sleep(10)


is_automatic_game = True

if __name__ == "__main__":
    _ = input_handling.start()
    while True:
        input_handling.clear_inputs()
        if is_automatic_game:
            run_automatic_game_round()
        else:
            run_interactive_game_round()
