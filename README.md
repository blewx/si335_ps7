# si335_ps7 Group 4	

Resources: 
Python concepts learned in Intelligent Robotics such as classes, class variables, init

https://www.geeksforgeeks.org/a-search-algorithm/ - Used in conjunction with the source below, and project number 1 in AI in order to get a good understanding of A* search which is the main method for finding the path length of moves
https://www.geeksforgeeks.org/a-search-algorithm-in-python/- Used in conjunction with the source above, and project number 1 in AI in order to get a good understanding of A* search which is the main method for finding the path length of moves. Some of the code concepts such as using the heapq and deque imports and how they are implemented are used in our program. 
https://realpython.com/python-deque/ - Used to better grasp the python deque library, expecially how popleft works.
https://realpython.com/python-heapq-module/ - Used to better grasp the python deque library
https://www.geeksforgeeks.org/fractional-knapsack-problem/ - One of the problems that led to the idea of doing value / path length as our greedy choice in trying to figure out the best way to choose between one node and the next

Our solution to the pathfinding problem was to use the A* algorithm which we learned 
about in the aritifial intelligence class to find the shortest path to the each remaining 
target on the board, and then make a greedy choice that picked the highest value comparing 
all remaining targets / the path length the asset would need to travel in order to reach the target.
We then made it so that this greedy choice compared the target value summed with any additional targets
that were on the path to get to the target in order to try and get paths that picked up targets if it 
didn't lower the speed at which our algorithm got to the target.
We wanted to use A* because it seemed to fit this problem well, it had a distance hueristic called
manhatten that appeared to do a good job of estimating the values, and it also was able to provide
solutions and choose targets quickly so our program finishes well within the givin time limit.
Once a target is chosen by A* search, the algorithm will plan a route to that target, 
and then return the path to the target. The algorithm will then move the asset one step towards the target,
only redoing A* search when an asset has collected his target and repeat
the process until all targets are captured or all assets are dead.

A few rules that we implemented to optimize our answer were that assets never choose the same target unless
it's the last target, and that if an asset reaches a target it will check to see if it is
closer to a target that another asset is going for. If it is, then we want to clear the 
other asset's route.
