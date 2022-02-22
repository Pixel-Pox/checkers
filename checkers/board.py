import pygame
import numpy as np
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
        diagonals = []
        positions = [[[j, i] for i in range(ROWS)] for j in range(COLS)]
        possible_skip = False
        row = piece.row
        col = piece.col

        #Create all possible directions of movement for a piece, if king piece can move through whole board, if not only one move is permitted
        if piece.king:
            #first diagonal with offset of -(row - col)
            diag1 = np.diagonal(positions, -(row - col)).T
            #second diagonal with offset accounted for the flip
            diag2 = np.flipud(positions).diagonal(-(ROWS - 1 - row - col)).T
            diagonals = np.concatenate([diag1, diag2]).tolist()
        else:
            diagonals = [
                [row + piece.direction, col - piece.direction],
                [row + piece.direction, col + piece.direction],
                [row - piece.direction, col - piece.direction],
                [row - piece.direction, col + piece.direction]
            ]
        
        #first check if there is possible skip over other pieces as it's required to skip in the rules if possible, and always have to take a path with MOST skips.
        for coordinates in diagonals: 
            if not self.is_outside_board(coordinates):
                if coordinates != [row, col] and self.board[coordinates[0]][coordinates[1]] == 0:
                    moves.append(coordinates)
                    print(moves)
        return moves

    

    def is_outside_board(self, coordinates):
        row, col = coordinates
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return True
        return False 
        
