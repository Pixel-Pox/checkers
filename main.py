import pygame
from checkers.constants import SQUARE_SIZE, WIDTH, HEIGHT, WHITE, BLACK
from checkers.game import Game
from minimax.algorithm import minimax
from sys import argv

FPS = 60
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

def get_position_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WINDOW)

    while run: 
        clock.tick(FPS)
        #comment out if you don't want to play against the AI
        if not game.board.is_won(game.turn) or not game.board.is_tie(game.turn):
            if game.turn == BLACK:
                _, new_board = minimax(game.board, 3, False, float('-inf'), float('inf'))
                game.ai_move(new_board)
                

            else:          
               _, new_board = minimax(game.board, 3, True, float('-inf'), float('inf'))
               game.ai_move(new_board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_position_mouse(pos)
                game.select(row, col)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.reset()

        
        game.update()
    
    pygame.quit()


if __name__ == "__main__":
    print("I'm a game creator now.")
    pygame.display.set_caption("Checkers")
    main()


