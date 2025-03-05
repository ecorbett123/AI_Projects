import time
import math
import sys

from BaseAI import BaseAI

sys.setrecursionlimit(10**6)

# Agent to solve 2048, using heuristics and min-max search algorithm

def h_free_cells(grid):
    length = len(grid.getAvailableCells())
    return 0 if length == 0 else length


def h_weight_higher_values(grid):
    if grid.getMaxTile() == 2048:
        return 100
    return 0


def h_max_tile_on_edge(grid):
    max = grid.getMaxTile()
    return 0 if grid.map[0][3] != max else 1


def get_next_tile_val(board, x, y, direction):
    # next non-zero tile in a given direction
    if direction == 0:
        for i in range(1, 3):
            if x+i < 4 and board[x + i][y] != 0:
                return math.log2(board[x + i][y])
    elif direction == 1:
        for i in range(1, 3):
            if x-i >= 0 and board[x - i][y] != 0:
                return math.log2(board[x - i][y])
    elif direction == 2:
        for i in range(1, 3):
            if y+i < 4 and board[x][y+i] != 0:
                return math.log2(board[x][y+i])
    elif direction == 3:
        for i in range(1, 3):
            if y-i >= 0 and board[x][y-i] != 0:
                return math.log2(board[x][y-i])
    return 0


# want to emphasize having same tile or half tile next to a tile
# penalize when greater than half distance between tile
def h_monotonicity(board):
    mono = [0, 0, 0, 0]
    for x in range(4):
        # left/right
        for current in range(3):
            if board[x][current] != 0:
                next_tile = get_next_tile_val(board, x, current, 2)
                cur_val = 0 if board[x][current] == 0 else math.log2(board[x][current])
                if next_tile > cur_val:
                    mono[0] += cur_val - next_tile
                elif next_tile < cur_val:
                    mono[1] += next_tile - cur_val
    for y in range(4):
        # up/down
        for current in range(3):
            if board[current][y] != 0:
                next_tile = get_next_tile_val(board, current, y, 0)
                cur_val = 0 if board[current][y] == 0 else math.log2(board[current][y])
                if next_tile > cur_val:
                    mono[2] += cur_val - next_tile
                elif next_tile < cur_val:
                    mono[3] += next_tile - cur_val

    return max(mono[0], mono[1]) + max(mono[2], mono[3])


# get all cubes around each cube and take their difference
def h_smoothness(board):
    smooth = 0
    looking = True
    for x in range(4):
        for y in range(4):
            if board[x][y] != 0:
                tile_val = math.log2(board[x][y])
                # check tile to the right
                i = 1
                while (y + i) < 4 and looking:
                    if board[x][y+i] != 0:
                        smooth -= abs(math.log2(board[x][y+i]) - tile_val)
                        looking = False
                    i += 1

                # check below tile
                looking = True
                i = 1
                while (x - i) >= 0:
                    if board[x-i][y] != 0:
                        smooth -= abs(math.log2(board[x - i][y]) - tile_val)
                        looking = False
                        break
                    i += 1
    return smooth


def h_average_tile(board):
    avg = 0
    nums = 0
    for x in range(4):
        for y in range(4):
            if board[x][y] != 0:
                if x < 2:
                    avg += math.log2(board[x][y])
                    nums += 1
    return 0 if nums == 0 else avg/nums

MOVE_ORDER = [1, 3, 2, 0]


class IntelligentAgent(BaseAI):

    def __init__(self):
        self.time = 0
        self.w1 = 2
        self.w2 = 4.7
        self.w3 = 1.2
        self.w4 = 1.1

    def evaluate_state(self, grid):
        board = grid[1]
        return .5*h_monotonicity(board.map) + 1*h_max_tile_on_edge(board) + h_free_cells(board) + h_weight_higher_values(board)

    def getMove(self, grid):
        self.time = time.process_time()
        if grid.getMaxTile() == 2048:
            return 0
        board, util = self.maximize((0, grid), -10000, 10000, 0)
        return board[0]

    # Maximize the possible utility returned using alpha-beta pruning
    # Returns tuple with state of board and utility
    def maximize(self, grid, alpha, beta, depth):
        depth += 1
        available_moves = grid[1].getAvailableMoves()
        available_moves = [move for x in MOVE_ORDER for move in available_moves if move[0] == x and grid[1].canMove([move[0]])]
        cur_time = time.process_time() - self.time
        if len(available_moves) < 1 or depth > 5 or cur_time >= 0.1:
            return grid, self.evaluate_state(grid)

        max_child, max_util = None, -100000
        for child in available_moves:
            # get the minimum board value returned for this child
            new_grid_1, min_util_2 = self.minimize(child, alpha, beta, depth, 2)
            new_grid_2, min_util_4 = self.minimize(child, alpha, beta, depth, 4)
            min_util = (.9*min_util_2) + (.1*min_util_4)
            if min_util > max_util:
                max_child, max_util = child, min_util

            if max_util >= beta:
                return max_child, max_util

            alpha = max(alpha, max_util)

        return max_child, max_util

    def minimize(self, grid, alpha, beta, depth, tile):
        depth += 1
        available_moves = grid[1].getAvailableCells()
        cur_time = time.process_time() - self.time
        if len(available_moves) < 1 or cur_time >= 0.1 or depth > 5:
            return grid, self.evaluate_state(grid)

        min_child, min_util = None, 100000
        for cell in available_moves:
            next_grid = grid[1].clone()
            next_grid.insertTile(cell, tile)
            child = (5, next_grid)
            new_grid, max_util = self.maximize(child, alpha, beta, depth)
            if max_util < min_util:
                min_child, min_util = child, max_util

            if min_util <= alpha:
                return min_child, min_util

            beta = min(beta, min_util)

        return min_child, min_util
