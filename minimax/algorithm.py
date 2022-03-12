from copy import deepcopy
from select import select
import pygame
from ast import literal_eval

BLACK = (0,0,0)
WHITE = (255, 255, 255)

def minimax(game, depth, max_player, alpha, beta):
    board = game.get_board()

    if depth == 0:
        return board.evaluate(), board

    if max_player:
        max_eval = float('-inf')
        best_move = None

        for move in get_all_moves(board, WHITE):
            evaluation = minimax(game, depth -1, False, alpha, beta)[0]
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
            evaluation = minimax(game, depth -1, True, alpha, beta)[0]
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
        valid_moves = board.get_valid_moves(piece)
        if any(value != False for value in valid_moves.values()) == True:
            for move, skip in valid_moves.items():
                move = literal_eval(move)
                if skip:
                    skip = board.get_piece(literal_eval(skip)[0], literal_eval(skip)[1])
                    simulate_move(piece, move, board, skip, color)
                    return board
            
        board.make_king(piece, move[0])    
        return board
    board.make_king(piece, move[0])
    return board

def get_all_moves(board, color):
    possible_board_states = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            move = literal_eval(move)
            if skip: 
                skip = board.get_piece(literal_eval(skip)[0], literal_eval(skip)[1])
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skip, color)
            possible_board_states.append(new_board)
     
    return possible_board_states