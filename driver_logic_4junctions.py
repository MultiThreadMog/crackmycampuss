import random
import math

# Global car list
cars = []
cars_passed = 0

# Parameters
car_speed = 2  # Scaled down from 3
STOP_MARGIN = 7  # Scaled down from 10

def distance(car1, car2):
    """Calculate Euclidean distance between two cars"""
    dx = car1["x"] - car2["x"]
    dy = car1["y"] - car2["y"]
    return math.sqrt(dx * dx + dy * dy)

def can_spawn(pos, lane_name):
    """Check if spawn position is clear"""
    spawn_x, spawn_y = pos
    for car in cars:
        if car["lane"] == lane_name:
            dist = math.sqrt((car["x"] - spawn_x)**2 + (car["y"] - spawn_y)**2)
            if dist < 60:  # Scaled spawn distance
                return False
    return True

def get_signal_for_lane(lane_name, all_signals):
    """Get signal color for a specific lane"""
    # Extract junction and direction from lane name (e.g., "j1_bottom" -> "j1", "bottom")
    parts = lane_name.split('_')
    if len(parts) >= 2:
        junction_id = parts[0]
        direction = parts[1]
        return all_signals.get(junction_id, {}).get(direction, "red")
    return "red"