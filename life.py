# John Conway's Game of Life
#
# Runs on CircuitPython
#
# Cellular automata displayed on a grid of cells
# Some cells begin populated
# Repeated generations are calculated using the following rules:
#
# 1. Live cells with 2 or 3 live neighbors survive
# 2. Dead cells with 3 live neighbors become live cells
# 3. Every other cell stays dead or dies
#
# Supports print and/or LED Grid output
#
# The implementation here begins with a World dictionary with:
#
# world['rows']    = Number of rows in the world grid
# world['columns'] = Number of columns in the world grid
# world['world_length'] = length of bytearray representing world
# world['cells']   = A bytearray() representing all of the world's cells
# world['old_cells']   = Bytearray() for previous generation
# world['offsets']      = Offsets to neighbors from a cell

# In data, the world is represented as a linear array of bytes.
# Logically, the world is an nxm grid surrounded by a layer of zeros
# The zeros are a void barrier that limits the civilization
# 

from random import randint
from board import TX, RX, A1
import busio, digitalio, time, math

# MatrixN controls "n" matrices
from ledmatrix import MatrixN

# Pixel width and height of world (should be multiple of 
# 8 if using an LED grid)
DISPLAY_WIDTH       = const(16)
DISPLAY_HEIGHT      = const(8)

# Display brightness (0-15)
DISPLAY_BRIGHTNESS  = 0

# Output can be directed to the LED grid, print (serial out),
# or both: show_world(w, 'print', 'matrix')
OUTPUT_MODE = 'matrix'
# OUTPUT_MODE = 'print'

# How to seed the world (other options are available, see below)
LIFE_SEED = 'random'
# LIFE_SEED = 'carousel'

# Options for generation delay, maximum number of generations,
# and, the pause in the timeline between simulations
GENERATION_DELAY = .1
GENERATION_MAXIMUM = 50
TIMELINE_PAUSE = 1.0

# LED Grid pins/ SPI setup
clk = RX
din = TX
cs = digitalio.DigitalInOut(A1) 
spi = busio.SPI(clk, MOSI=din)

# Display is mapped to a number of 8x8 LED grids
display = MatrixN(spi, cs, DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Initialize the display
display.init_display()
display.brightness(DISPLAY_BRIGHTNESS)
display.fill(0)
display.show()

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

# Seeds the world from a source ('random', 'frog', 'clapper', 'blinker', ...)
def seed_world(w, *argv):

    rows = w["rows"]
    columns = w["columns"]

    # Clear the world
    for c in range(w['world_length']): w['cells'][c]=0

    # Seed the world depending on type (default 'random')
    # May combine more than one
    seed_type = argv if len(argv)>0 else ['carousel']

    if seed_type[0] == 'carousel':
        seed_type = [[ \
            'random',       \
            'frogger',      \
            'clapper',      \
            'nova',         \
            'blinkers',     \
            'bullseye',     \
            'glider'
            ][randint(0,6)]]

    # Add the seeds
    for type in seed_type:
    
        if (type=='random'):
            cell = 1
            for r in range(rows):
                cell += (columns+2)
                for c in range(columns):
                    w['cells'][cell+c] = randint(0,1)

        elif (type=='frogger'):
            pattern = bytes(

                b'....OOO.' +\
                 '..O....O' +\
                 '..O....O' +\
                 '..O....O' +\
                 '........' +\
                 '....OOO.' +\
                 '........' +\
                 '........'
                )

        elif (type=='clapper'):
            pattern = bytes(
                b'........' + \
                 '........' + \
                 '...O....' + \
                 '...OO...' + \
                 '...OO...' + \
                 '....O...' + \
                 '........' + \
                 '........'
                )

        elif (type=='blinkers'):
            pattern = bytes(
                b'........' +\
                 'OOO..OOO' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '.O....O.' +\
                 '.O....O.' +\
                 '.O....O.'  
                )

        elif (type=='nova'):
            pattern = bytes(
                b'........' +\
                 '........' +\
                 '........' +\
                 '....O...' +\
                 '...OOO..' +\
                 '..OO.OO.' +\
                 '........' +\
                 '........'
                )

        elif (type=='bullseye'):
            pattern = bytes(
                b'........' +\
                 'OOO.....' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '.....OO.' +\
                 '.....O.O' +\
                 '.....O..'
                )

        elif (type=='glider'):
            pattern = bytes(
                b'........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '.OO.....' +\
                 'O.O.....' +\
                 '..O.....'  \
                )
            
        elif (type=='void'):
            pattern = bytes(
                b'........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........'
                )

        elif (type=='untitled'):
            pattern = bytes(
                b'........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........' +\
                 '........'
                )

        # This catches the case of 'random' or unknown
        # since 'pattern' won't exist
        try:
            orientation = randint(0,3)
            cell = 1
            for r in range(8):
                cell += (columns+2)
                for c in range(8):
                    if   orientation == 0: w['cells'][cell+c] = pattern[(r*8) + c] == ord('O')
                    elif orientation == 1: w['cells'][cell+c] = pattern[(r*8) + (8-c-1)] == ord('O')
                    elif orientation == 2: w['cells'][cell+c] = pattern[((8-r-1)*8) + c] == ord('O')
                    elif orientation == 3: w['cells'][cell+c] = pattern[((8-r-1)*8) + (8-c-1)] == ord('O')
        except:
            pass

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
            # census = sum([w['old_cells'][world_cell+o] for o in w['offsets']])
            # Apply Conway's rules:
            # Cells with 2 neighbors don't change
            # Cells with 3 neighbors give birth
            # Cells with <2 or >3 neighbors die
            if census != 2: w['cells'][world_cell] = 1 if (census == 3) else 0

    # Return True if population is stable (i.e. new == old), False otherwise        
    return (w['cells']==w['old_cells'])

# Show the world by printing, on an LED grid, or both
def show_world(w, *argv):

    displays = argv if len(argv) > 0 else ['print']
    for type in displays:
        if type == 'print':
            print_world(w)
        elif type == 'matrix':
            matrix_world(w)

def print_world(w):
#
    rows = w["rows"] + 2
    columns = w["columns"] + 2
#
    for r in range(rows):
        start_cell = columns * r
        for c in w['cells'][start_cell:start_cell+columns]:
            print(' .' if c == 0 else ' O', end="")
        print()
    print('\n')

def matrix_world(w):
    rows = w["rows"]
    columns = w["columns"]
    display.fill(0)
    for r in range(rows):
        start_cell = columns+3 + r*(columns+2)
        for c in range(columns):
            if (w['cells'][start_cell+c] != 0):
                display.pixel(c,r,1)
    display.show()

# Run a single simulation until the world is stable
# or until 'max' generations.
#
#   'w'     is the world
#   't'     is the time delay between generations
#   'max'   is the maximum number of generations
#   *argv   can be empty, 'print' and/or 'led)grid'
#
# For example:
#
#   live_life(w, .5, 50)
#   live_life(w, .25, 70, 'print')
#   live_life(w, .25, 70, 'matrix')
#   live_life(w, .25, 70, 'print', 'matrix')
#
def live_life(w, t, max, *argv):
    stable = False
    for g in range(GENERATION_MAXIMUM):
        show_world(w, *argv)
        stable = next_generation(w)
        if stable: break
        time.sleep(t)

# Create a world
w = world(DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Run continuous simulations seeding a new world each time
# Default world is 'random', but can be any number of shapes
# including 'carousel', which randomly chooses a seed pattern
#
# 'random', 'carousel', frogger', 'clapper', 'blinkers',
# 'glider', 'bullseye'
# examples:
#   seed_world(x)
#   seed_world(x, 'frogger')
#   seed_world(x, 'blinkers', 'clapper')
#
while True:
    seed_world(w, LIFE_SEED)
    live_life(w, GENERATION_DELAY, GENERATION_MAXIMUM, OUTPUT_MODE)
    time.sleep(TIMELINE_PAUSE)
