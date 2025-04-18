#!/usr/bin/env python3

# SI 335 Algorithms, Spring 2025
# Problem Set 7 Helper code
#
# This program can be used to generate a random input map
# with obstacles, assets, and targets.

import argparse
import sys
import random

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a random map")
    parser.add_argument("rows", metavar="R", type=int, 
            help="number of rows in the map")
    parser.add_argument("cols", metavar="C", type=int, 
            help="number of columns in the map")
    parser.add_argument("nobst", metavar="B", type=int, 
            help="how many obstacles to place in the map")
    parser.add_argument("nasset", metavar="A", type=int, 
            help="how many assets to place in the map")
    parser.add_argument("ntarg", metavar="N", type=int, 
            help="how many targets to place in the map")
    parser.add_argument("max_targ", type=int, default=1000, nargs='?',
            help="the maximum target value (default 1000)")
    parser.add_argument("-o", "--output-file", nargs='?', dest='out',
            type=argparse.FileType('w'), default=sys.stdout,
            help="output file destination (defaults to standard out)")
    args = parser.parse_args()

    # make sure everything is nonzero
    assert all(x>0 for x in (args.rows, args.cols, args.nasset, args.ntarg, args.max_targ))
    # make sure everything fits
    assert args.nobst + args.nasset + args.ntarg <= args.rows * args.cols

    # get a list of (row,column) pairs in random order
    spaces = [(r,c) for r in range(args.rows) for c in range(args.cols)]
    random.shuffle(spaces)
    space_iter = iter(spaces)

    # choose obstacle and asset locations
    obstacles = sorted(next(space_iter) for _ in range(args.nobst))
    assets = sorted(next(space_iter) for _ in range(args.nasset))

    # choose target locations and values
    targets = []
    for _ in range(args.ntarg):
        r, c = next(space_iter)
        val = random.randrange(1, args.max_targ + 1)
        targets.append((r,c,val))
    targets.sort()

    # print everything out
    print(args.rows, args.cols, file=args.out)
    print(file=args.out)
    
    print(args.nobst, file=args.out)
    for r, c in obstacles:
        print(r, c, file=args.out)
    print(file=args.out)

    print(args.nasset, file=args.out)
    for r, c in assets:
        print(r, c, file=args.out)
    print(file=args.out)

    print(args.ntarg, file=args.out)
    for r, c, v in targets:
        print(r, c, v, file=args.out)

if __name__ == '__main__':
    main()
