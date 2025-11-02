import pygame

# Screen dimensions for 4 junctions (2x2 grid) - REDUCED SIZE
WIDTH, HEIGHT = 1440, 1440
DARK_GREEN = (82, 183, 136)
BLACK = (30, 30, 30)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

signal_color_map = {"green": (100, 220, 100), "red": (220, 50, 50), "yellow": (255, 215, 0)}

# Junction positions (top-left corner of each junction)
JUNCTIONS = {
    "j1": (0, 0),           # Top-left
    "j2": (720, 0),         # Top-right
    "j3": (0, 720),         # Bottom-left
    "j4": (720, 720)        # Bottom-right
}

JUNCTION_WIDTH = 720
JUNCTION_HEIGHT = 720

def draw_junction(offset_x, offset_y, signals_dict, junction_id):
    """Draw a single junction at the given offset position."""
    
    # ROAD DRAWING (relative to offset) - scaled down
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 0, 144, 285))     # Top road
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 429, 144, 291))   # Bottom road
    pygame.draw.rect(screen, BLACK, (offset_x + 0, offset_y + 285, 288, 144))     # Left road
    pygame.draw.rect(screen, BLACK, (offset_x + 432, offset_y + 285, 288, 144))   # Right road
    pygame.draw.rect(screen, BLACK, (offset_x + 288, offset_y + 285, 144, 144))   # Center intersection
    
    # LANE DRAWINGS
    points_top = [(offset_x + 360, offset_y + 0), (offset_x + 360, offset_y + 270)]
    pygame.draw.lines(screen, YELLOW, False, points_top, 2)
    
    points_bottom = [(offset_x + 360, offset_y + 720), (offset_x + 360, offset_y + 445)]
    pygame.draw.lines(screen, YELLOW, False, points_bottom, 2)

    points_left = [(offset_x + 0, offset_y + 357), (offset_x + 270, offset_y + 357)]
    pygame.draw.lines(screen, YELLOW, False, points_left, 2)

    points_right = [(offset_x + 720, offset_y + 357), (offset_x + 450, offset_y + 357)]
    pygame.draw.lines(screen, YELLOW, False, points_right, 2)

    # SIGNAL LIGHTS [top, bottom, right, left] - scaled down
    pygame.draw.rect(screen, signal_color_map[signals_dict["top"]], 
                     (offset_x + 360, offset_y + 268, 73, 17))
    pygame.draw.rect(screen, signal_color_map[signals_dict["bottom"]], 
                     (offset_x + 288, offset_y + 429, 73, 17))
    pygame.draw.rect(screen, signal_color_map[signals_dict["right"]], 
                     (offset_x + 432, offset_y + 357, 18, 73))
    pygame.draw.rect(screen, signal_color_map[signals_dict["left"]], 
                     (offset_x + 270, offset_y + 285, 18, 73))


def draw_scene(all_signals):
    """Draw the entire scene with 4 junctions."""
    screen.fill(DARK_GREEN)
    
    # Draw all 4 junctions
    for junction_id, (offset_x, offset_y) in JUNCTIONS.items():
        draw_junction(offset_x, offset_y, all_signals[junction_id], junction_id)


def draw_car(car):
    """Draw a single car as a circle with color based on turn direction"""
    import math
    
    # Car radius
    car_radius = 8
    
    # Color based on turn direction
    color_map = {
        "straight": (100, 150, 255),  # Blue
        "left": (255, 100, 100),      # Red
        "right": (150, 255, 150)      # Green
    }
    color = color_map.get(car.get("turn", "straight"), (255, 255, 100))
    
    # Draw circle at car position
    center_x = int(car["x"] + 10)
    center_y = int(car["y"] + 10)
    
    # Main circle
    pygame.draw.circle(screen, color, (center_x, center_y), car_radius)
    
    # Add a small direction indicator (white dot)
    direction = car["lane"].split('_')[-1] if "_" in car["lane"] else "bottom"
    indicator_offset = 4
    
    if car.get("turning") or car.get("angle", 0) != 0:
        # Use angle for turning cars
        angle_rad = math.radians(car.get("angle", 0) - 90)
        indicator_x = center_x + int(indicator_offset * math.cos(angle_rad))
        indicator_y = center_y + int(indicator_offset * math.sin(angle_rad))
    else:
        # Use direction for straight cars
        if direction in ["bottom", "down"]:
            indicator_x, indicator_y = center_x, center_y - indicator_offset
        elif direction in ["top", "up"]:
            indicator_x, indicator_y = center_x, center_y + indicator_offset
        elif direction == "left":
            indicator_x, indicator_y = center_x + indicator_offset, center_y
        else:  # right
            indicator_x, indicator_y = center_x - indicator_offset, center_y
    
    pygame.draw.circle(screen, (255, 255, 255), (indicator_x, indicator_y), 2)


def draw_all_cars(cars):
    """Draw all cars in the simulation"""
    for car in cars:
        draw_car(car)


# Junction boundaries for position checking - UPDATED for smaller size
JUNCTION_BOUNDARIES = {
    "j1": {"x_min": 0, "x_max": 720, "y_min": 0, "y_max": 720},
    "j2": {"x_min": 720, "x_max": 1440, "y_min": 0, "y_max": 720},
    "j3": {"x_min": 0, "x_max": 720, "y_min": 720, "y_max": 1440},
    "j4": {"x_min": 720, "x_max": 1440, "y_min": 720, "y_max": 1440}
}