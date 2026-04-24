#!/usr/bin/env python3
import time

from solver_implementation import *
import game_state as gs
from rendering import *

def get_move() -> tuple[int, int]:
    while True:
        try:
            move = input("Move [x,y]: ")
            x, y = move.split(",")
            x = int(x.strip())
            y = int(y.strip())
            return y, x
        except BrokenPipeError:
            raise
        except Exception as err:
            print(f"{err.__class__.__name__}: {err}", flush=True)


def init_game_state():
    gs.n_rows = 16
    gs.n_cols = 16
    gs.n_mines = gs.n_rows * gs.n_cols // 5
    gs.new_state()


matrix = create_rgbmatrix()
offscreen_canvas = matrix.CreateFrameCanvas()
highlighted_pos: None | tuple[int, int] = None


def draw_pixel(pos: tuple[int, int], colour: tuple[int, int, int]) -> None:
    x, y = pos
    offscreen_canvas.SetPixel(x, y, *colour)

def draw_board():
    global offscreen_canvas

    offscreen_canvas.Fill(0, 0, 0)

    self = gs.player_solution
    for i in range(self.n_rows):
        x = i * 4
        for j in range(self.n_cols):
            if self.grid.nodes[i, j]['solved']:
                if self.grid.nodes[i, j]['value'] == -1:
                    if self.grid.nodes[i, j]['flagged']:
                        draw_4x4_flag(x, j * 4, drawpx=draw_pixel)
                    else:
                        draw_4x4_mine(x, j * 4, drawpx=draw_pixel)
                else:
                    draw_4x4_number(x, j * 4, self.grid.nodes[i, j]['value'], drawpx=draw_pixel)

    if highlighted_pos:
        (x, y) = highlighted_pos
        x *= 4
        y *= 4
        draw_pixel((x, y), WHITE)
        draw_pixel((x + 4, y), WHITE)
        draw_pixel((x, y + 4), WHITE)
        draw_pixel((x + 4, y + 4), WHITE)

    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)


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


if __name__ == "__main__":
    while True:
        run_interactive_game_round()
