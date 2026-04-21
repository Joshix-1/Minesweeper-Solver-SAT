#!/usr/bin/env python3
import time

from solver_implementation import *
import game_state as gs

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

gs.n_rows = 16
gs.n_cols = 16
gs.n_mines = gs.n_rows * gs.n_cols // 5
gs.new_state()

while gs.state == 0:
    print(gs.player_solution)

    move = get_move()

    gs.do_player_move(move)

    gs.state = check_solution(gs.board, gs.player_solution)

print(gs.player_solution)
if gs.state == 1:
    print("won")
if gs.state == -1:
    print("lost")
