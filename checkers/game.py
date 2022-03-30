from numpy import array
import pygame
from ast import literal_eval
from checkers.board import Board
from checkers.constants import WHITE, BLACK, BLUE, SQUARE_SIZE, ROWS
from time import sleep
from typing import Tuple

class Game:
    def __init__(self, window) -> None:
        #function for init to easly reset the game state to initial
        self._init()
        self.window = window

    # game update redraws the next frame of the game
    def update(self) -> None:
        self.board.draw(self.window)
        self.draw_valid_moves(self.valid_moves, self.selected)
        pygame.display.update()

    # additional init function for reseting the game
    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}
        self.winner = None

    # reset function
    def reset(self):
        self._init()

    # this function handles selection of a space on the board
    def select(self, row: int, col: int) -> bool:
        #if a piece has been skipped, mark it, else select a piece
        if self.board.skipped:
            piece = self.board.skipped
        else:
            piece = self.board.get_piece(row, col)
        #if piece selected, try to move it, else just reselect the current selection
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        #if selected is an instance of a Piece class and it's current player's piece, check all valid moves for that player
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves, _ = self.board.get_valid_moves(self.turn)
            return True

        return False

    # function that tries to move the piece on the board
    def _move(self, row: int, col: int) -> bool:
        #get selected spot on the board
        piece = self.board.get_piece(row, col)
        # retrieve the possible moves for current piece
        possible_moves = self.valid_moves.get(self.selected)
        #if selected is an empty space, and is a valid move, then make that move
        if possible_moves:
            if self.selected and piece == 0 and str([row, col]) in possible_moves.keys():
                self.board.move(self.selected, row, col)

                # if skipped, remove skipped piece
                if possible_moves[str([row, col])]:
                    skipped_piece = literal_eval(self.valid_moves[self.selected][str([row, col])])
                    remove_piece = self.board.get_piece(
                        skipped_piece[0], skipped_piece[1])
                    self.board.remove_piece(remove_piece)

                    # if after skipping there is another skip available, keep current players turn and allow him to move only the selected piece.
                    piece = self.board.get_piece(row, col)
                    self.valid_moves, skipped = self.board.get_valid_moves(self.turn)
                    if skipped and piece in self.valid_moves.keys():
                        self.board.skipped = piece
                        self.select(row, col)
                    else:
                        # if a piece gets to opposite end, make it a king and change turn
                        if row == 0 or row == ROWS-1:
                            self.board.make_king(self.selected, row)
                            self.change_turn()
                            return True

                # if a piece gets to opposite end, make it a king and change turn
                else:
                    if row == 0 or row == ROWS-1:
                        self.board.make_king(self.selected, row)
                        self.change_turn()
                        return True

                # change turn if no skip avilable
                if not self.board.skipped:
                    self.change_turn()

                self.board.skipped = None
        return True

    # Draws valid moves as blue dots on the board
    def draw_valid_moves(self, moves: dict, current_piece: object) -> None:
        if current_piece in moves:
            for key, value in moves[current_piece].items():
                key_list = literal_eval(key)
                row, col = key_list[0], key_list[1]
                pygame.draw.circle(self.window, BLUE, (col * SQUARE_SIZE +
                                SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    # switches players turns
    def change_turn(self):
        # print evaluation of the current board state
        print(f'Current evaluation: {self.board.evaluate():.2f}')

        #check if after last move, the game is won or a tie, else reset turn dependent variables   
        if self.board.is_won(self.turn):
            self.update()
            self.winner = self.turn
            print(f"AND THE WINNER IS {self.winner}")
            print(f"Do you want to play another round? y/n\n")
            if input() == 'y':
                self.reset()
            elif input() == 'n':
                exit()

        elif self.board.is_tie():
            self.update()
            self.winner = None
            print(f"GAME HAS ENDED IN A DRAW DUE TO TOO MANY NON SKIP TYPE MOVES")
            print(f"Do you want to play another round? y/n\n")
            if input() == 'y':
                self.reset()
            elif input() == 'n':
                exit()
        else:
            self.valid_moves = {}
            self.board.skipped = False
            self.selected = None
            if self.turn == WHITE:
                self.turn = BLACK
            else:
                self.turn = WHITE
        # if using caching it's good to have this sleep call, otherwise the game is unwatchable - too fast
        #sleep(0.3)

    # returns the current game's board object
    def get_board(self) -> object:
        return self.board

    # if ai is playing, then this switches the current board with the board where the AI made a move
    def ai_move(self, board):
        self.board = board
        self.change_turn()