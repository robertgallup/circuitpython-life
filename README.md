# circuitpython-life

John Conway's Life algorithm is a cellular automata that evolves through simple rules. More information can be found [at this link](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

Here are some implementations using CircuitPython.

**life.py**  
output can be printed (serial output), or displayed on a max7219-controlled LED matrix or both.  

**life-simple.py**  
Supports only print output. In both versions, the grid size can be adjusted depending on available memory.

The algorithm is implemented on a 2D grid (x by y pixels). The grid is surrounded by a layer of zero cells to keep the community within the boundary. The grid is represented using a `bytearray()` with a byte for each cell in the grid in row-first order.

For example, the 8x8 grid:

```
x . . . . . . .
x x . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
. . . . . . . .
```
Would be represented as something close to:


```
+---------------------------------------------------------------+
| x |   |   |   |   |   |   |   | x | x |   |   |   |   |   |   | . . .
+---------------------------------------------------------------+
```

Technically, the grid is bordered with zeros so there are some extra cells in the list, but this is the main idea.

For each generation, A census is taken for each cell by counting neighbors using offsets from the current cell (for an 8x8 grid the offsets are -11, -10, -9, -1, +1, 9, 10, 11). Once the cell census it complete, the next generation is calculated according to Life's rules.

These scripts require using the following CircuitPython modules:

**adafruit_bus_device**  
**ledmatrix.py**  
**adafruit_max7219**  
**adafruit_framebuf.mpy**  

## Hardware Connections

The world grid can be displayed on one or more common 8x8 LED grids controlled by max7219 LED drivers. The connections are as follows

```
max7219 grid | VCC  ->  +5V | Microcontroller
             | GND  ->  GND |
             | DIN  ->  TX  | <MOSI>
             | CS   ->  A1  |
             | CLK  ->  RX  | <SCK>
```

The scripts have been tested on Trinket M0, and Circuit Playground Express, but likely run on other CircuitPython boards (perhaps with some pin changes)
