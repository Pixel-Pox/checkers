from functools import cached_property, lru_cache
import pygame
import numpy as np
from .piece import Piece
from .constants import BLACK, DARK_BROWN, LIGHT_BROWN, ROWS, SQUARE_SIZE, COLS, WHITE
from collections import defaultdict
from random import choice
from typing import Tuple


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
    
    # draw a colorful checkerboard as a background
    def draw_checkerboard(self, window) -> None:       
        window.fill(BLACK)
        for row in range(ROWS):
            for col in range(COLS):
                if self.background[row][col] == 1:
                    pygame.draw.rect(
                        window, DARK_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                else:
                    pygame.draw.rect(
                        window, LIGHT_BROWN, (row*SQUARE_SIZE, col*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # checks for a tie condition
    def is_tie(self) -> bool:
        # 30 consecutive moves with a king piece without skipping are considered a tie
        if self.king_moves == 30:
            return True
        return False

    # checks for winning conditions 
    def is_won(self, current_player: tuple) -> bool:              
        # checking next player
        next_player = None        
        if current_player == WHITE:
            next_player = BLACK
        else:
            next_player = WHITE

        # if there are no more pieces on the board for next player, current player wins
        if next_player == WHITE and self.white_left == 0:
            return True
        elif next_player == BLACK and self.black_left == 0:
            return True

        # if there are no moves available for the next player, current player wins
        next_player_moves = self.get_valid_moves(next_player)[0]
        for move in next_player_moves.keys():
            if next_player_moves[move].keys():
                return False
        
        return True
        
    # evaluation function for the current board state
    def evaluate(self) -> float:
        # if win for black evaluation is -infinity
        if self.is_won(BLACK):
            return float('-inf')
        # if win for white evaluation is +infinity
        elif self.is_won(WHITE):
            return float('inf')
        # if board state is a tie then evaluation is 0 - draw
        elif self.is_tie():
            return 0

        # random component of the evaluation to make the game less deterministic
        random_eval = choice([-0.1, 0.1])
        sum_king_dist_white = 0 
        sum_king_dist_black = 0

        whites = self.get_all_side_pieces(WHITE)
        blacks = self.get_all_side_pieces(BLACK)

        # calculation of the average distance of all pieces to the edge of the oponent side (making a king)
        # less the absolute value for each player the better the evaluation for that player.
        # This encourages moving more pieces and trying to take control of the centre instead 
        # of pushing just one piece.
        for piece in whites: 
            sum_king_dist_white += piece.dist_to_king
        for piece in blacks: 
            sum_king_dist_black += piece.dist_to_king
        
        # creating a weight of 2 for the distance
        average_king_dist_white = 2*(len(whites)*ROWS - (sum_king_dist_white / len(whites)))
        average_king_dist_black = (-2)*(len(whites)*ROWS - (sum_king_dist_black / len(blacks)))

        # number of pieces are evaluated at 3 points per normal piece, 5 per king piece. 
        # weight of the total pieces is 5 on top of that. 
        total_pieces = 3*self.white_left - 3*self.black_left + (5*self.white_kings - 5*self.black_kings)
        return 5*total_pieces + 2*(average_king_dist_black) + 2*average_king_dist_white + random_eval

    # returns all pieces of the passed side as a list
    def get_all_side_pieces(self, color: tuple) -> list:
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    # move function for the pieces on the board
    def move(self, piece: object, new_row: int, new_col: int) -> None:
        # swap position of a piece with empty space, returns True if King has been made to end turn
        self.board[piece.row][piece.col], self.board[new_row][new_col] = self.board[new_row][new_col], self.board[piece.row][piece.col]
        
        # change the row and col values of a Piece object
        piece.move(new_row, new_col)

        # if a moved piece is a king piece and no skip has been done then increase the "tie" counter else zero it
        if piece.king and not self.skipped:
            self.king_moves += 1
        else:
            self.king_moves = 0 

    # if conditions are met, changes a piece to a king piece
    def make_king(self, piece: object, new_row: int) -> None:
        # if passed piece is an instance of a Piece class
        if piece != 0:
            # if not already a king piece and on the opposite end of the board, change a piece to a king
            if new_row == 0 and piece.color == WHITE and piece.king == False:
                piece.make_king()
                self.white_kings += 1

            elif new_row == ROWS - 1 and piece.color == BLACK and piece.king == False:
                piece.make_king()
                self.black_kings += 1
        
    # returns either 0 for empty space, and an instance of Piece class if a piece
    def get_piece(self, row: int, col: int) -> object:        
        return self.board[row][col]

    # create the initial board setup with white pieces on the bottom and black on the top
    def create_board(self) -> None:
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

    # draw the window function
    def draw(self, window):
        # redraw the background
        self.draw_checkerboard(window)
        # draw only the pieces
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(window)

    # returns possible moves for all pieces of passed player(color), and information if a move involves a skip
    def get_valid_moves(self, color: tuple) -> Tuple[dict, bool]:
        # moves is a dictionary which keys are an instance of a Piece class of "color" side, 
        # values are a dictionaries of key, value pairs where key is a possible move coordinate as a string
        # and value is either False for no skip involved, or a coordinate of a skipped piece
        moves = defaultdict(dict)
        skip_only_moves = defaultdict(dict)
        diagonals = []
        
        # create a 2d array of coordinates as tuples from (0,0) to (ROWS-1, COLS-1)
        positions = [[(j, i) for i in range(ROWS)] for j in range(COLS)]
        
        # create a flipped board of both positions and pieces to find a second diagonal of moves
        flipped_positions = np.fliplr(positions)
        flipped_board = np.fliplr(self.board)
        
        all_pieces = self.get_all_side_pieces(color)


        for piece in all_pieces:
            diagonals = []
            # during flip, row stays the same, below finds the new column on a flipped board
            flipped_piece_col = int(np.where(flipped_board == piece)[1])
            row = piece.row
            col = piece.col
            moves[piece] = {}
            # Create all possible directions of movement for a piece, if piece is a king it can move through the whole board
            if piece.king:
                # first diagonal with offset of col - row, transposed into a list of coordinate lists
                diag1 = (np.diagonal(positions, col - row).T).tolist()

                # second diagonal with offset accounted for the flip
                diag2 = np.fliplr((flipped_positions.diagonal(flipped_piece_col - row).T)).tolist()

                # find the index of position of current piece in the diagonal array
                piece_idx_1 = diag1.index([row, col])
                piece_idx_2 = diag2.index([row, col])

                # split two diagonals into 4 lists representing 4 directions that go in order from the piece's position
                # e.g. piece on 2,2 can move forward left to 1,1 or 0,0, back left 3,1 or 4,0
                # forward right 1,3 -> 0, 4 or back right which on a 10x10 board would be (in order, which is important)
                # 3,3 -> 4,4 -> 5,5 -> 6,6 -> 7,7 -> 8,8 -> 9,9
                forward_left = list(reversed(diag1[:piece_idx_1]))
                back_left = list(reversed(diag2[:piece_idx_2]))

                # we ignore the current piece's position, so we use the try and except in case the piece is on the edge of the board
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
            else:
                diagonals = [
                    [[row + piece.direction, col - piece.direction]],
                    [[row + piece.direction, col + piece.direction]],
                    [[row - piece.direction, col - piece.direction]],
                    [[row - piece.direction, col + piece.direction]]
                    ]

            for diagonal in diagonals:
                # for each diagonal we check if a skip occured separately 
                skipped = False
                for coordinates in diagonal:           
                    # if by any chance coordinates were outside of the board     
                    if not self.is_outside_board(coordinates):
                        # row and column directions (-1/+1)
                        row_dir, col_dir = self.get_direction(row, col, coordinates[0], coordinates[1])

                        # if space on board is empty and a piece hasn't been skipped add a possible move to moves
                        if self.board[coordinates[0]][coordinates[1]] == 0 and not skipped:
                            if piece.king:
                                moves[piece][str(coordinates)] = False
                            elif piece.direction == row_dir:
                                moves[piece][str(coordinates)] = False

                        # if there are 2 consecutive pieces in a diagonal, break out of that diagonal
                        elif self.board[coordinates[0]][coordinates[1]] != 0 and skipped:
                            break

                        # if space on board is empty but a piece has been skipped, then add current coordinate as viable move
                        # and add previous coordinate as a skipped piece's coordinate
                        elif self.board[coordinates[0]][coordinates[1]] == 0 and skipped:
                            skipped_to_row, skipped_to_col = coordinates[0], coordinates[1]
                            if not self.is_outside_board([skipped_to_row, skipped_to_col]):
                                moves[piece][str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col]) 
                                
                        # if no piece have been skipped and the color of the piece at current coordinate is different then player's color
                        # mark this move as a skip for next move in the diagonal if a piece is king. 
                        # else just mark the move as viable with the skip information for non king piece.
                        elif not skipped and self.board[coordinates[0]][coordinates[1]].color != piece.color:
                                skipped_row, skipped_col = row_dir+row, col_dir+col 
                                if piece.king:
                                    skipped = True                              
                                else:
                                    skipped_to_row, skipped_to_col = row_dir*2+row, col_dir*2+col
                                    # if the move after the skip is not outside of the board, then add it to the possible moves list
                                    if not self.is_outside_board([skipped_to_row, skipped_to_col]) and self.board[skipped_to_row][skipped_to_col] == 0:
                                        moves[piece][str([skipped_to_row, skipped_to_col])] = str([skipped_row, skipped_col])
                        
                        # if a piece on the diagonal is the same color as the current player, then break out of that diagonal               
                        elif self.board[coordinates[0]][coordinates[1]].color == piece.color:
                                break         
                        else:
                            break               
        
        # if any of the moves has a skip available, create a dictionary of only such moves, as skips are obligatory,
        # therefor we are removing all other possible moves
        for piece in moves:
            skip_only_moves[piece] = {k: v for k, v in moves[piece].items() if v != False}

        # only remaining movable pieces are the ones with possible moves    
        skip_only_moves = {k: v for k, v in skip_only_moves.items() if v}    

        # if skip_only_moves is not empty, then return it as tuple of possible moves, and information if a move has been skipped
        if len(skip_only_moves) >= 1:
            return skip_only_moves, True
        
        # if no skips available, return the moves, and the information that there are no skips
        return moves, False

    # calculates the direction of the diagonal by returning positive or negative 1 in place of a row and col
    def get_direction(self, row: int, col: int, new_row: int, new_col: int) -> Tuple[int, int]:
        #calulates the direction of movement on the board for non king piece
        row_dir = new_row - row
        col_dir = new_col - col
        return row_dir, col_dir

    # checks if a move is made within board boundaries
    def is_outside_board(self, coordinates: tuple) -> bool:        
        row, col = coordinates
        if row < 0 or col < 0 or row >= ROWS or col >= COLS:
            return True
        return False

    # remove the piece from the board and update board attributes
    def remove_piece(self, piece: object):        
        self.board[piece.row][piece.col] = 0
        if piece.color == WHITE:
            self.white_left -= 1
            if piece.king:
                self.white_kings -= 1
        else:
            self.black_left -= 1
            if piece.king:
                self.black_kings -= 1
