import pygame
import numpy as np
from checkers.piece import Piece
from .constants import BLACK, DARK_BROWN, LIGHT_BROWN, ROWS, SQUARE_SIZE, COLS, WHITE


class Board:
    def __init__(self):
        self.board = []
        self.skipped = False

        self.background = np.zeros((ROWS, COLS))
        self.background[1::2, ::2] = 1
        self.background[::2, 1::2] = 1

        self.black_left = self.white_left = (ROWS - 2)//2*COLS//2
        self.black_kings = self.white_kings = 0
        self.create_board()

    def draw_checkerboard(self, window):
        window.fill(BLACK)
        for row in range(ROWS):
            for col in range(COLS):
                if self.background[row][col] == 1:
                    pygame.draw.rect(
                        window, DARK_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(
                        window, LIGHT_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, new_row, new_col):
        # swap position of a piece with empty space, returns True if King has been made to end turn
        self.board[piece.row][piece.col], self.board[new_row][new_col] = self.board[new_row][new_col], self.board[piece.row][piece.col]
        piece.move(new_row, new_col)


    def make_king(self, piece, new_row):
        if piece != 0:
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
                if col % 2 == ((row + 1) % 2):
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

    def get_valid_moves(self, piece):
        moves = {}
        diagonals = []
        positions = [[[j, i] for i in range(ROWS)] for j in range(COLS)]
        row = piece.row
        col = piece.col

        # Create all possible directions of movement for a piece, if king piece can move through whole board, if not only one move is permitted
        if piece.king:
            # first diagonal with offset of -(row - col)
            diag1 = (np.diagonal(positions, -(row - col)).T).tolist()
            # second diagonal with offset accounted for the flip
            diag2 = (
                np.flipud(positions).diagonal(-(ROWS - 1 - row - col)).T).tolist()
            # find the index of position of current piece
            piece_idx_1 = diag1.index([row, col])
            piece_idx_2 = diag2.index([row, col])
            # split two diagonals into 4 lists representing 4 directions that go in order from the piece's pov.
            forward_left = list(reversed(diag1[:piece_idx_1]))
            back_left = list(reversed(diag2[:piece_idx_2]))
            try:
                forward_right = diag2[piece_idx_2+1:]
            except IndexError:
                forward_right = None
            try:
                back_right = diag1[piece_idx_1+1:]
            except IndexError:
                forward_right = None
            directions = [forward_left, back_left, forward_right, back_right]
            for direction in directions:
                if direction != None:
                    diagonals.append(direction)
        else:
            diagonals = [
                [[row + piece.direction, col - piece.direction]],
                [[row + piece.direction, col + piece.direction]],
                [[row - piece.direction, col - piece.direction]],
                [[row - piece.direction, col + piece.direction]]
                ]

        # first check if there is possible skip over other pieces as it's required to skip in the rules if possible, and always have to take a path with MOST skips.

        for diagonal in diagonals:
            skipped = False
            for coordinates in diagonal:                
                if not self.is_outside_board(coordinates):
                    row_dir, col_dir = self.get_direction(row, col, coordinates[0], coordinates[1])

                    if self.board[coordinates[0]][coordinates[1]] == 0 and not skipped:
                        if piece.king:
                            moves[str(coordinates)] = False
                        elif piece.direction == row_dir:
                            moves[str(coordinates)] = False

                    elif self.board[coordinates[0]][coordinates[1]] == 0 and skipped:
                        skipped_to_row, skipped_to_col = coordinates[0], coordinates[1]
                        if not self.is_outside_board([skipped_to_row, skipped_to_col]):
                            moves[str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col])  

                    elif not skipped and self.board[coordinates[0]][coordinates[1]].color != piece.color:
                            skipped_row, skipped_col = row_dir+row, col_dir+col 
                            if piece.king:
                                skipped = True                              
                            else:
                                skipped_to_row, skipped_to_col = row_dir*2+row, col_dir*2+col
                                if not self.is_outside_board([skipped_to_row, skipped_to_col]) and self.board[skipped_to_row][skipped_to_col] == 0:
                                    moves[str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col])
                                    
                    elif self.board[coordinates[0]][coordinates[1]].color == piece.color:
                            break                        
                        
        return moves

    def get_direction(self, row, col, new_row, new_col):
        row_dir = new_row - row
        col_dir = new_col - col
        return row_dir, col_dir

    def is_outside_board(self, coordinates):
        row, col = coordinates
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return True
        return False

    def remove_piece(self, piece):
        self.board[piece.row][piece.col] = 0
        if piece.color == WHITE:
            self.white_left -= 1
        else:
            self.black_left -= 1
