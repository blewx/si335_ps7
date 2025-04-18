from show import World, read_moves

# SI 335 Algorithms, Spring 2025
# Problem Set 7 
# Brendan Lewis, Ian Coffey, Hunter Shook, Richard Kang


###############################################################
'''
    Sources:
        A* search idea - https://www.geeksforgeeks.org/a-search-algorithm-in-python/
        How does any work in python - https://www.datacamp.com/tutorial/python-any-function

'''


###############################################################
#This section of code is used to print error messages to stderr
import sys
import heapq

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
###############################################################




# This function takes a world object and prints the map to the screen
# It prints the obstacles as *,
# the assets as A,
# the targets as T,
# and empty spaces as a space
def print_map(world):
    for i in range(world.rows):
        for j in range(world.cols):
            if (i,j) in world.obstacles:
                print("*", end=" ")
            elif [i,j] in world.assets:
                print("A", end=" ")
            elif any((i, j) == (x, y) for (x, y, _) in world.targets.values()):
                print("T", end=" ")
            else:
                print(" ", end=" ")
        print()


#This function takes two locations on the board and returns the manhattan distance
def manhattan(a,b):
    #takes two locations on the board and returns the difference
    return abs(a[0]-b[0])+abs(a[1]-b[1])


#takes two locations on the board and returns the manhattan distance
#This funciton takes into account the obstacles in the world
#def manhattan_distance(world, a, b):
    for i in range(min(a[0],b[0]), max (a[0],b[0])):
        for j in range(min(a[1],b[1]), max (a[1],b[1])):
            if (i,j) in world.obstacles:
                return float("inf")


###############################################################
# Prims's algorithm - we want to use this to find the shortest 
# path from every start to each goal 



'''
THIS NEEDS TO BE TWEAKED SO THAT IT RETURNS THE STEPS THAT WERE
TAKEN TO GET TO EACH GOAL/TARGET
'''
def prims(starts, goals, world):
    all_seen = False
    while not all_seen:
        # Create a priority queue
        queue = []
        # Create a set to keep track of visited nodes
        visited = set()
        # Add the starting node to the queue
        for start in starts:
            heapq.heappush(queue, (0, start))
            visited.add(start)

        # Create a dictionary to keep track of the parent of each node
        parent = {}

        while queue:
            # Get the node with the lowest cost
            cost, current = heapq.heappop(queue)

            # Check if we have reached a goal
            if current in goals:
                return current

            # Get the neighbors of the current node
            neighbors = world.get_neighbors(current)

            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    heapq.heappush(queue, (cost + 1, neighbor))
                    parent[neighbor] = current
        # Check if all goals have been reached
        all_seen = True
        for goal in goals:
            if goal not in visited:
                all_seen = False
                break
    return None
###############################################################

    

    
def main():

    ###############################################################
    #Read in the map
    filename = "sample-map.txt"#input("Map: ")
    world = None
    with open(filename) as f:
        world = World(f)


    eprint("Reading in the map...")
    eprint("rows", world.rows)
    eprint("cols", world.cols)
    eprint("obstacles", world.obstacles)
    eprint("assets", world.assets)
    eprint("targets", world.targets)
    print_map(world)
    ###############################################################

    #Run prims algorithm to find the shortest path from the start to each goal
    start = world.assets[0]
    goals = world.targets #list of goals
    
    


if __name__ == "__main__":
    main()