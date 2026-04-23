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

def draw_pixel(pos: tuple[int, int], colour: tuple[int, int, int]) -> None:
    x, y = pos
    offscreen_canvas.SetPixel(x, y, *colour)

def draw_board():
    global offscreen_canvas
    self = gs.player_solution
    for i in range(self.n_rows):
        for j in range(self.n_cols):
            if self.grid.nodes[i, j]['solved']:
                if self.grid.nodes[i, j]['value'] == -1:
                    if self.grid.nodes[i, j]['flagged']:
                        draw_4x4_flag(i, j, drawpx=draw_pixel)
                    else:
                        draw_4x4_mine(i, j, drawpx=draw_pixel)
                else:
                    if self.grid.nodes[i, j]['value'] == 0:
                        pass
                    else:
                        draw_4x4_number(i, j, self.grid.nodes[i, j]['value'], drawpx=draw_pixel)

    offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)


def run_interactive_game_round():
    init_game_state()

    while gs.state == 0:
        print(gs.player_solution)
        draw_board()

        move = get_move()

        gs.do_player_move(move)

        gs.state = check_solution(gs.board, gs.player_solution)

    print(gs.player_solution)
    if gs.state == 1:
        print("won")
    if gs.state == -1:
        print("lost")


if __name__ == "__main__":
    while True:
        run_interactive_game_round()
