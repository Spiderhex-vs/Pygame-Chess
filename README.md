# Chess Engine - CS50 Final Project

#### Video Demo: TODO
#### Description:

This is my CS50 final project: a chess game built in Python using Pygame and python-chess.

The project allows the player to play chess against a simple computer engine. The graphical interface is made with Pygame, while the chess rules, legal move generation, checkmate detection, stalemate detection, and board logic are handled by the python-chess library.

The game includes a playable chess board, piece movement, legal move highlighting, capture highlighting, last move highlighting, check highlighting, pawn promotion, a side panel with game status, and chess clocks for both players. The player controls White, while the engine controls Black. The engine runs in a separate thread so that the Pygame window does not freeze while the computer is thinking.

## Features

- Full graphical chess board
- Legal chess moves using python-chess
- Player vs computer mode
- Minimax chess engine with alpha-beta pruning
- Piece-square table evaluation
- Move ordering for captures
- Highlighted selected piece
- Highlighted legal moves
- Highlighted captures
- Highlighted last move
- Highlighted king in check
- Pawn promotion menu
- Game status display
- White and black chess clocks
- Threaded engine calculation to keep the UI responsive

## Files

### main.py

This file contains the main Pygame application. It creates the window, draws the board, loads piece images, handles mouse input, updates the timers, displays the sidebar, and manages the game loop.

It also starts the engine in a separate thread when it is Black's turn, so the interface remains responsive while the engine searches for a move.

### engine.py

This file contains the computer chess engine.

The engine evaluates positions using material values and piece-square tables. It uses the minimax algorithm with alpha-beta pruning to search possible future moves. It also sorts capture moves before quiet moves to improve pruning efficiency.

The evaluation returns positive scores for White advantages and negative scores for Black advantages.

## How the Engine Works

The engine uses a minimax search. White tries to maximize the evaluation score, while Black tries to minimize it.

Alpha-beta pruning is used to skip branches of the move tree that cannot affect the final decision. This makes the engine much faster than plain minimax.

The engine also evaluates moves using a simple capture ordering system. Captures are searched first, which helps alpha-beta pruning cut more branches.

The board evaluation includes:

- piece values
- pawn positioning
- knight positioning
- bishop positioning
- rook positioning
- queen positioning
- king positioning
- checkmate detection
- stalemate detection
- insufficient material detection

## Controls

- Click a piece to select it.
- Click a highlighted square to move.
- If a pawn reaches the last rank, choose a promotion piece from the promotion menu.
- Press Backspace to quit the game.

## Requirements

This project requires Python and the following libraries:

```bash
pip install pygame python-chess