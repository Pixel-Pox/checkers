from copy import deepcopy
from select import select
import pygame
from ast import literal_eval

BLACK = (0,0,0)
WHITE = (255, 255, 255)

def minimax(move, depth, max_player, alpha, beta):
    board = move

    if depth == 0:
        return board.evaluate(), board

    if max_player:
        max_eval = float('-inf')
        best_move = None

        for move in get_all_moves(board, WHITE):
            evaluation = minimax(move, depth -1, False, alpha, beta)[0]
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, max_eval)
            if max_eval == evaluation: 
                best_move = move
            if beta <= alpha:
                break
            
        return max_eval, best_move
    
    else:
        min_eval = float('inf')
        best_move = None
        for move in get_all_moves(board, BLACK):
            evaluation = minimax(move, depth -1, True, alpha, beta)[0]
            min_eval = min(min_eval, evaluation)
            beta = min(beta, min_eval)
            if min_eval == evaluation: 
                best_move = move
            if beta <= alpha:
                break            
        return min_eval, best_move

def simulate_move(piece, move, board, skip, color):
    board.move(piece, move[0], move[1])
    
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
            
        board.make_king(piece, move[0])    
        return board
    board.make_king(piece, move[0])
    return board

def get_all_moves(board, color):
    possible_board_states = []
    valid_moves, _ = board.get_valid_moves(color)
    for piece in valid_moves:
        for move, skip in valid_moves[piece].items():
            move = literal_eval(move)
            if skip: 
                skip = board.get_piece(literal_eval(skip)[0], literal_eval(skip)[1])
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skip, color)
            possible_board_states.append(new_board)
     
    return possible_board_states