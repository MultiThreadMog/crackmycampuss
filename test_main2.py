import pygame
import sys

# Import modules
from visualization_4junctions import screen, draw_scene, draw_all_cars, WIDTH, HEIGHT
from signal_control_4junctions import update_signals, update_vehicle_counts, all_signals, get_green_counts
from car_spacing_4junctions import update_car
from driver_logic_4junctions import cars, cars_passed

pygame.init()
pygame.display.set_caption("4-Junction Traffic Simulation with Turning")

# Simulation parameters
FPS = 60

# Game state
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

def draw_ui():
    """Draw UI information"""
    y_offset = 10
    
    # Total vehicle count
    text = font.render(f"Active Vehicles: {len(cars)}", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 25
    
    # Cars passed
    text = font.render(f"Cars Passed: {cars_passed}", True, (255, 255, 255))
    screen.blit(text, (10, y_offset))
    y_offset += 35
    
    # Green counts for each junction
    green_counts = get_green_counts()
    for junction_id in ["j1", "j2", "j3", "j4"]:
        junction_label = f"{junction_id.upper()} Green Cycles:"
        text = font.render(junction_label, True, (255, 255, 255))
        screen.blit(text, (10, y_offset))
        y_offset += 20
        
        counts = green_counts[junction_id]
        for direction, count in counts.items():
            count_text = f"  {direction}: {count}"
            text = font.render(count_text, True, (200, 200, 200))
            screen.blit(text, (10, y_offset))
            y_offset += 18
        y_offset += 5

def main():
    """Main simulation loop"""
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update simulation
        update_vehicle_counts(cars)
        update_signals(cars)
        update_car(all_signals)
        
        # Draw everything
        draw_scene(all_signals)
        draw_all_cars(cars)
        draw_ui()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()