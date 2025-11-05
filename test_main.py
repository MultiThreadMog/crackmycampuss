import pygame
import sys

from junction import WIDTH, HEIGHT, screen, draw_scene
from driver_logic import draw_car
from update_cars import update_car
from signal_control import update_signals, update_vehicle_counts, get_green_count
from driver_logic import cars
from draw_stats import draw_stats
from ambulance import update_ambulance_priority, spawn_ambulance

pygame.init()

pygame.display.set_caption("Intersection Scene")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # TEST: Press 1,2,3,4 to spawn ambulance in different lanes
            elif event.key == pygame.K_1:
                spawn_ambulance("bottom")
            elif event.key == pygame.K_2:
                spawn_ambulance("right")
            elif event.key == pygame.K_3:
                spawn_ambulance("top")
            elif event.key == pygame.K_4:
                spawn_ambulance("left")

    '''if state:
    # Check if there's already an ambulance in the simulation
        has_ambulance = any(car.get("is_ambulance", False) for car in cars)
        
        if not has_ambulance:
            spawn_ambulance("top")'''

    update_car()
    update_vehicle_counts(cars)
    update_signals()
    update_ambulance_priority()  # Handle ambulance priority
    
    draw_scene()
    draw_car(screen)
    draw_stats(screen, get_green_count())

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()