#!/usr/bin/env python
#coding:utf-8

"""
Each sudoku board is represented as a dictionary with string keys and
int values.
e.g. my_board['A1'] = 8
"""
import math
import sys
import time

ROW = "ABCDEFGHI"
COL = "123456789"

def print_board(board):
    """Helper function to print board in a square."""
    print("-----------------")
    for i in ROW:
        row = ''
        for j in COL:
            row += (str(board[i + j]) + " ")
        print(row)


def board_to_string(board):
    """Helper function to convert board dictionary to string for writing."""
    ordered_vals = []
    for r in ROW:
        for c in COL:
            ordered_vals.append(str(board[r + c]))
    return ''.join(ordered_vals)


def backtracking(board):
    """Takes a board and returns solved board."""
    if is_complete_board(board):
        return board

    # build initial map that maps location to domain
    domain_map = get_domain_map(board)
    if not domain_map:
        return None
    location = get_min_domain(domain_map)

    for value in domain_map[location]:
        board[location] = value
        result = backtracking(board)
        if result == board:
            return result
        board[location] = 0

    return None

def get_domain_map(board):
    domain_map = {}
    for location in board.keys():
        if board[location] == 0:
            domain = set()
            for i in range(1, 10):
                if is_valid_move(board, location, i):
                    domain.add(i)
            if len(domain) < 1:
                return None
            domain_map[location] = domain

    return domain_map


def get_min_domain(domain_map):
    min_location = ""
    min_size = 10
    for location in domain_map.keys():
        domain_length = len(domain_map[location])
        if domain_length < min_size:
            min_size = domain_length
            min_location = location
    return min_location


# method to check validity of a board
def is_valid_move(board, location, value):
    row = location[0]
    col = location[1]

    # check row validity
    for i in range(9):
        if board[row + COL[i]] == value:
            return False
    #check column validity
    for i in range(9):
        if board[ROW[i] + col] == value:
            return False
    # check square validity
    origin_x = (ROW.index(row)//3)*3
    origin_y = (COL.index(col)//3)*3
    for i in range(3):
        for j in range(3):
            if board[ROW[origin_x+i] + COL[origin_y+j]] == value:
                return False
    return True


# check completeness of a board, returns True if completely satisfied
def is_complete_board(board):
    # check column validity
    num_set = set()
    for i in range(9):
        for j in range(9):
            val = board[ROW[i]+COL[j]]
            if val != 0:
                num_set.add(val)
            else:
                # return false because 0 found so board is not complete
                return False
        # if numbers 1-9 were not present, return false

        for j in range(1, 10):
            if j not in num_set:
                return False
        num_set.clear()

    # check row validity
    for i in range(9):
        for j in range(9):
            val = board[ROW[j]+COL[i]]
            if val != 0:
                num_set.add(val)
            else:
                # return false because 0 found so board is not complete
                return False
        # if numbers 1-9 were not present, return false

        for j in range(1, 10):
            if j not in num_set:
                return False
        num_set.clear()

    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            for k in range(3):
                for m in range(3):
                    val = board[ROW[i+k]+COL[j+m]]
                    if val != 0:
                        num_set.add(val)
                    else:
                        return False
            for j in range(1, 10):
                if j not in num_set:
                    return False
            num_set.clear()

    return True

if __name__ == '__main__':
    if len(sys.argv) > 1:
        
        # Running sudoku solver with one board $python3 sudoku.py <input_string>.
        print(sys.argv[1])
        # Parse boards to dict representation, scanning board L to R, Up to Down
        board = { ROW[r] + COL[c]: int(sys.argv[1][9*r+c])
                  for r in range(9) for c in range(9)}       
        
        solved_board = backtracking(board)
        
        # Write board to file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")
        outfile.write(board_to_string(solved_board))
        outfile.write('\n')

    else:
        # Running sudoku solver for boards in sudokus_start.txt $python3 sudoku.py

        #  Read boards from source.
        src_filename = 'sudokus_start.txt'
        try:
            srcfile = open(src_filename, "r")
            sudoku_list = srcfile.read()
        except:
            print("Error reading the sudoku file %s" % src_filename)
            exit()

        # # Setup output file
        out_filename = 'output.txt'
        outfile = open(out_filename, "w")

        run_times = []
        num_solved = 0
        max_time = 0
        min_time = 10000
        # Solve each board using backtracking
        for line in sudoku_list.split("\n"):
            if len(line) < 9:
                continue

            # Parse boards to dict representation, scanning board L to R, Up to Down
            board = { ROW[r] + COL[c]: int(line[9*r+c])
                      for r in range(9) for c in range(9)}

            # Print starting board. Comment this out when timing runs.
            #print_board(board)

            # Solve with backtracking
            start_time = time.time()
            solved_board = backtracking(board)
            end_time = time.time()
            total_time = end_time - start_time
            # Print solved board. Comment this out when timing runs.
            #print_board(solved_board)
            if solved_board:
                num_solved += 1
                if total_time > max_time:
                    max_time = total_time
                if total_time < min_time:
                    min_time = total_time
                run_times.append(total_time)
            # # Write board to file
            outfile.write(board_to_string(solved_board))
            outfile.write('\n')

        # Code to write out timing statistics
        # read_me = 'README.txt'
        # read_me_file = open(read_me, "w")
        # read_me_file.write("Number of boards solved: " + str(num_solved) + "\n")
        # read_me_file.write("Maximum: " + str(round(max_time, 8)) + "\n")
        # read_me_file.write("Minimum: " + str(round(min_time, 8)) + "\n")
        # total_sum = 0
        # for time in run_times:
        #     total_sum += time
        # mean = total_sum/num_solved
        # std_sum = 0
        # for time in run_times:
        #     std_sum += (time - mean)**2
        # std_deviation = math.sqrt(std_sum/num_solved)
        # read_me_file.write("Mean: " + str(round(mean, 8)) + "\n")
        # read_me_file.write("Standard Deviation: " + str(round(std_deviation, 8)) + "\n")

        print("Finishing all boards in file.")