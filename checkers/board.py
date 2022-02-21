from email.policy import default
import pygame
import numpy as np
from collections import defaultdict
from checkers.piece import Piece
from .constants import BLACK, DARK_BROWN, LIGHT_BROWN, ROWS, SQUARE_SIZE, COLS, WHITE

class Board:
    def __init__(self):
        self.board = []

        self.background = np.zeros((ROWS, COLS))
        self.background[1::2,::2] = 1
        self.background[::2,1::2] = 1

        self.black_left = self.white_left = 20
        self.black_kings = self.white_kings = 0
        self.create_board()

    def draw_checkerboard(self, window):
        window.fill(BLACK)
        for row in range(ROWS):
            for col in range(COLS):
                if self.background[row][col] == 1:
                    pygame.draw.rect(window,DARK_BROWN,(row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(window,LIGHT_BROWN,(row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, new_row, new_col):
        #swap position of a piece with empty space
        self.board[piece.row][piece.col], self.board[new_row][new_col] = self.board[new_row][new_col], self.board[piece.row][piece.col]    
        piece.move(new_row, new_col)

        if new_row == 0 and piece.color == WHITE and piece.king == False:
            piece.make_king()
            self.white_kings += 1

        elif new_row == ROWS - 1 and piece.color == BLACK and piece.king == False:
            piece.make_king()
            self.black_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]


    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row +  1) % 2):
                    if row < ROWS//2 - 1:
                        self.board[row].append(Piece(row, col, BLACK))
                    elif row > ROWS//2:
                        self.board[row].append(Piece(row, col, WHITE))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, window):
        self.draw_checkerboard(window)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(window)

    def get_valid_moves(self, piece, move_no=0):
        moves = []
        if piece.king:
            pass
        else:
            forward_left = [piece.row + piece.direction, piece.col + piece.direction]
            forward_right = [piece.row + piece.direction, piece.col - piece.direction]
            back_left = [piece.row - piece.direction, piece.col + piece.direction]
            back_right = [piece.row - piece.direction, piece.col - piece.direction]

        if not self.is_outside_board(forward_left[0], forward_left[1]):
            if self.get_piece(forward_left[0], forward_left[1]) == 0:
                moves.append(forward_left)
        if not self.is_outside_board(forward_right[0], forward_right[1]):
            if self.get_piece(forward_right[0], forward_right[1]) == 0:
                moves.append(forward_right)
        if not self.is_outside_board(back_left[0], back_left[1]):
            if self.get_piece(back_left[0], back_left[1]) == 0:
                moves.append(back_left)
        if not self.is_outside_board(back_right[0], back_right[1]):
            if self.get_piece(back_right[0], back_right[1]) == 0:
                moves.append(back_right)

        
        return moves



    def is_outside_board(self, row, col):
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return True
        return False 
        
