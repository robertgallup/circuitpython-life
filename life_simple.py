# John Conway's Game of Life
#
# Runs on CircuitPython
#
# Cellular automata displayed on a grid of cells. Some
# cells begin populated. Repeated generations are calculated
# using the following rules:
#
# 1. Live cells with 2 or 3 live neighbors survive
# 2. Dead cells with 3 live neighbors become live cells
# 3. Every other cell stays dead or dies
#
from random import randint
import time, math

# Pixel width and height of world (should be multiple of 
# 8 if using an LED grid)
DISPLAY_WIDTH       = const(16)
DISPLAY_HEIGHT      = const(8)

# Options for generation delay, maximum number of generations,
# and, the pause in the timeline between simulations
GENERATION_DELAY = .1
GENERATION_MAXIMUM = 50
TIMELINE_PAUSE = 1.0

# Returns a new world. Specify width and height.
def world(width, height):
    row_length = width+2
    first_cell = row_length+1
    world_length = (height+2) * (width+2)

    w = {
        'rows'          : height,
        'columns'       : width,
        'world_length'  : world_length,
        'cells'         : bytearray(world_length),
        'old_cells'     : bytearray(world_length),
        'offsets'       : [-first_cell, -first_cell+1, -first_cell+2, \
                          -1, +1, width+1, width+2, width+3]
        }
    return w

# Seeds the world randomly
def seed_world(w):

    rows = w["rows"]
    columns = w["columns"]

    cell = 1
    for r in range(rows):
        cell += (columns+2)
        for c in range(columns):
            w['cells'][cell+c] = randint(0,1)

# Calculate the world's next generation
def next_generation(w):
#
    rows = w["rows"]
    columns = w["columns"]

    # Copy previous generation
    w['old_cells'][:] = w['cells']

    row_start = 1
    for r in range(rows):
        row_start += (columns+2)
        for c in range(columns):
            # The index of this world cell
            world_cell = row_start + c
            # Take a census of this cells neighbors
            census = 0
            for o in w['offsets']:
                census += w['old_cells'][world_cell+o]
            # Apply Conway's rules:
            if (census<2 or census>3):
                w['cells'][world_cell] = 0
            elif (census==3):
                w['cells'][world_cell] = 1

    # Return True if population is stable (i.e. new == old), False otherwise        
    return (w['cells']==w['old_cells'])

def print_world(w):

    rows = w["rows"] + 2
    columns = w["columns"] + 2

    for r in range(rows):
        start_cell = columns * r
        for c in w['cells'][start_cell:start_cell+columns]:
            print(' .' if c == 0 else ' O', end="")
        print()
    print('\n')

# Run a single simulation until the world is stable
# or until 'max' generations.
def live_life(w, t, max):
    stable = False
    for g in range(GENERATION_MAXIMUM):
        print_world(w)
        stable = next_generation(w)
        if stable: break
        time.sleep(t)


# Create a world
w = world(DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Run continuous simulations seeding a new world each time
while True:
    seed_world(w)
    live_life(w, GENERATION_DELAY, GENERATION_MAXIMUM)
    time.sleep(TIMELINE_PAUSE)
