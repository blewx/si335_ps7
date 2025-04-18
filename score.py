#!/usr/bin/python3

# SI 335 Algorithms, Spring 2025
# Problem Set 7 Helper code
#
# This program scores the given map and moves, without actually
# displaying everything.

import argparse
import sys
import curses
import time
import collections

from show import World, read_moves

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description="Compute score for given moves in given map")
    parser.add_argument("mapfile", type=argparse.FileType('r'),
            help="filename of the map")
    parser.add_argument("movesfile", type=argparse.FileType('r'),
            help="filename of the moves")
    args = parser.parse_args()

    # read in the map
    world = World(args.mapfile)

    # read in moves
    moves = read_moves(args.movesfile, world.nasset)

    # calculate the score
    for move in moves:
        if not world.active(): break
        msgs, status = world.move(move)
        for msg in msgs:
            print(msg, file=sys.stderr)

    remasset = len(world.assets) - len(world.dead)
    remtarg = len(world.targets)

    if remasset:
        print("Finished with {} assets remaining".format(remasset), file=sys.stderr)
    else:
        print("All assets were lost", file=sys.stderr)

    if remtarg:
        print("Finished with {} targets remaining".format(remtarg), file=sys.stderr)
    else:
        print("All targets were destroyed", file=sys.stderr)

    print(world.score)

if __name__ == '__main__':
    main()
