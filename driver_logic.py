import math
import random
import pygame

from signal_control import signals
from paths import TURN_PATHS
from lane_config import LANES

car_speed = 2
CAR_SPACING = 60 
STOP_MARGIN = 25

cars = []
cars_passed = 0

def get_stats():
    return {
        "cars_passed": cars_passed,
        "total_cars": len(cars)
    }

def distance(c1, c2):
    return math.sqrt((c1["x"] - c2["x"])**2 + (c1["y"] - c2["y"])**2)

def can_spawn(pos, lane_dir):
    """Check if a car can spawn at the given position"""
    MIN_SPAWN_DISTANCE = 100 
    
    for car in cars:
        # check if car is (nearby && in same lane)
        if car["lane"] == lane_dir:
            dx = abs(car["x"] - pos[0])
            dy = abs(car["y"] - pos[1])
            
            if lane_dir in ["bottom", "top"]:
                if dx < 30 and dy < MIN_SPAWN_DISTANCE:
                    return False
            else:
                if dy < 30 and dx < MIN_SPAWN_DISTANCE:
                    return False
    return True


def draw_car(screen):
    """Draw all cars with color based on turn direction and white dot indicator"""
    
    # Color map based on turn direction
    color_map = {
        "straight": (100, 150, 255),  # Blue
        "left": (255, 100, 100),      # Red
        "right": (150, 255, 150)      # Green
    }
    
    for car in cars:
        # Determine color
        if car.get("is_ambulance", False):
            color = (255, 0, 0)  # Red for ambulance
            radius = 12
        else:
            turn_type = car.get("turn", "straight")
            color = color_map.get(turn_type, (255, 255, 100))
            radius = 10

        # Car center position
        center_x = int(car["x"] + 10)
        center_y = int(car["y"] + 10)

        # Draw main car circle
        pygame.draw.circle(screen, color, (center_x, center_y), radius)
        
        # Draw white dot direction indicator
        indicator_offset = 4
        direction = car["lane"]
        
        # Calculate indicator position based on direction or angle
        if car.get("turning") or car.get("angle", 0) != 0:
            # Use angle for turning cars
            angle_rad = math.radians(car.get("angle", 0) - 90)
            indicator_x = center_x + int(indicator_offset * math.cos(angle_rad))
            indicator_y = center_y + int(indicator_offset * math.sin(angle_rad))
        else:
            # Use direction for straight cars
            if direction == "bottom":
                indicator_x, indicator_y = center_x, center_y - indicator_offset
            elif direction == "top":
                indicator_x, indicator_y = center_x, center_y + indicator_offset
            elif direction == "left":
                indicator_x, indicator_y = center_x + indicator_offset, center_y
            else:  # right
                indicator_x, indicator_y = center_x - indicator_offset, center_y
        
        # Draw white dot indicator
        pygame.draw.circle(screen, (255, 255, 255), (indicator_x, indicator_y), 2)