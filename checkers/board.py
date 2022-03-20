import pygame
import numpy as np
from .piece import Piece
from .constants import BLACK, DARK_BROWN, LIGHT_BROWN, ROWS, SQUARE_SIZE, COLS, WHITE


class Board:
    def __init__(self):
        self.board = []
        self.skipped = False
        self.king_moves = 0

        # create a background checkerboard pattern of 0 and 1
        self.background = np.zeros((ROWS, COLS))
        self.background[1::2, ::2] = 1
        self.background[::2, 1::2] = 1

        # initial ammount of white/black pieces and the number of kings
        self.black_left = self.white_left = (ROWS - 2)//2*COLS//2
        self.black_kings = self.white_kings = 0
        self.create_board()

    def draw_checkerboard(self, window):
        # draw a colorful checkerboard as a background
        window.fill(BLACK)
        for row in range(ROWS):
            for col in range(COLS):
                if self.background[row][col] == 1:
                    pygame.draw.rect(
                        window, DARK_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(
                        window, LIGHT_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def evaluate(self):
        return self.white_left - self.black_left + (2*self.white_kings - 2*self.black_kings)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces


    def move(self, piece, new_row, new_col):
        # swap position of a piece with empty space, returns True if King has been made to end turn
        self.board[piece.row][piece.col], self.board[new_row][new_col] = self.board[new_row][new_col], self.board[piece.row][piece.col]
        
        # change the row and col values of a Piece object
        piece.move(new_row, new_col)

        # if a moved piece is a king piece and no skip has been done then increase the "tie" counter else zero it
        if piece.king and not self.skipped:
            self.king_moves += 1
        else:
            self.king_moves = 0 


    def make_king(self, piece, new_row):
        # if passed piece is an instance of Piece class
        if piece != 0:
            # if not already a king piece and on the opposite end of the board, change a piece to a king
            if new_row == 0 and piece.color == WHITE and piece.king == False:
                piece.make_king()
                self.white_kings += 1

            elif new_row == ROWS - 1 and piece.color == BLACK and piece.king == False:
                piece.make_king()
                self.black_kings += 1
        

    def get_piece(self, row, col):
        # returns either 0 for empty space, and an instance of Piece class if a piece
        return self.board[row][col]

    def create_board(self):
        # couldn't make np.array work with both int and object types in the same array
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS): 
                # in a checkerboard pattern create pieces, if first half of the board then black else white, if empty then 0
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
        # draw only the pieces on the screen
        self.draw_checkerboard(window)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(window)

    def get_valid_moves(self, piece):
        # moves is a dictionary of possible moves as keys and value informing if a piece was skipped.
        # If a piece has been skipped then the value takes the form of a skipped piece coordinate
        moves = {}
        diagonals = []
        # create an array of coordinates from 0,0 to ROWS-1, COLS-1
        positions = [[[j, i] for i in range(ROWS)] for j in range(COLS)]
        row = piece.row
        col = piece.col

        # Create all possible directions of movement for a piece, if king piece can move through whole board
        if piece.king:
            # first diagonal with offset of -(row - col)
            diag1 = (np.diagonal(positions, -(row - col)).T).tolist()

            # second diagonal with offset accounted for the flip
            diag2 = (
                np.flipud(positions).diagonal(-(ROWS - 1 - row - col)).T).tolist()

            # find the index of position of current piece in the diagonal array
            piece_idx_1 = diag1.index([row, col])
            piece_idx_2 = diag2.index([row, col])

            # split two diagonals into 4 lists representing 4 directions that go in order from the piece's position
            # e. g. piece on 2,2 can move forward left to 1,1 or 0,0, back left 3,1 or 4,0
            # forward right 1,3 -> 0, 4 or back right which on a 10x10 board would be (in order, which is important)
            # 3,3 -> 4,4 -> 5,5 -> 6,6 -> 7,7 -> 8,8 -> 9,9
            forward_left = list(reversed(diag1[:piece_idx_1]))
            back_left = list(reversed(diag2[:piece_idx_2]))

            # we ignore the current piece's position, so we use the try and except in case the piece is on the edge of the board. 
            # this will be changed to check if piece is on the border, then piece_idx +1 else, empty array
            try:
                forward_right = diag2[piece_idx_2+1:]
            except IndexError:
                forward_right = None

            try:
                back_right = diag1[piece_idx_1+1:]
            except IndexError:
                forward_right = None

            # create an 3-deep array of directions, their coordinates, and row, col if direction was created - ergo not an edge piece
            directions = [forward_left, back_left, forward_right, back_right]
            for direction in directions:
                if direction != None:
                    diagonals.append(direction)
        # if not a king piece, only possible directions of movement are the corner spaces on the board. 
        # piece's directions recognzies if a piece is white or black
        else:
            diagonals = [
                [[row + piece.direction, col - piece.direction]],
                [[row + piece.direction, col + piece.direction]],
                [[row - piece.direction, col - piece.direction]],
                [[row - piece.direction, col + piece.direction]]
                ]

        # first check if there is possible skip over other pieces as it's required to skip
        # in the rules if possible.
        for diagonal in diagonals:
            # we check if a piece was skipped on each diagonal separately
            skipped = False
            for coordinates in diagonal:                
                if not self.is_outside_board(coordinates):
                    # row and columns directions (-1, +1 for a row and col)
                    row_dir, col_dir = self.get_direction(row, col, coordinates[0], coordinates[1])

                    # if space on board is empty and piece hasn't been skipped yet and current coordinate as a viable move
                    if self.board[coordinates[0]][coordinates[1]] == 0 and not skipped:
                        if piece.king:
                            moves[str(coordinates)] = False
                        elif piece.direction == row_dir:
                            moves[str(coordinates)] = False

                    # if space on board is empty but a piece has been skipped, then add current coordinate as viable move
                    # and add previous coordinate as a skipped piece's coordinate
                    elif self.board[coordinates[0]][coordinates[1]] == 0 and skipped:
                        skipped_to_row, skipped_to_col = coordinates[0], coordinates[1]
                        if not self.is_outside_board([skipped_to_row, skipped_to_col]):
                            moves[str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col]) 
                            

                    # if no piece's on the diagonal have been skipped
                    # and the color of the piece at current coordinate is different then player's color
                    # mark this move as a skip for next move in the diagonal if a piece is king. 
                    # else just mark the move as viable with the skip information for non king piece.
                    elif not skipped and self.board[coordinates[0]][coordinates[1]].color != piece.color:
                            skipped_row, skipped_col = row_dir+row, col_dir+col 
                            if piece.king:
                                skipped = True                              
                            else:
                                skipped_to_row, skipped_to_col = row_dir*2+row, col_dir*2+col
                                if not self.is_outside_board([skipped_to_row, skipped_to_col]) and self.board[skipped_to_row][skipped_to_col] == 0:
                                    moves[str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col])
                    
                    # can't skip past own color, so we can break out of the whole diagonal and move to another diagonal               
                    elif self.board[coordinates[0]][coordinates[1]].color == piece.color:
                            break                        
        
        # if any(value != False for value in moves.values()):
        #     skip_only_moves = {k: v for k, v in moves.items() if v != False}
        #     print(skip_only_moves)
        #     return skip_only_moves             
        
        return moves

    def get_direction(self, row, col, new_row, new_col):
        #calulates the direction of movement on the board for non king piece
        row_dir = new_row - row
        col_dir = new_col - col
        return row_dir, col_dir

    def is_outside_board(self, coordinates):
        # checks if a move is made within board boundaries
        row, col = coordinates
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return True
        return False

    def remove_piece(self, piece):
        # remove the piece from the board and update board attributes
        self.board[piece.row][piece.col] = 0
        if piece.color == WHITE:
            self.white_left -= 1
            if piece.king:
                self.white_kings -= 1
        else:
            self.black_left -= 1
            if piece.king:
                self.black_kings -= 1
