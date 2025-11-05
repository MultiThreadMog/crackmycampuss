import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1440, 1440
DARK_GREEN = (82, 183, 136)
BLACK = (30, 30, 30)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coordinate Tool - Click to get coordinates")

font = pygame.font.Font(None, 36)

JUNCTIONS = {
    "j1": (0, 0),
    "j2": (720, 0),
    "j3": (0, 720),
    "j4": (720, 720)
}

def draw_junction(offset_x, offset_y):
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 0, 144, 285))
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 429, 144, 291))
    pygame.draw.rect(screen, BLACK, (offset_x + 0, offset_y + 285, 288, 144))
    pygame.draw.rect(screen, BLACK, (offset_x + 432, offset_y + 285, 288, 144))
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 285, 144, 144))
    
    points_top = [(offset_x + 360, offset_y + 0), (offset_x + 360, offset_y + 270)]
    pygame.draw.lines(screen, YELLOW, False, points_top, 2)
    
    points_bottom = [(offset_x + 360, offset_y + 720), (offset_x + 360, offset_y + 445)]
    pygame.draw.lines(screen, YELLOW, False, points_bottom, 2)

    points_left = [(offset_x + 0, offset_y + 357), (offset_x + 270, offset_y + 357)]
    pygame.draw.lines(screen, YELLOW, False, points_left, 2)

    points_right = [(offset_x + 720, offset_y + 357), (offset_x + 450, offset_y + 357)]
    pygame.draw.lines(screen, YELLOW, False, points_right, 2)
    
    pygame.draw.rect(screen, RED, (offset_x + 360, offset_y + 268, 73, 17))
    pygame.draw.rect(screen, RED, (offset_x + 288, offset_y + 429, 73, 17))
    pygame.draw.rect(screen, RED, (offset_x + 432, offset_y + 357, 18, 73))
    pygame.draw.rect(screen, RED, (offset_x + 270, offset_y + 285, 18, 73))

clicked_pos = None

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked_pos = pygame.mouse.get_pos()
    
    screen.fill(DARK_GREEN)
    
    for junction_id, (offset_x, offset_y) in JUNCTIONS.items():
        draw_junction(offset_x, offset_y)
    
    if clicked_pos:
        pygame.draw.circle(screen, WHITE, clicked_pos, 8)
        coord_text = font.render(f"({clicked_pos[0]}, {clicked_pos[1]})", True, WHITE)
        screen.blit(coord_text, (clicked_pos[0] + 15, clicked_pos[1] - 20))
    
    mouse_pos = pygame.mouse.get_pos()
    cursor_text = font.render(f"{mouse_pos[0]}, {mouse_pos[1]}", True, WHITE)
    screen.blit(cursor_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()