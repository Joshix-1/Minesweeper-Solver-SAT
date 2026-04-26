import time
import json
from solver_implementation import *
from random_fair_boards import get_fair_mines

n_rows: int = 16
n_cols: int = 16
n_mines: int = 42

board: Board = Board(n_rows, n_cols)
player_solution = Solution(0, 0, 0)

state = 0  # -1: loss, 0: ongoing, 1: win

start_time = 0


def new_state(initial: tuple[int, int] | None = None, force_solvable: bool = False):
    global board
    global player_solution
    global start_time
    global state

    player_solution = Solution(board.n_rows, board.n_cols, board.n_mines)

    if not initial:
        board = Board(n_rows, n_cols)
        state = 0
        start_time = time.time()
        return

    if n_rows == 16 and n_cols == 16:
        board = Board(n_rows, n_cols, n_mines, mines=get_fair_mines(initial))
    else:
        print("generating board")
        board = (
            generate_fair_board(n_rows, n_cols, n_mines, initial, max_depth=1, remainder_cutoff=16, max_attempts=1000)
            if force_solvable
            else generate_fun_board(n_rows, n_cols, n_mines, initial, max_attempts=1000)
        )

    update_solution(player_solution, board.reveal_node(initial))

    state = 0
    start_time = time.time()


def do_player_move(move: tuple[int, int]):
    global board
    global player_solution

    if not board.has_reveal():
        new_state(move)
    else:
        update_solution(player_solution, board.reveal_node(move))
