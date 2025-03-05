from __future__ import division
from __future__ import print_function

import sys
import math
import time
import queue as Q
import resource

sys.setrecursionlimit(10**6)
class Solver(object):
    """
        The Solver takes the end state of a game and returns the necessary
        stats on the game run
    """
    def __init__(self, state, frontier_size, max_search_depth, run_time, max_ram_usage):
        """
        :param state -> last run state of PuzzleGame

        """
        self.state = state
        self.path_to_goal = []
        self.cost_of_path = state.cost
        self.nodes_expanded = frontier_size
        self.search_depth = state.cost
        self.max_search_depth = max_search_depth
        self.running_time = run_time
        self.max_ram_usage = max_ram_usage

    def get_path_to_goal(self, state):
        if state.action == "Initial":
            return
        self.path_to_goal.insert(0, state.action)
        self.get_path_to_goal(state.parent)

    def solve(self):
        self.get_path_to_goal(self.state)

## The Class that Represents the Puzzle
class PuzzleState(object):
    """
        The PuzzleState stores a board configuration and implements
        movement instructions to generate valid children.
    """
    def __init__(self, config, n, parent=None, action="Initial", cost=0):
        """
        :param config->List : Represents the n*n board, for e.g. [0,1,2,3,4,5,6,7,8] represents the goal state.
        :param n->int : Size of the board
        :param parent->PuzzleState
        :param action->string
        :param cost->int
        """
        if n*n != len(config) or n < 2:
            raise Exception("The length of config is not correct!")
        if set(config) != set(range(n*n)):
            raise Exception("Config contains invalid/duplicate entries : ", config)

        self.n        = n
        self.cost     = cost
        self.parent   = parent
        self.action   = action
        self.config   = config
        self.children = []

        # Get the index and (row, col) of empty block
        self.blank_index = self.config.index(0)

    def display(self):
        """ Display this Puzzle state as a n*n board """
        for i in range(self.n):
            print(self.config[3*i : 3*(i+1)])

    def move_up(self):
        """ 
        Moves the blank tile one row up.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index > 2 and self.action != "Down":
            new_config = self.config.copy()
            new_config[self.blank_index] = new_config[self.blank_index-3]
            new_config[self.blank_index-3] = 0
            new_cost = self.cost + 1
            return PuzzleState(new_config, self.n, self,  "Up", new_cost)

        return None
      
    def move_down(self):
        """
        Moves the blank tile one row down.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index < 6 and self.action != "Up":
            new_config = self.config.copy()
            new_config[self.blank_index] = new_config[self.blank_index + 3]
            new_config[self.blank_index + 3] = 0
            new_cost = self.cost + 1
            return PuzzleState(new_config, self.n, self, "Down", new_cost)

        return None
      
    def move_left(self):
        """
        Moves the blank tile one column to the left.
        :return a PuzzleState with the new configuration
        """
        if self.blank_index % 3 != 0 and self.action != "Right":
            new_config = self.config.copy()
            new_config[self.blank_index] = new_config[self.blank_index - 1]
            new_config[self.blank_index - 1] = 0
            new_cost = self.cost + 1
            return PuzzleState(new_config, self.n, self, "Left", new_cost)

        return None

    def move_right(self):
        """
        Moves the blank tile one column to the right.
        :return a PuzzleState with the new configuration
        """
        if (self.blank_index+1) % 3 != 0 and self.action != "Left":
            new_config = self.config.copy()
            new_config[self.blank_index] = new_config[self.blank_index + 1]
            new_config[self.blank_index + 1] = 0
            new_cost = self.cost + 1
            return PuzzleState(new_config, self.n, self, "Right", new_cost)

        return None
      
    def expand(self):
        """ Generate the child nodes of this node """
        
        # Node has already been expanded
        if len(self.children) != 0:
            return self.children
        
        # Add child nodes in order of UDLR
        children = [
            self.move_up(),
            self.move_down(),
            self.move_left(),
            self.move_right()]

        # Compose self.children of all non-None children states
        self.children = [state for state in children if state is not None]
        return self.children

    def __lt__(self, other):
        self_h = calculate_manhattan_dist(self) + self.cost
        other_h = calculate_manhattan_dist(other) + other.cost
        if self_h == other_h:
            moves = ["Up", "Down", "Left", "Right"]
            return moves.index(self.action) < moves.index(other.action)
        else:
            return self_h < other_h

    def __eq__(self, other):
        return "".join(str(num) for num in self.config) == "".join(str(num) for num in other.config)


# Function that Writes to output.txt
def writeOutput(solver):
    output_file = open("output.txt", "w+")
    output_file.write("path_to_goal: " + str(solver.path_to_goal) + "\n")
    output_file.write("cost_of_path: " + str(solver.cost_of_path) + "\n")
    output_file.write("nodes_expanded: " + str(solver.nodes_expanded) + "\n")
    output_file.write("search_depth: " + str(solver.cost_of_path) + "\n")
    output_file.write("max_search_depth: " + str(solver.max_search_depth) + "\n")
    run_time = str(round(solver.running_time, 8))
    if "." in run_time:
        sub_string = run_time[run_time.index("."):]
        while len(sub_string) < 9:
            sub_string = sub_string + "0"
    else:
        sub_string = ".00000000"
    run_time = run_time[0:run_time.index(".")] + sub_string
    output_file.write("running_time: " + run_time + "\n")
    max_ram = str(round(solver.max_ram_usage, 8))
    if "." in max_ram:
        sub_string = max_ram[max_ram.index("."):]
        while len(sub_string) < 9:
            sub_string = sub_string + "0"
    else:
        sub_string = ".00000000"
    max_ram = max_ram[0:max_ram.index(".")] + sub_string
    output_file.write("max_ram_usage: " + max_ram + "\n")
    pass

def bfs_search(initial_state):
    """BFS search"""
    start_time = time.time()
    dfs_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = Q.Queue()
    frontier.put(initial_state)
    board = "".join(str(num) for num in initial_state.config)
    frontier_set = set()
    frontier_set.add(board)
    explored = set()
    nodes_expanded = 0
    max_cost = 0

    while frontier.qsize() > 0:
        state = frontier.get()
        state_board = "".join(str(num) for num in state.config)
        frontier_set.remove(state_board)
        explored.add(state_board)

        # if find end goal state
        if test_end_goal(state, nodes_expanded, max_cost, dfs_start_ram, start_time):
            return

        nodes_expanded += 1
        for child in state.expand():
            child_board = "".join(str(num) for num in child.config)
            if child_board not in frontier_set and child_board not in explored:
                if child.cost > max_cost:
                    max_cost = child.cost
                frontier.put(child)
                frontier_set.add(child_board)

    return

def dfs_search(initial_state):
    """DFS search"""
    start_time = time.time()
    dfs_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = [initial_state]
    board = "".join(str(num) for num in initial_state.config)
    frontier_set = set()
    frontier_set.add(board)
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while len(frontier) > 0:
        state = frontier.pop()
        state_board = "".join(str(num) for num in state.config)
        frontier_set.remove(state_board)

        explored.add(state_board)

        if test_end_goal(state, nodes_expanded, max_search_depth, dfs_start_ram, start_time):
            return

        expanded = state.expand()
        expanded.reverse()
        nodes_expanded += 1
        for child in expanded:
            child_board = "".join(str(num) for num in child.config)
            if child_board not in frontier_set and child_board not in explored:
                if child.cost > max_search_depth:
                    max_search_depth = child.cost
                frontier.append(child)
                frontier_set.add(child_board)

    return

def A_star_search(initial_state):
    """A * search"""
    start_time = time.time()
    dfs_start_ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    frontier = Q.PriorityQueue()
    frontier.put(initial_state)

    initial_board = "".join(str(num) for num in initial_state.config)
    mhd_initial_state = calculate_manhattan_dist(initial_state)
    frontier_to_cost_map = {initial_board: mhd_initial_state}
    explored = set()
    nodes_expanded = 0
    max_search_depth = 0

    while frontier.qsize() > 0:
        state = frontier.get()
        state_board = "".join(str(num) for num in state.config)
        if state_board not in explored:
            explored.add(state_board)

            if test_end_goal(state, nodes_expanded, max_search_depth, dfs_start_ram, start_time):
                return

            nodes_expanded += 1
            for child in state.expand():
                child_board = "".join(str(num) for num in child.config)
                child_h = calculate_manhattan_dist(child) + child.cost
                if child_board not in frontier_to_cost_map.keys() and child_board not in explored:
                    if child.cost > max_search_depth:
                        max_search_depth = child.cost
                    frontier.put(child)
                    frontier_to_cost_map[child_board] = child_h
                elif child_board in frontier_to_cost_map.keys():
                    if child_h < frontier_to_cost_map.get(child_board):
                        frontier.put(child)
                        frontier_to_cost_map[child_board] = child_h
        explored.add(state_board)

    return

def test_end_goal(state, nodes_expanded, max_search_depth, dfs_start_ram, start_time):
    if test_goal(state):
        end_time = time.time()
        dfs_ram = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - dfs_start_ram) / (2 ** 20)
        solver = Solver(state, nodes_expanded, max_search_depth, end_time - start_time, dfs_ram)
        solver.solve()
        writeOutput(solver)
        return True

    return False

def calculate_total_cost(state):
    """calculate the total estimated cost of a state"""
    pass

def calculate_manhattan_dist(state):
    """calculate the manhattan distance of a state"""
    mhd = 0
    index = 0
    while index < 9:
        if state.config[index] != 0:
            difference = abs(state.config[index] - index)
            mhd += (difference % 3)
            mhd += (difference//3)
        index += 1

    return mhd

def test_goal(puzzle_state):
    """test the state is the goal state or not"""
    index = 0
    for num in puzzle_state.config:
        if index != num:
            return False
        index += 1
    return True

# Main Function that reads in Input and Runs corresponding Algorithm
def main():
    search_mode = sys.argv[1].lower()
    begin_state = sys.argv[2].split(",")
    begin_state = list(map(int, begin_state))
    board_size  = int(math.sqrt(len(begin_state)))
    hard_state  = PuzzleState(begin_state, board_size)
    start_time  = time.time()

    if   search_mode == "bfs": bfs_search(hard_state)
    elif search_mode == "dfs": dfs_search(hard_state)
    elif search_mode == "ast": A_star_search(hard_state)
    else:
        print("Enter valid command arguments !")
        
    end_time = time.time()
    print("Program completed in %.3f second(s)"%(end_time-start_time))

if __name__ == '__main__':
    main()

