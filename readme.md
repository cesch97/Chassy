Chassy
======
Chassy is a simple chess engine based on the minimax algorithm with alpha-beta pruning. The evaluation function is based on piece-square tables and piece values, and the search algorithm is enhanced with transposition tables. The interactive GUI is made with the PyQt library.

### Evaluation function
The evaluation function is based on piece-square tables and piece values. The piece-square tables are used to evaluate the position of the pieces on the board, and the piece values are used to evaluate the material balance. The piece values are just a table where for each piece there is its coresponding value. The piece-square tables instead are a set of tables one for each piece. Each table contains a value for each square on the board. The value is positive if the piece is in a good position and negative if the piece is in a bad position. The final evaluation of a position is calculated by summing the values of the piece-square tables and the piece values.

Eample of piece-square table for the pawn:
| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 10 | 10 | -20 | -20 | 10 | 10 | 5 |
| 5 | -5 | -10 | 0 | 0 | -10 | -5 | 5 |
| 0 | 0 | 0 | 20 | 20 | 0 | 0 | 0 |
| 5 | 5 | 10 | 25 | 25 | 10 | 5 | 5 |
| 10 | 10 | 20 | 30 | 30 | 20 | 10 | 10 |
| 50 | 50 | 50 | 50 | 50 | 50 | 50 | 50 |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

This table rewards the pawn for advancing and punishes the pawn for staying back

### Search algorithm
The search algorithm is based on the minimax algorithm with alpha-beta pruning. The minimax algorithm is a recursive algorithm that generates all the possible moves from the current position and evaluates them using the evaluation function. The alpha-beta pruning is a technique used to reduce the number of nodes that are evaluated by the minimax algorithm. The idea is to keep track of the best moves found so far and prune the branches of the search tree that are not promising.

### Transposition tables
The transposition tables are used to store the positions that have already been evaluated by the search algorithm. This way, if the search algorithm reaches a position that has already been evaluated, it can retrieve the evaluation from the transposition table instead of reevaluating the position. This can save a lot of time and improve the performance of the search algorithm. The transposition tables are implemented as a hash table where the key is the position of the board and the value is the evaluation of the position.

### GUI
The interactive GUI is made with the PyQt library. The GUI allows the user to play against the engine, set the depth of the search algorithm, and see the evaluation of the position over time.

### Usage
It is possible to play against the engine either by running the jupyter notebook in `engine/Playing.ipynb` or by launching the GUI with the command `python main.py`.