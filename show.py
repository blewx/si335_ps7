#!/usr/bin/python3

# SI 335 Algorithms, Spring 2025
# Problem Set 7 Helper code
#
# This program will display the given map and moves file,
# either one step at a time or played as a "movie".

import argparse
import sys
import curses
import time
import collections
from enum import Enum

class Obj(Enum):
    BORDER = 1
    OBSTACLE = 1
    ASSET = 2
    TARGET = 3
    MESSAGE = 4
    DEAD_ASSET = 5

    def pair(self):
        return curses.color_pair(self.value)

def runmoves(stdscr, world, movesIter, speed, autostop):
    def showMessage(text):
        stdscr.move(msgline, 0)
        stdscr.clrtoeol()
        stdscr.addstr(text, Obj.MESSAGE.pair()|curses.A_BOLD)

    def showScore(curscore):
        stdscr.move(*scorePos)
        stdscr.clrtoeol()
        stdscr.addstr(str(curscore), Obj.MESSAGE.pair())

    curses.curs_set(0)
    curses.use_default_colors()
    stdscr.nodelay(1)

    curses.init_pair(Obj.BORDER.value,     -1                 , -1                  )
    curses.init_pair(Obj.OBSTACLE.value,   -1                 , -1                  )
    curses.init_pair(Obj.ASSET.value,      curses.COLOR_GREEN , -1                  )
    curses.init_pair(Obj.DEAD_ASSET.value, curses.COLOR_RED   , -1                  )
    curses.init_pair(Obj.TARGET.value,     -1                 , -1                  )
    curses.init_pair(Obj.MESSAGE.value,    -1                 , -1                  )

    mazedims = world.rows+2, world.cols+2
    world.display(stdscr)

    scoreline = mazedims[0] + 1
    stdscr.move(scoreline, 0)
    stdscr.addstr("Score: ", Obj.MESSAGE.pair())
    scorePos = stdscr.getyx()

    showScore(world.score)

    infoline = mazedims[0] + 4
    stdscr.move(infoline,0)
    stdscr.addstr("S to step once, P to play/pause, UP/DOWN keys change speed, Q to quit\n")

    msgline = mazedims[0] + 2

    stdscr.refresh()

    messages = collections.deque()
    paused = True
    step = False

    if speed < 0:
        paused = True
        speed *= -1

    while True:
        time.sleep(1.0/speed)

        c = stdscr.getch()
        badch = False
        if c == curses.KEY_UP:
            speed += 1
            paused = False
        elif c == curses.KEY_DOWN:
            if speed <= 2:
                speed /= 2
            else:
                speed -= 1
            continue
        elif c == ord('s') or c == ord('S'):
            paused = True
            step = True
        elif c == ord('p') or c == ord('P'):
            paused = not paused
        elif c == ord('q') or c == ord('Q'):
            break
        elif c >= 0:
            badch = True

        if badch:
            showMessage("Unrecognized command")
            stdscr.refresh()
            continue

        if world.active() and (step or (not paused and speed > 0)):
            step = False
            try:
                nextMove = next(movesIter)
            except StopIteration:
                nextMove = None
                active = False
        else:
            nextMove = None

        if nextMove:
            msgs, status = world.move(nextMove)
            messages.extend(msgs)

            showScore(world.score)
            if status == 0:
                # neutral
                curses.init_pair(Obj.MESSAGE.value, -1, -1)
            elif status == 1:
                # bad
                curses.init_pair(Obj.MESSAGE.value, curses.COLOR_RED, -1)
            elif status == 2:
                # good
                curses.init_pair(Obj.MESSAGE.value, curses.COLOR_GREEN, -1)

            if not world.active():
                messages.append("All targets acquired or assets destroyed.")
        if messages:
            showMessage(messages.popleft())

        world.display(stdscr)
        stdscr.refresh()

        if not world.active() and not messages and autostop:
            time.sleep(5)
            break

class World:
    def __init__(self, mapin):
        self.rows, self.cols = map(int, next(mapin).split())
        next(mapin) # blank line

        # obstacles is a set of locations
        self.obstacles = set()
        nobst = int(next(mapin))
        for _ in range(nobst):
            r, c = map(int, next(mapin).split())
            self.obstacles.add((r,c))
        next(mapin) # blank line

        self.nasset = int(next(mapin))
        # assets is a list of locations
        self.assets = []
        for _ in range(self.nasset):
            r, c = map(int, next(mapin).split())
            self.assets.append([r,c])
        next(mapin) # blank line

        ntarg = int(next(mapin))
        # targets is a map of label to location/value tuple
        self.targets = {}
        # targloc is a map of location to target label
        self.targloc = {}
        for label in map(chr, range(ord('A'), ord('A') + ntarg)):
            r, c, v = map(int, next(mapin).split())
            self.targets[label] = (r,c,v)
            self.targloc[r,c] = label

        # how many moves have occurred
        self.elapsed = 0

        # current accumulated points
        self.score = 0

        # which assets are dead
        self.dead = set()

        # which spaces have been visited already
        self.trail = set()

    def astr(self, i):
        """Gets a 1-character string from asset index."""
        res = str(i+1)
        if len(res) != 1:
            res = 'x'
        return res

    def display(self, win, offset=(0,0)):
        """Displays the world map at specified offset in specified window."""

        # toshow is a map of location -> (character, style)
        toshow = {}
        for r,c in self.trail:
            toshow[r,c] = (ord('.'), Obj.BORDER.pair())
        for r,c in self.obstacles:
            toshow[r,c] = (ord('*'), Obj.OBSTACLE.pair())
        for label, (r,c,_) in self.targets.items():
            toshow[r,c] = (ord(label), Obj.TARGET.pair())
        for i,[r,c] in enumerate(self.assets):
            otype = Obj.DEAD_ASSET if i in self.dead else Obj.ASSET
            toshow[r,c] = (ord(self.astr(i)), otype.pair()|curses.A_BOLD)

        # top border
        win.addch(offset[0], offset[1], curses.ACS_ULCORNER, Obj.BORDER.pair())
        for c in range(self.cols):
            win.addch(offset[0], offset[1]+1+c, curses.ACS_HLINE, Obj.BORDER.pair())
        win.addch(offset[0], offset[1]+1+self.cols, curses.ACS_URCORNER, Obj.BORDER.pair())

        # the map
        for r in range(self.rows):
            # left border
            win.addch(offset[0]+1+r, offset[1], curses.ACS_VLINE, Obj.BORDER.pair())

            for c in range(self.cols):
                if (r,c) in toshow:
                    char, style = toshow[r,c]
                    win.addch(offset[0]+1+r, offset[1]+1+c, char, style)
                else:
                    win.addch(offset[0]+1+r, offset[1]+1+c, ord(' '), Obj.BORDER.pair())

            # right border
            win.addch(offset[0]+1+r, offset[1]+1+self.cols, curses.ACS_VLINE, Obj.BORDER.pair())

        # bottom border
        win.addch(offset[0]+1+self.rows, offset[1], curses.ACS_LLCORNER, Obj.BORDER.pair())
        for c in range(self.cols):
            win.addch(offset[0]+1+self.rows, offset[1]+1+c, curses.ACS_HLINE, Obj.BORDER.pair())
        win.addch(offset[0]+1+self.rows, offset[1]+1+self.cols, curses.ACS_LRCORNER, Obj.BORDER.pair())

    def move(self, moves):
        """Updates the assets according to the given list of moves.
        Returns a messages/status pair.
        Status is 0 if nothing special, 1 if something bad happened,
        2 if something good happened."""
        assert len(moves) == self.nasset

        msgs = []
        status = 0

        # one more step has been taken
        self.elapsed += 1

        # remove any target values <= 0
        zero_targets = []
        for label, (r,c,v) in self.targets.items():
            if v <= self.elapsed:
                zero_targets.append(label)
        for label in zero_targets:
            self.remove_target(label)

        for i, (dr, dc) in enumerate(moves):
            if i in self.dead:
                # dead assets don't move
                continue

            self.trail.add(tuple(self.assets[i]))
            self.assets[i][0] += dr
            self.assets[i][1] += dc
            r,c = self.assets[i]
            if r < 0 or r >= self.rows or c < 0 or c > self.cols:
                # ran out of bounds
                self.assets[i][0] -= dr
                self.assets[i][1] -= dc
                msgs.append("Asset {} ran out of bounds".format(self.astr(i)))
                self.dead.add(i)
                status = 1
            elif (r,c) in self.obstacles:
                # ran into an obstacle
                msgs.append("Asset {} ran into an obstacle".format(self.astr(i)))
                self.dead.add(i)
                status = 1
            elif (r,c) in self.targloc:
                # we got 'em!
                label = self.targloc[r,c]
                value = self.targets[label][2] - self.elapsed
                assert value > 0
                msgs.append("Asset {} got target {} for {} points".format(self.astr(i),label,value))
                self.remove_target(label)
                self.score += value
                status = 2

        return msgs,status

    def active(self):
        """Returns True only when there are more targets, and some assets are not dead."""
        return len(self.targets) > 0 and len(self.dead) < len(self.assets)

    def remove_target(self, label):
        r,c,v = self.targets[label]
        del self.targets[label]
        del self.targloc[r,c]

def read_moves(movesin, nasset):
    """Returns an iteration of moves. Each move is a tuple of row,col changes."""
    for line in movesin:
        directions = line.strip()
        assert len(directions) == nasset
        move = []
        for d in directions.upper():
            if d == 'U': move.append((-1,0))
            elif d == 'D': move.append((1,0))
            elif d == 'L': move.append((0,-1))
            elif d == 'R': move.append((0,1))
            else:
                raise RuntimeError("invalid move character: "+d)
        yield move

def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description="Show a map and associated moves")
    parser.add_argument("mapfile", type=argparse.FileType('r'),
            help="filename of the map")
    parser.add_argument("movesfile", type=argparse.FileType('r'),
            help="filename of the moves")
    parser.add_argument('speed', type=float, default=2.0, nargs='?',
            help="speed to display the moves, in frames per second. Default is 2")
    parser.add_argument('-a', '--autostop', action='store_true')
    args = parser.parse_args()

    # read in the map
    print(type(args.mapfile))
    print(args.mapfile)
    world = World(args.mapfile)

    # read in moves
    if args.movesfile:
        moves = read_moves(args.movesfile, world.nasset)
    else:
        moves = iter([])

    try:
        curses.wrapper(runmoves, world, moves, args.speed, args.autostop)
    except curses.error:
        print("There was an error displaying the map with curses.")
        print("Check that your terminal window is large enough for the map.")
        exit(3)

if __name__ == '__main__':
    main()
