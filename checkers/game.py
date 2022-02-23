from distutils.util import change_root
import pygame
from ast import literal_eval
from checkers.board import Board
from checkers.constants import WHITE, BLACK, BLUE, SQUARE_SIZE


class Game:
    def __init__(self, window) -> None:
        self._init()
        self.window = window

    def update(self):
        self.board.draw(self.window)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and str([row, col]) in self.valid_moves.keys():
            self.board.move(self.selected, row, col)

            # if skipped player gets another turn with that piece
            if self.valid_moves[str([row, col])]:
                skipped_piece = literal_eval(self.valid_moves[str([row, col])])
                remove_piece = self.board.get_piece(
                    skipped_piece[0], skipped_piece[1])
                self.board.remove_piece(remove_piece)
                piece = self.board.get_piece(row, col)
                self.valid_moves = self.board.get_valid_moves(piece)
                for value in self.valid_moves.values():
                    if value != False:
                        self.select(row, col)
                        break
                    else:
                        self.change_turn()
                
            else:
                self.change_turn()

        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for key, value in moves.items():
            key_list = literal_eval(key)
            row, col = key_list[0], key_list[1]
            pygame.draw.circle(self.window, BLUE, (col * SQUARE_SIZE +
                               SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        self.selected = None
        if self.turn == WHITE:
            self.turn = BLACK
        else:
            self.turn = WHITE
