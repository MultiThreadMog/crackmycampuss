import pygame

from signal_control import RED,YELLOW,GREEN,signals,signal_colors

WIDTH, HEIGHT = 1080, 1070
DARK_GREEN = (82, 183, 136)
BLACK = (30, 30, 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

signal_color_map = {"green": (100,220,100), "red": (220,50,50), "yellow": (255,215,0)}

def draw_scene():

    screen.fill(DARK_GREEN)  

    # ROAD DRAWING
    pygame.draw.rect(screen, BLACK, (432, 0, 216, 427))  
    pygame.draw.rect(screen, BLACK, (432, 643, 216, 427))  

    pygame.draw.rect(screen, BLACK, (0, 427, 432, 216))  
    pygame.draw.rect(screen, BLACK, (648, 427, 432, 216)) 
    
    pygame.draw.rect(screen, BLACK, (432, 427, 216, 216))
    
    # LANE DRAWINGS
    points_top = [(540, 0),(540,404)]
    pygame.draw.lines(screen, YELLOW, False, points_top, 3)
    
    points_bottom = [(540,1070),(540,668)]
    pygame.draw.lines(screen, YELLOW, False, points_bottom, 3)

    points_left = [(0, 535),(404,535)]
    pygame.draw.lines(screen, YELLOW, False, points_left, 3)

    points_right = [(1080,535),(676,535)]
    pygame.draw.lines(screen, YELLOW, False, points_right, 3)

    # signal [ top bottom right left ]
    pygame.draw.rect(screen, signal_colors[signals["top"]], (540, 402, 109, 25))
    pygame.draw.rect(screen, signal_colors[signals["bottom"]], (432, 643, 109, 25))
    pygame.draw.rect(screen, signal_colors[signals["right"]], (648, 535, 28, 109))
    pygame.draw.rect(screen, signal_colors[signals["left"]], (404, 427, 28, 109))