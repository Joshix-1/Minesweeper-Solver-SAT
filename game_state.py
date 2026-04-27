import time
import json
from solver_implementation import *
from random_fair_boards import get_fair_mines

n_rows: int = 13
n_cols: int = 13
n_mines: int = 42

board: Board = Board(n_rows, n_cols)
player_solution = Solution(0, 0, 0)
solver_solution = Solution(0, 0, 0)

state = 0  # -1: loss, 0: ongoing, 1: win

start_time = 0


def new_state(initial: tuple[int, int] | None = None, force_solvable: bool = False):
    global board
    global player_solution
    global solver_solution
    global start_time
    global state

    if not initial:
        board = Board(n_rows, n_cols)
        player_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
        solver_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
        state = 0
        start_time = time.time()
        return

    if n_rows == 13 and n_cols == 13:
        mines = get_fair_mines(initial)
        board = Board(n_rows, n_cols, n_mines=len(mines), mines=mines)
    else:
        print("generating board")
        board = (
            generate_fair_board(n_rows, n_cols, n_mines, initial, max_depth=1, remainder_cutoff=16, max_attempts=1000)
            if force_solvable
            else generate_fun_board(n_rows, n_cols, n_mines, initial, max_attempts=1000)
        )

    player_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
    solver_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
    update_solutions((player_solution, solver_solution), board.reveal_node(initial))

    state = 0
    start_time = time.time()


def do_player_move(move: tuple[int, int], flag=False):
    global board
    global player_solution

    if not board.has_reveal():
        new_state(move)
    elif flag:
        for s in (player_solution, solver_solution):
            node = s.grid.nodes[move]
            node['value'] = -1
            node['solved'] = True
            node['flagged'] = True
    else:
        update_solutions((player_solution, solver_solution), board.reveal_node(move))


def remove_flag(pos: tuple[int, int]):
    for s in (player_solution, solver_solution):
        node = s.grid.nodes[pos]
        node['value'] = 0
        node['solved'] = False
        node['flagged'] = False
