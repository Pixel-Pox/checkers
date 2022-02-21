import pygame
from checkers.constants import SQUARE_SIZE, WIDTH, HEIGHT
from checkers.board import Board
from checkers.game import Game

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
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_position_mouse(pos)
                game.select(row, col)
        
        game.update()
    
    pygame.quit()


if __name__ == "__main__":
    print("I'm a game creator now.")
    pygame.display.set_caption("Checkers")
    main()


