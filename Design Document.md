This is the Design document for the Turing Machine version of Conway's Game of Life

# Machine goal:
Input: one board state of Conway's game of life
Output: the next board state

# Input Format

- Board must be rectangular
- Input 2d board in a flatted 1d structure, row by row
- Starts with a blank, followed by `S`
- Ends with an `X`
- Between each row put a `#`
- Dead cells are `-`
- Live cells are `+`

Example board: 6x6
```
S
--++--#
++--++#
--++--#
++--++#
--++--#
++--++X
```

# General Design Overview

## Logic Flow
Program consists of 4 main sections that loop across every row:
- `INIT`
- `PROCESS`
- `STORE`
- `RESET`
Start state will begin at a special section:
- `START`
End state accepts once `STORE` writes `X` and completes a special section:
- `END`

### Color Labels:
- `START`: Red 
- `INIT`: Lime
- `PROCESS`: Blue
- `STORE`: Slate
- `RESET`: Purple 
- `END`: Pink

## Alphabets
- Input alphabet
	- `SX#-+`
	- Their uses are described in [[#Input Format]]
- Tape alphabet
	- `SX#-+@01234ABCDEe`
	- `@` - marks out the three row chunk being calculated
	- `01234` - counter for how many surrounding alive cells are around a dead one
	- `ABCDE` - counter for how many surrounding alive cells are around an alive one
	- `e` - pointer to end of output section
	- ` ` - blank, required

# Section Design

The general idea is to make sure we know exactly where each section leaves the tape head so we know exactly where the next section begins. In general, we leave the tape head at the start of the row that is currently being analyzed.

**Notation**
- `<, >`, move one head one space left or right
- `<- a, -> a`, move head to the next symbol `a` to the left or right
- `a/b`, overwrite `a` with `b`
- ` /b`, write `b` on a blank
- `(a OR b)`, goes until either symbol is reached
- `see a`, check for required symbol, if not found, reject
- `if see a`, conditional, indicates branching
- `-SECTION-`, go to start state of indicated section

## `START`
This section sets up output location and does a basic formatting check.
1. `-> see S -> see # -> see X > /S > /e`
2. `<- S <- S`
>writes `Se` at the end of the input and checks to make sure `S` and `X` to indicate start and end exists, and one `#` to make sure it isn't just a line

```
S
--++--#
++--++#
--++--#
++--++#
--++--#
++--++X
S
e
```

## `INIT`
This section sets up the boundaries of the three row chunks by placing `@`s.

From `-START-`:
1. `see S -> # ->`
	1. `if see #/@`
	2. `if see X/X`
2. `<-- S > -PROCESS-`
> only places the ending `@`

```
S
--++--#
++--++@
--++--#
++--++#
--++--#
++--++X
S
e
```

From `-RESET-`:
1. `< see # <- (# OR S)/@ -> # ->`
	1. `if see # ->`
		1. `if see #/@`
		2. `if see X/X`
			1. Both: `<- # <- # > -PROCESS-`
	2. `if see X/X <- # > -PROCESS-`
>This places both `@`s at the start and end, while keep `X` as is. In the next section, `X` will sometimes also serve the same function as an `@`

```
@
--++--#
++--++#
--++--@
++--++#
--++--#
++--++X
S
e
```
or 
```
@
--++--@
++--++@
--++--@
++--++#
--++--#
++--++X
S
e
...
```
or 
```
@
--++--@
++--++@
--++--@
++--++@
--++--#
++--++X
S
e
...
```
## `PROCESS`
This section processes a single row, counting the neighbors for each cell. This section is more complicated so it is split into its own looping sub-sections, and also has a function:
- `(INC)`
	- `if see A/B`
	- `if see B/C`
	- `if see C/D`
	- `if see D/E`
	- `if see E`
	- `if see 0/1`
	- `if see 1/2`
	- `if see 2/3`
	- `if see 3/4`
	- `if see 4`

From `-INIT-`:
### `SET-VALUE`
This is the start of the sub-loop. Each sub-loop counts the neighbors for a single cell. 
- `if see -/0`
- `if see +/A`
	- both:  `-TOP-ROW-`
> Sets respective counter to 0, and moves on

Example, Row 2 Column 2:
```
@
--++--#
BA--++#
--++--@
++--++#
--++--#
++--++X
S
-++++-#
e
```
### `TOP-ROW`
Counts neighbors in the top row
1. `<`
	1. `if see # <- @` do step 4 - edge, skip top left
2. `<-`
	1. `if see S -> (- OR + OR #) < -BOTTOM-ROW-` - conditional skips to next subsection
	2. `if see # <- (0 OR A)`
3. `>`
	1. `if see -/0`
	2. `if see +/A -> # -> (- OR + OR #) < (INC) <- # <- A`
4. `>`
	1. `if see -/0`
	2. `if see +/A -> # -> (- OR + OR #) < (INC) <- # <- A`
5. `>`
	1. `if see #` do step 8 - ends early since row is complete
	2. `if see -/0`
	3. `if see +/A -> # -> (- OR + OR #) < (INC) <- # <- A`
6. 
	1. `if see 0/-`
	2. `if see A/+`
7. `<`
	1. `if see 0/-`
	2. `if see A/+`
8. `-> # -> (- or + or # or X) <`
9. `-BOTTOM-ROW-`
> Note that steps 2, 3, and 4 are basically repeated. This is checking the top left, top middle, and top right respectively. Steps 5 and 6 then reset the top middle and top right for the next cell to use.
> Note in steps 1 and 4, they account for cells on the edge of the grid

Example, Row 2 Column 2:
```
@
0-++--#
BB--++#
--++--@
++--++#
--++--#
++--++X
S
-++++-#
e
```
### `BOTTOM-ROW`
Very similar to top row
1. `<`
	1. `if see (# OR S) ->`
		1. `if see X <- (# OR S) -> (- OR + OR # OR X) < -MIDDLE-ROW-` - conditional skips to next sub-section
		2. `if see # -> (- OR +)` do step 4 - edge, skip bottom left
2. `->`
	1. `if see X <- (# OR S) -> (- OR + OR # OR X) < -MIDDLE-ROW-` - conditional skips to next sub-section
	2. `if see # -> (- OR +)`
3. 
	1. `if see -/0 >`
	2. `if see +/A <- # <- (# OR S) -> (- OR + OR # OR X) < (INC) -> # > (- OR +)`
4. 
	1. `if see -/0 >`
	2. `if see +/A <- # <- (# OR S) -> (- OR + OR # OR X) < (INC) -> # >`
		1. `if see (- OR +)`
		2. `if see (@ OR X)` do step 8 - end early since row is complete
5. 
	1. `if see -/0 >`
	2. `if see +/A <- # <- (# OR S) -> (- OR + OR # OR X) < (INC) -> # > (- OR + OR @ OR X)`
6. `<` 
	1. `if see 0/-`
	2. `if see A/+`
7. `<`
	1. `if see 0/-`
	2. `if see A/+`
8. `<- # <- (# OR S) -> (- or + or #) <`
9. `-MIDDLE-ROW-`
> This is quite similar to checking the top row, except a little more complicated back and forth. This also means edge detection is slightly different, but all in all remains familiar

Example, Row 2 Column 2:
```
@
0-++--#
BC--++#
0-++--@
++--++#
--++--#
++--++X
S
-++++-#
e
```
### `MIDDLE-ROW`
Check the middle left and middle right of the cell
1. `<`
	1. `if see (0, 1, 2, 3, 4, OR S OR #) >`
	2. `if see (A, B, C, D, OR E) > (INC)`
2. `>`
	1. `if see (- OR # OR X) <`
	2. `if see + < (INC)`
3. `-STEP-FORWARD-`
> Relatively simple compared to checking the top and bottom rows, just note the left will consist of the counters and right will consist of the input symbols, and don't forget the literal edge cases

Example, Row 2 Column 2:
```
@
0-++--#
BD--++#
0-++--@
++--++#
--++--#
++--++X
S
-++++-#
e
```
### `STEP-FORWARD`
Iterate to the next cell in the row. Also serves as the exit point for when the row has been complete processed.
1. `>`
	1. `if see (- or +) -SET-VALUE-`
	2. `if see (# or X) <- (# or S) > -STORE-`
> Pretty straight forward: if it sees an unprocessed cell, jump back to the start of the loop. If it sees the end of the row, move the head back to the beginning of the row and continue with the next section.

Example, Row 2, after a whole row is complete:
```
@
00AA00#
BD44DB#
00AA00@
++--++#
--++--#
++--++X
S
-++++-#
e
```
## `STORE`
At this point, a row was just completed, and now we need to store the processed row in the output section. This once again loops, but the loop much simpler. This section mostly contains conditionals, as this is where the actual rules for the cellular automata are performed.

From `-PROCESS-`:
1. ``
	1. `if see (0, 1, 2, OR 4)/-` 
	2. `if see (A, B, OR E)/+` 
		1. both: `-> e/-` - dead cell rules
	3. `if see 3/-` 
	4. `if see (C OR D)/+`
		1. both: `-> e/+` - alive cell rules
2. `> /e <- X <- @ <-`
	1. `if see @ -> # -> (# OR X)` - case where `X` is used as `@` or its last row
	2. `if see #`
3. `<- (- or +) >`
	1. `if see (0,1,2,3,4,A,B,C,D, OR E)` do step 1 - loop
	2. `if see # -> e/# > /e <- X <- @ <-`
		1. `if see @ -> # -> #`  
		2. `if see #`
			1. both: `> -RESET-`
	3. `if see X -> e/X -END-`
> This is pretty hard to follow but here is the rundown:
> Step 1 enacts the rules of Conway's Game of Life
> Step 2 helps the head find it's way back to the original working row
> Step 3 moves head forward one and enacts the loop. If it finds the end of the row, it writes that too and depending on if it is the end of a normal row or the last row, it moves on to the next step.

Example, Row 2, after store section is complete:
```
@
00AA00#
++--++#
00AA00@
++--++#
--++--#
++--++X
S
-++++-#
-+--+-#
e
```

## `RESET`
Now located at the next row, Change the `0`s and `A`s used as placeholder back to `-` and `+`, get rid of the `@`, and move back to the start of the row to start at `INIT` again.

From `-STORE-`:
1. ``
	1. `if see 0/-`
	2. `if see A/+`
		1. both: `>` do step 1 - loop
	3. `if see @/#`
	4. `if see X`
		1. both: `<- # > -INIT-`
> This one is a relatively simple step through of the row. not much explaining need here. Once the end of the row is reached, go back and do `-INIT-`

Example, Row 2 to 3, after reset section is complete:
```
@
00AA00#
++--++#
--++--# 
++--++#
--++--#
++--++X
S
-++++-#
-+--+-#
e
```

## `END`
The machine reaches this section once store has written the `X` to the output area. Now we remove the input and are left with a clean output.

From `-STORE-`:
1. `<- S < see X`
2. `/blank <`
	1. `if see not blank` do step 2 - loop
	2. `if see blank -> S` ACCEPT
> Wipe the original input and move the head back to the output's start, ready for the machine to be run again if desired
# Test Cases

These test cases can be used to test each step of the process on a small example. It will be based off of the following input:
```
S
-+-#
-+-#
-+-X
```
## Full Test:
Input: 
```
S
-+-#
-+-#
-+-X
```
Output: 
```
S
---#
+++#
---X
```

## `START`
Input: 
```
S
-+-#
-+-#
-+-X
```
Output: 
```
S
-+-#
-+-#
-+-X
S
e
```

## `INIT`
### Top row
Input:
```
S
-+-#
-+-#
-+-X
S
e
```
Output:
```
S
-+-#
-+-@
-+-X
S
e
```

### Middle row
Input:
```
S
-+-#
-+-#
-+-X
S
---#
e
```
Output:
```
@
-+-#
-+-#
-+-X
S
---#
e
```

### Bottom row
Input:
```
@
0A0#
-+-#
-+-X
S
---#
+++#
e
```
Output:
```
@
0A0@
-+-#
-+-X
S
---#
+++#
e
```

## Process

### Top row
Input:
```
S
-+-#
-+-@
-+-X
S
e
```
Output:
```
S
2B2#
0A0@
-+-X
S
e
```

### Middle row
Input:
```
@
-+-#
-+-#
-+-X
S
---#
e
```
Output:
```
@
0A0#
3C3#
0A0X
S
---#
e
```

### Bottom row
Input:
```
@
0A0@
-+-#
-+-X
S
---#
+++#
e
```
Output:
```
@
0A0@
0A0#
2B2X
S
---#
+++#
e
```

## `TOP_ROW`
For the sub-sections of `PROCESS`, these are all for the middle row.
### Left Edge
Input:
```
@
-+-#
0+-#
-+-X
S
---#
e
```
Output:
```
@
-+-#
1+-#
-+-X
S
---#
e
```

### Middle
Input:
```
@
-+-#
3A-#
-+-X
S
---#
e
```
Output:
```
@
0+-#
3B-#
-+-X
S
---#
e
```

### Right Edge
Input:
```
@
0+-#
3C0#
0+-X
S
---#
e
```
Output:
```
@
0A0#
3C1#
0+-X
S
---#
e
```

## `BOTTOM_ROW`
For the sub-sections of `PROCESS`, these are all for the middle row.
### Left Edge
Input:
```
@
-+-#
1+-#
-+-X
S
---#
e
```
Output:
```
@
-+-#
2+-#
-+-X
S
---#
e
```

### Middle
Input:
```
@
0+-#
3B-#
-+-X
S
---#
e
```
Output:
```
@
0+-#
3C-#
0+-X
S
---#
e
```

### Right Edge
Input:
```
@
0A0#
3C1#
0+-X
S
---#
e
```
Output:
```
@
0A0#
3C2#
0A0X
S
---#
e
```

## `MIDDLE_ROW`
For the sub-sections of `PROCESS`, these are all for the middle row.
### Left Edge
Input:
```
@
-+-#
2+-#
-+-X
S
---#
e
```
Output:
```
@
-+-#
3+-#
-+-X
S
---#
e
```

### Middle
Input:
```
@
0+-#
3C-#
0+-X
S
---#
e
```
Output:
```
@
0+-#
3C-#
0+-X
S
---#
e
```

### Right Edge
Input:
```
@
0A0#
3C2#
0A0X
S
---#
e
```
Output:
```
@
0A0#
3C3#
0A0X
S
---#
e
```

## `STORE`

### Top row
Input:
```
S
2B2#
0A0@
-+-X
S
e
```
Output:
```
S
-+-#
0A0@
-+-X
S
---#
e
```

### Middle row
Input:
```
@
0A0#
3C3#
0A0X
S
---#
e
```
Output:
```
@
0A0#
-+-#
0A0X
S
---#
+++#
e
```

### Bottom row
Input:
```
@
0A0@
0A0#
2B2X
S
---#
+++#
e
```
Output:
```
@
0A0@
0A0#
-+-X
S
---#
+++#
---X
```

## `RESET`

### Top row
Input:
```
S
-+-#
0A0@
-+-X
S
---#
e
```
Output:
```
S
-+-#
-+-#
-+-X
S
---#
e
```

### Middle row
Input:
```
@
0A0#
-+-#
0A0X
S
---#
+++#
e
```
Output:
```
@
0A0#
-+-#
-+-X
S
---#
+++#
e
```

## `END`
Input:
```
@
0A0@
0A0#
-+-X
S
---#
+++#
---X
```
Output:
```
S
---#
+++#
---X
```
