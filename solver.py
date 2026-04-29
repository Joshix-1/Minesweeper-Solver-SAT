import traceback
import random
import itertools as it

import networkx as nx
from bidict import bidict
from pysat.formula import CNF
from pysat.solvers import Minisat22


class Solution:
    def __init__(self, n_rows, n_cols, n_mines):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_mines = n_mines
        self.n_unsolved_mines = n_mines

        self.grid = nx.grid_2d_graph(n_rows, n_cols)
        self.grid.add_edges_from([
                                     ((x, y), (x + 1, y + 1))
                                     for x in range(n_rows - 1)
                                     for y in range(n_cols - 1)
                                 ] + [
                                     ((x + 1, y), (x, y + 1))
                                     for x in range(n_rows - 1)
                                     for y in range(n_cols - 1)
                                 ], weight=1.4)

        for n in self.grid.nodes:
            self.grid.nodes[n]['solved'] = False
            self.grid.nodes[n]['value'] = 0
            self.grid.nodes[n]['flagged'] = False

        self.nodes = list(self.grid.nodes)

    def __str__(self):
        string = ''
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.grid.nodes[i, j]['solved']:
                    if self.grid.nodes[i, j]['value'] == -1:
                        if self.grid.nodes[i, j]['flagged']:
                            string = string + '.'
                        else:
                            string = string + '*'
                    else:
                        if self.grid.nodes[i, j]['value'] == 0:
                            string = string + ' '
                        else:
                            string = string + str(self.grid.nodes[i, j]['value'])
                else:
                    string = string + '-'
            string = string + '\n'
        return string


def sat_inspect_cell(solution, source, depth=1):
    # if node has not been solved, it has no information
    if not solution.grid.nodes[source]['solved']:
        return

    # determine all nodes in the border and their adjacent unsolved nodes
    dfs_tree = nx.dfs_tree(solution.grid, source, depth_limit=depth)
    unknown_nodes = set()
    border_nodes = {
        n
        for n in dfs_tree.nodes
        if solution.grid.nodes[n]['solved'] and sum(
            1
            for m in solution.grid.neighbors(n)
            if not solution.grid.nodes[m]['solved'] and (unknown_nodes.add(m) or True)
        )
    }
    if len(border_nodes) == 0:
        try:
            solution.nodes.remove(source)
        except Exception:
            traceback.print_exc()
        return

    # map all unknown nodes to boolean variable indices
    variable_by_node = bidict()
    variable = 1
    for n in unknown_nodes:
        variable_by_node[n] = variable
        variable += 1

    # using values of border nodes, construct CNF expression
    cnf = CNF()
    for n in border_nodes:
        node = solution.grid.nodes[n]
        if node['value'] == -1:
            continue

        adj = list(solution.grid.neighbors(n))
        adj_unknown = (m for m in adj if not solution.grid.nodes[m]['solved'])
        adj_mine = (m for m in adj if solution.grid.nodes[m]['solved'] and solution.grid.nodes[m]['value'] == -1)

        variables = [variable_by_node[m] for m in adj_unknown]

        mines_total = node['value']
        mines_needed = mines_total - sum(1 for _ in adj_mine)

        left_combinations = it.combinations(variables, len(variables) + 1 - mines_needed)
        right_combinations = it.combinations(variables, 1 + mines_needed)


        for lc in left_combinations:
            cnf.append(lc)
        for rc in right_combinations:
            cnf.append([-1 * x for x in rc])

    # exhaust solutions to CNF expression with pysat
    solutions = []
    for i in range(100000):
        with Minisat22(bootstrap_with=cnf.clauses) as solver:
            has_solution = solver.solve()
            model = solver.get_model()
        if has_solution:
            cnf.append([-1 * x for x in model])
            solutions.append(model)
        else:
            break

    # find all variables which have only one value over all solutions to CNF
    if solutions:
        for j, first in enumerate(solutions[0]):
            certain = True
            for s in solutions:
                if not s[j] == first:
                    certain = False
                    break
            if certain:
                v = first
                node = variable_by_node.inv[abs(v)]
                yield node
                if v > 0:
                    solution.grid.nodes[node]['flagged'] = True


def sat_inspect_generator(solution, depth=1):
    random.shuffle(solution.nodes)
    for n in solution.nodes or solution.grid.nodes:
        yield from sat_inspect_cell(solution, n, depth=depth)


def solve_remainder(solution, cutoff=16):
    global_mines_solved = sum(
        1
        for n in solution.grid.nodes
        if solution.grid.nodes[n]['solved'] and solution.grid.nodes[n]['value'] == -1)
    global_mines_needed = solution.n_mines - global_mines_solved

    border_nodes = {
        n
        for n in solution.grid.nodes
        if solution.grid.nodes[n]['solved'] and any(not solution.grid.nodes[m]['solved'] for m in solution.grid.neighbors(n))
    }
    unknown_nodes = {
        n
        for n in solution.grid.nodes
        if not solution.grid.nodes[n]['solved']
    }

    if len(unknown_nodes) <= cutoff:
        variable_by_node = bidict()
        variable = 1
        for n in unknown_nodes:
            variable_by_node[n] = variable
            variable += 1

        cnf = CNF()

        global_left_combinations = set(it.combinations(list(variable_by_node.values()),
                                                       len(unknown_nodes) + 1 - global_mines_needed))
        global_right_combinations = set(it.combinations(list(variable_by_node.values()), 1 + global_mines_needed))
        for glc in global_left_combinations:
            cnf.append(glc)
        for grc in global_right_combinations:
            cnf.append([-1 * grc[i] for i in range(len(grc))])

        for n in border_nodes:
            if solution.grid.nodes[n]['value'] == -1:
                continue

            adj = list(solution.grid.neighbors(n))
            adj_unknown = [m for m in adj if not solution.grid.nodes[m]['solved']]
            adj_mine = [m for m in adj if solution.grid.nodes[m]['solved'] and solution.grid.nodes[m]['value'] == -1]

            variables = [variable_by_node[m] for m in adj_unknown]

            mines_total = solution.grid.nodes[n]['value']
            mines_needed = mines_total - len(adj_mine)

            left_combinations = set(it.combinations(variables, len(adj_unknown) + 1 - mines_needed))
            right_combinations = set(it.combinations(variables, 1 + mines_needed))

            for lc in left_combinations:
                cnf.append(lc)
            for rc in right_combinations:
                cnf.append([-1 * rc[i] for i in range(len(rc))])

        solutions = []
        for i in range(100000):
            with Minisat22(bootstrap_with=cnf.clauses) as solver:
                has_solution = solver.solve()
                model = solver.get_model()
            if has_solution:
                cnf.append([-1 * model[i] for i in range(len(model))])
                solutions.append(model)
            else:
                break

        discovered_variables = []
        for j in range(len(solutions[0])):
            certain = True
            first = solutions[0][j]
            for i in range(len(solutions)):
                if not solutions[i][j] == first:
                    certain = False
                    break
            if certain:
                discovered_variables.append(first)

        # return newly solved nodes
        solved_nodes = []
        for v in discovered_variables:
            node = variable_by_node.inv[abs(v)]
            solved_nodes.append(node)
            if v > 0:
                solution.grid.nodes[node]['flagged'] = True
            #solution.grid.nodes[node]['solved'] = True
        return solved_nodes
    else:
        return []


def is_complete(solution):
    for n in solution.grid.nodes:
        if not solution.grid.nodes[n]['solved']:
            return False
    return True
