import pygame
from ast import literal_eval
from checkers.board import Board
from checkers.constants import WHITE, BLACK, BLUE, SQUARE_SIZE, ROWS


class Game:
    def __init__(self, window) -> None:
        #function for init to easly reset the game state to initial
        self._init()
        self.window = window

    def update(self):
        self.board.draw(self.window)
        self.draw_valid_moves(self.valid_moves, self.selected)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = WHITE
        self.valid_moves = {}
        self.winner = None

    def reset(self):
        self._init()

    def is_won(self):              
        #checking next player
        next_player = None        
        if self.turn == WHITE:
            next_player = BLACK
        else:
            next_player = WHITE
        #if there are no more pieces on the board for next player, current player wins
        if next_player == WHITE and self.board.white_left == 0:
            return True
        elif next_player == BLACK and self.board.black_left == 0:
            return True

        #if there are no moves available for the next player, current player wins
        for idx_row, _ in enumerate(self.board.board):
            for idx_col, _ in enumerate(self.board.board[idx_row]):
                piece = self.board.board[idx_row][idx_col]
                if piece != 0 and piece.color == next_player and self.board.get_valid_moves(self.turn)[0]:
                    return False
        
        return True

    def is_tie(self):
        #if each player makes 15 moves with a king without any skipped pieces the game is a tie
        if self.board.king_moves == 30:
            return True
        return False


    def select(self, row, col):
        #if a piece has been skipped, mark it, else select a piece
        if self.board.skipped:
            piece = self.board.skipped
        else:
            piece = self.board.get_piece(row, col)
        #if piece selected, try to move it, else just select a new piece
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        #if selected is an instance of Piece and it's current player's piece, check all valid moves for that piece
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves, _ = self.board.get_valid_moves(self.turn)
            return True

        return False

    def _move(self, row, col):
        #get selected spot on the board
        piece = self.board.get_piece(row, col)
        #if selected is an empty space, and is a valid move, then make that move
        if self.selected and piece == 0 and str([row, col]) in self.valid_moves[self.selected].keys():
            self.board.move(self.selected, row, col)

            # if skipped, remove skipped piece
            if self.valid_moves[self.selected][str([row, col])]:
                skipped_piece = literal_eval(self.valid_moves[self.selected][str([row, col])])
                remove_piece = self.board.get_piece(
                    skipped_piece[0], skipped_piece[1])
                self.board.remove_piece(remove_piece)

                # if after skipping there is another skip available, keep current players turn and allow him to move only the selected piece.
                piece = self.board.get_piece(row, col)
                self.valid_moves, _ = self.board.get_valid_moves(self.turn)
                if any(value != False for value in self.valid_moves[piece].values()):
                    self.board.skipped = piece
                    self.select(row, col)
                else:
                    #if a piece gets to opposite end, make it a king and change turn
                    if row == 0 or row == ROWS-1:
                        self.board.make_king(self.selected, row)
                        self.change_turn()
                        return True

            #if a piece gets to opposite end, make it a king and change turn
            else:
                if row == 0 or row == ROWS-1:
                    self.board.make_king(self.selected, row)
                    self.change_turn()
                    return True

            if not self.board.skipped:
                self.change_turn()

            self.board.skipped = None
        return True

    def draw_valid_moves(self, moves, current_piece):
        #mark all possible moves with blue dot
        if current_piece in moves:
            for key, value in moves[current_piece].items():
                key_list = literal_eval(key)
                row, col = key_list[0], key_list[1]
                pygame.draw.circle(self.window, BLUE, (col * SQUARE_SIZE +
                                SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        #check if after last move, the game is won or a tie, else reset turn dependent variables
        if self.is_won():
            self.update()
            self.winner = self.turn
            print(f"AND THE WINNER IS {self.winner}")
            print(f"Do you want to play another round? y/n\n")
            if input() == 'y':
                self.reset()
            elif input() == 'n':
                pygame.quit() #doesn't work :P 

        elif self.is_tie():
            self.update()
            self.winner = None
            print(f"GAME HAS ENDED IN A DRAW DUE TO TOO MANY NON SKIP TYPE MOVES")
            print(f"Do you want to play another round? y/n\n")
            if input() == 'y':
                self.reset()
            elif input() == 'n':
                pygame.quit() #doesn't work :P 
        else:
            self.valid_moves = {}
            self.board.skipped = False
            self.selected = None
            if self.turn == WHITE:
                self.turn = BLACK
            else:
                self.turn = WHITE
    
    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()