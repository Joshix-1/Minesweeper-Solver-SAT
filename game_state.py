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

    revealed = board.reveal_node(initial)

    player_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
    update_solution(player_solution, revealed)
    solver_solution = Solution(board.n_rows, board.n_cols, board.n_mines)
    update_solution(solver_solution, revealed)

    state = 0
    start_time = time.time()


def do_player_move(move: tuple[int, int], flag=False):
    global board
    global player_solution

    if not board.has_reveal():
        new_state(move)
    elif flag:
        player_solution.grid.nodes[move]['value'] = -1
        player_solution.grid.nodes[move]['solved'] = True
        player_solution.grid.nodes[move]['flagged'] = True
        solver_solution.grid.nodes[move]['value'] = -1
        solver_solution.grid.nodes[move]['solved'] = True
        solver_solution.grid.nodes[move]['flagged'] = True
    else:
        revealed = board.reveal_node(move)
        update_solution(player_solution, revealed)
        update_solution(solver_solution, revealed)
