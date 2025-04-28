#!/usr/bin/env python3

'''
plan.py
si335 - problem set 7 part 4
Brendan Lewis, Hunter Shook, Richard Kang, Ian Coffey

Our solution to the pathfinding problem was to use the A* algorithm to find the
shortest path to the each remaining target on the board, and then make a greedy 
choice that picked the highest value comparing all remaining targets / the path length
the asset would need to travel in order to reach the target. Once a target is chosen,
the algorithm will plan a route to that target, and then return the path to the target.
The algorithm will then move the asset one step towards the target, and repeat
the process until all targets are captured or all assets are dead.

A few rules that we implemented were that assets never choose the same target unless
it's the last target, and that if an asset reaches a target it will check to see if it is
closer to a target that another asset is going for. If it is, then we want to clear the 
other asset's route.


Resources: 
Coding concepts learned in Intelligent Robotics 
https://www.geeksforgeeks.org/a-search-algorithm/
https://www.geeksforgeeks.org/a-search-algorithm-in-python/
https://brilliant.org/wiki/a-star-search/
https://realpython.com/python-deque/
https://realpython.com/python-heapq-module/
https://www.geeksforgeeks.org/python-collections-module/
https://www.geeksforgeeks.org/fractional-knapsack-problem/

'''

import sys
from collections import deque
import heapq
from show import World            

# Returns the distance between two points
def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

#Checks if a point is within the bounds of the grid
def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

# Returns the direction characters and x,y movement vectors of a point/square in the grid
def neighbors():
    return [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]

# Sum up values of any targets on the path
def collectable_value_on_path(path, target_values):
    total = 0
    for square in path:
        total += target_values.get(square, 0)
    return total

"""
Standard A* algorithm, created using pseudocode from geeksforgeeks and 
from the A* project in AI, modified to fit the needs of this project.

The algorithm is used to find the shortest path from the start square to the goal square
"""
def astar(start, goal, rows, cols, blocked):
    # If we are already on the goal square, there is no path to get there 
    # so we want to just return an empty list
    if start == goal:
        return []

    # The open list is a heap storing (f_cost, g_cost, square_position)
    h0 = manhattan(start, goal)          # guess cost from start to goal
    open_heap = [(h0, 0, start)]         # we start with only the start square

    g_cost = {start: 0}                  # cheapest known cost to each square
    parent = {}                          # how we got to a square
    closed = set()                       # squares already fully checked
    
    # loop while we still have squares to try
    while open_heap:                     
        _, g_now, curr_square = heapq.heappop(open_heap)  # pick the square with best score

        #If we are at the goal square, we want to return the path to get there
        if curr_square == goal:                  
            path = []
            while curr_square != start:
                path.append(curr_square)
                curr_square = parent[curr_square]
            path.reverse()
            return path                  

        # mark square as checked/visited
        closed.add(curr_square)       

        # look at the 4 neighbors of the current square
        for row_vector, column_vector, _ in neighbors():
            new_row, new_col = curr_square[0] + row_vector, curr_square[1] + column_vector
            nxt_sqr = (new_row, new_col)

            # skip if out of board, blocked, or already done
            if (not in_bounds(new_row, new_col, rows, cols) or
                    nxt_sqr in blocked or
                    nxt_sqr in closed):
                continue

            new_g = g_now + 1            # cost to move 1 step

            # if this new tile is closer to the goal than the other options of the 4 cardinal directions,
            # we want to update the cost and add it to the open list
            if new_g < g_cost.get(nxt_sqr, 1 << 30):
                g_cost[nxt_sqr] = new_g
                parent[nxt_sqr] = curr_square
                f = new_g + manhattan(nxt_sqr, goal)
                heapq.heappush(open_heap, (f, new_g, nxt_sqr))

    return []                            # no path found



# Class that represents the an asset on the board
class Asset:
    # Maps movemment tupples to letters
    move_letter = {(-1, 0): 'U', (1, 0): 'D', (0, -1): 'L', (0, 1): 'R'}

    def __init__(self, start_square):
        self.pos = list(start_square)    # current square
        self.route = deque()             # squares left until we get to the target
        self.alive = True               # set false if the asset dies or is trapped
    
    #Returns the path to the destination square
    def destination(self):
        return self.route[-1] if self.route else None

    #Pick best target and store shortest route to it.
    def plan(self, targets, rows, cols, obstacles, reserved):
        #If all targets have been captured, clear the route and exit the program.
        if not targets:
            self.route.clear() 
            return
        
        many_left = len(targets) > 1
        best_path, best_score = None, -1

        for target, value in targets.items():
            if many_left and target in reserved:    # skip squares another asset is moving towards
                continue
            path = astar(tuple(self.pos), target, rows, cols, obstacles)
            
            if path:
                # compute total points if we collect all targets on the way
                gain = collectable_value_on_path(path, targets)
                score = gain / len(path)    # points per move - Tried to do this with subtraction, but it was not nearly as good.
                                            # this forces the alogorithm to choose targets that are closer to the asset at first
                if score > best_score:
                    best_path, best_score = path, score
        
        # if nothing free was reachable, look at the targets that are being chased by other assets
        if best_path is None:
            for target in targets:
                path = astar(tuple(self.pos), target, rows, cols, obstacles)
                if path:
                    best_path = path; break
        self.route = deque(best_path or [])

    # take the next step in the route
    # return the letter of that move
    def step(self, rows, cols, obstacles):
        
        if not self.alive or not self.route:
            return 'U'                  # move up if dead or no route
        nxt = self.route.popleft() #nxt is equal to the next square in the route
        row_vector, col_vector = nxt[0] - self.pos[0], nxt[1] - self.pos[1]
        self.pos[:] = nxt               # update position of the asset
        if nxt in obstacles or not in_bounds(nxt[0],nxt[1], rows, cols):
            self.alive = False          # asset died because it hit an obstacle
        return self.move_letter[(row_vector, col_vector)]


#Main function that runs the plan
def run_plan(world):
    rows, cols = world.rows, world.cols
    obstacles = world.obstacles

    # make am Asset object for each starting square in the file
    assets = [Asset(square) for square in world.assets]

    # target dict is setup as position:current value
    targets = {(r, c): val for _, (r, c, val) in world.targets.items()}

    move_lines = []                      # list of output lines we will return

    while True:
        # only keep targets that are still worth points
        good_targets = {square: value for square, value in targets.items() if value > 0}
        living = [asset for asset in assets if asset.alive] # check to see which assets are still alive and add them to the list - living
        if not good_targets or not living:
            break                        # if all assets are dead or all targets are gone, the program can end

        # adds the target squares that assets are going for to a set
        reserved = {asset.destination() for asset in living if asset.destination()}

        # Check to make sure that the asset is not already on a target square, if it is,
        # we want to now plan a new route to a different target
        for asset in living:
            if not asset.route or targets.get(asset.destination(), 0) <= 0:
                asset.plan(good_targets, rows, cols, obstacles, reserved)
            if not asset.route:
                asset.alive = False         #assume asset is dead if it has no route to a target

        # move every asset one step and append the move to the output
        move_lines.append(''.join(asset.step(rows, cols, obstacles) for asset in assets))

        # check to see if any assets have captured a target
        captured = []
        for asset in assets:
            key = tuple(asset.pos) # make the square a tuple so it can be used as a key
            if asset.alive and targets.get(key, 0) > 0: #if no target is found then the value returned by the get function is 0 so we ignore it
                targets[key] = 0
                captured.append(asset)

        #If an asset has just captured a target, we want to check to see if that asset is closer
        # to a target that another asset is going for. If it is, then we want to clear the other asset's route
        # so that when we recompute routes the first asset can go for the target
        for cap in captured:
            for other in assets:
                if other is cap or not other.destination() or not other.alive:
                    continue
                new_path = astar(tuple(cap.pos), other.destination(), rows, cols, obstacles)
                if new_path and len(new_path) < len(other.route):
                    cap.route = deque(new_path)
                    other.route.clear()
                    break

        # simulate the loss of a point each step we take
        for square in targets:
            targets[square] = max(0, targets[square] - 1)

    return move_lines



def main():
    try:
        map_name   = input("Map file  : ").strip()
        moves_name = input("Moves file: ").strip()
    except EOFError:
        sys.exit("No names given")

    with open(map_name, 'r') as fh:
        world = World(fh)

    moves = run_plan(world)

    with open(moves_name, 'w') as out:
        out.write('\n'.join(moves))

if __name__ == '__main__':
    main()
