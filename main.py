import pygame
import argparse
from checkers.constants import SQUARE_SIZE, WIDTH, HEIGHT, WHITE, BLACK, PLAYER, WHITE_LEVEL, BLACK_LEVEL
from checkers.game import Game
from minimax.algorithm import minimax

FPS = 60
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))

#translates mouse position on the board into row and column of the board
def get_position_mouse(pos: tuple) -> tuple:
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
        

        if not game.board.is_won(game.turn) or not game.board.is_tie(game.turn):
            if game.turn == BLACK and BLACK_LEVEL:
                _, new_board = minimax(game.board, BLACK_LEVEL, False, float('-inf'), float('inf'))
                game.ai_move(new_board)
                

            elif game.turn == WHITE and WHITE_LEVEL:          
               _, new_board = minimax(game.board, WHITE_LEVEL, True, float('-inf'), float('inf'))
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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        
        game.update()
    
    pygame.quit()


if __name__ == "__main__":
    print("\nType -h for help\n")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-p",
                        "--player",
                        help="human player color: BLACK/WHITE, default WHITE - if None, white AI level is set to 3",
                        type=str, 
                        choices=["BLACK", "WHITE", "None"])
                        
    parser.add_argument("-b",
                        "--blacklevel",
                        help="Choose minimax depth for black player, default is 3",
                        type=int,
                        choices=range(1,8))
                        
    parser.add_argument("-w",
                        "--whitelevel",
                        help="Choose minimax depth for white player, dafault is no AI",
                        type=int,
                        choices=range(1,8))

    args = parser.parse_args()

    if args.player == "None":
        PLAYER = None
        WHITE_LEVEL = 3
    elif args.player == "BLACK":
        PLAYER = BLACK
        WHITE_LEVEL = 3
        BLACK_LEVEL = None
    elif args.player == "WHITE":
        PLAYER = WHITE
        BLACK_LEVEL = 3
        WHITE_LEVEL = None

    if args.blacklevel and args.player != "BLACK":
        BLACK_LEVEL = args.blacklevel

    if args.whitelevel and args.player != "WHITE":
        WHITE_LEVEL = args.whitelevel

    pygame.display.set_caption("Checkers")
    main()


