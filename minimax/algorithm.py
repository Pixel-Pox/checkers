from copy import deepcopy
from cachetools import cached, LRUCache
from cachetools.keys import hashkey
from ast import literal_eval
from typing import Tuple

BLACK = (0,0,0)
WHITE = (255, 255, 255)

# caching doesn't work too well on the recursive funciton. If you remove the depth from the hashkey's the game
# will be a lot faster, but only in bursts of the depth length. This also makes the AI make a decision once every /depth/
# moves. If depth is included the caching doesn't give any results. 

# The main minimax function
#@cached(LRUCache(maxsize=10000), key=lambda move, depth, max_player, alpha, beta: hashkey(move, max_player, depth))
def minimax(move: object, depth: int, max_player: tuple, alpha: float, beta: float) -> Tuple[float, object]:
    if depth == 0:
        return move.evaluate(), move

    # if white player, that tries to maximize the score
    if max_player:
        max_eval = float('-inf')
        best_move = None
        # get all possible moves for a player
        for move in get_all_moves(move, WHITE):
            # recursive call to minimax for evaulation of the board
            evaluation = minimax(move, depth -1, False, alpha, beta)[0]
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, max_eval)
            if max_eval == evaluation: 
                best_move = move
            # alpha beta pruning
            if beta <= alpha:
                break
            
        return max_eval, best_move
    
    # if black player, that tries to minimize the score
    else:
        min_eval = float('inf')
        best_move = None
        # get all possible moves for a player
        for move in get_all_moves(move, BLACK):
            # recursive call to minimax for evaulation of the board
            evaluation = minimax(move, depth -1, True, alpha, beta)[0]
            min_eval = min(min_eval, evaluation)
            beta = min(beta, min_eval)
            if min_eval == evaluation: 
                best_move = move
            # alpha beta pruning
            if beta <= alpha:
                break

        return min_eval, best_move

# simulates the move
def simulate_move(piece: object, move: list, board: object, skip: list, color: object) -> object:
    # on the copied board make a move from the list of possible moves
    board.move(piece, move[0], move[1])
    
    # if a piece is skipped during the simulated move, remove a skipped piece
    if skip: 
        removed_piece = board.get_piece(skip.row, skip.col)
        board.remove_piece(removed_piece)

        # if after skipping there is another skip available, keep current players turn and allow him to move only the selected piece.
        piece = board.get_piece(piece.row, piece.col)
        valid_moves, skipped = board.get_valid_moves(color)
        if skipped and piece in valid_moves.keys(): 
            for m, s in valid_moves[piece].items():
                m = literal_eval(m)
                s = board.get_piece(literal_eval(s)[0], literal_eval(s)[1])
                simulate_move(piece, m, board, s, color)
                return board
            
        # make a piece into a king if the piece is on the edge of the board
        board.make_king(piece, move[0])    
        # return the board modified by the simualted move
        return board

    # make a piece into a king if the piece is on the edge of the board
    board.make_king(piece, move[0])    
    # return the board modified by the simualted move
    return board

# returns all possible moves for the current board state
def get_all_moves(board: object, color: tuple) -> list:
    possible_board_states = []
    valid_moves, _ = board.get_valid_moves(color)
    # for each piece with valid moves
    for piece in valid_moves:
        for move, skip in valid_moves[piece].items():
            # change the string coordinates into a literal list
            move = literal_eval(move)
            # if that move has a skip, change the string coordinates into a literal list
            if skip: 
                skip = board.get_piece(literal_eval(skip)[0], literal_eval(skip)[1])
            # make a deepcopy of the board
            temp_board = deepcopy(board)
            # get a piece from the copied board
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            # simulate a move on the copied board
            new_board = simulate_move(temp_piece, move, temp_board, skip, color)
            possible_board_states.append(new_board)
     
    return possible_board_states