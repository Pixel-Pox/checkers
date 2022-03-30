import pygame
from .constants import WHITE, BLACK, SQUARE_SIZE, RED, GOLD, ROWS

#Piece class taken from the Tech with Tim checkers video, modified for my needs

class Piece:
    PADDING = 10
    BORDER = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        
        if self.color == WHITE:
            self.direction = -1
            self.dist_to_king = self.row
        else:
            self.direction = 1
            self.dist_to_king = ROWS - self.row - 1

        self.x = 0
        self.y = 0
        self.calculate_position()

    def calculate_position(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE //2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE //2
        if self.color == WHITE:
            self.dist_to_king = self.row
        else:
            self.dist_to_king = ROWS - self.row - 1

    def make_king(self):
        self.king = True

    def draw(self, window):
        radius = SQUARE_SIZE//2 - self.PADDING
        pygame.draw.circle(window, RED, (self.x, self.y), radius + self.BORDER)
        if self.king:
            pygame.draw.circle(window, GOLD, (self.x, self.y), radius + self.BORDER)
            pygame.draw.circle(window, self.color, (self.x, self.y), radius - self.BORDER)
        else:
            pygame.draw.circle(window, self.color, (self.x, self.y), radius)

    def move(self, new_row, new_col):
        self.row = new_row
        self.col = new_col
        self.calculate_position()

    def __repr__(self):
        return str(self.color)

