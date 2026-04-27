from minesweeper import *
from solver import *


def solve(board, initial, max_depth=1, remainder_cutoff=0):
    solution = Solution(board.n_rows, board.n_cols, board.n_mines)

    for node, value in board.reveal_node(initial):
        solution.grid.nodes[node]['solved'] = True
        solution.grid.nodes[node]['value'] = value

    depth = 0
    for i in range(10000):
        revealed_len = 0
        for node, value in board.reveal_nodes(sat_inspect_generator(solution, depth=depth)):
            solution.grid.nodes[node]['solved'] = True
            solution.grid.nodes[node]['value'] = value
            revealed_len += 1
        if revealed_len == 0:
            if depth < max_depth:
                depth += 1
            else:
                break
        else:
            depth = 0

    for i in range(1000):
        remainder_solved = solve_remainder(solution, cutoff=remainder_cutoff)
        revealed_len = 0
        for node, value in board.reveal_nodes(remainder_solved):
            solution.grid.nodes[node]['solved'] = True
            solution.grid.nodes[node]['value'] = value
            revealed_len += 1
        if revealed_len == 0:
            break

    return solution


def check_solution(board, solution):
    has_unsolved = False
    for n in board.grid.nodes:
        node = solution.grid.nodes[n]
        if node['solved']:
           if node['value'] == -1 and not node['flagged']:
               return -1
        elif node['value'] != -1:
            has_unsolved = True

    return 0 if has_unsolved else 1


def generate_fair_board(n_rows, n_cols, n_mines, initial, max_depth=1, remainder_cutoff=16, max_attempts=1000):
    for i in range(max_attempts):
        candidate = generate_fun_board(n_rows, n_cols, n_mines, initial, max_attempts=1000)
        solution = solve(candidate, initial, max_depth=max_depth, remainder_cutoff=remainder_cutoff)
        if check_solution(candidate, solution) == 1:
            candidate.reset_reveals()
            print('Generated fair board in ' + str(i + 1) + ' attempts.')
            return candidate
    print('Could not generate fair board.')
    return generate_fun_board(n_rows, n_cols, n_mines, initial)


def update_solution(solution, revealed):
    for node, value in revealed:
        solution.grid.nodes[node]['solved'] = True
        solution.grid.nodes[node]['value'] = value

def update_solutions(solutions: tuple[Solution, ...], revealed):
    for node, value in revealed:
        for solution in solutions:
            solution.grid.nodes[node]['solved'] = True
            solution.grid.nodes[node]['value'] = value
