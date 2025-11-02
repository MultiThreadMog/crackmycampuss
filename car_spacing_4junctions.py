"""
COMPLETE FIXED car_spacing_4junctions.py
ABSOLUTE RED LIGHT ENFORCEMENT - CARS PHYSICALLY CANNOT PASS RED SIGNALS
"""

from driver_logic_4junctions import cars, car_speed, can_spawn, distance, STOP_MARGIN, get_signal_for_lane
import driver_logic_4junctions
from paths_4junctions import TURN_PATHS
from lane_config_4junctions import LANES
import random
import math

CAR_SPACING = 40
MIN_COLLISION_DISTANCE = 18
ACCELERATION = 0.1
DECELERATION = 0.3  # Strong braking

# ============================================================================
# SPAWNING - ONLY 8 LOCATIONS
# ============================================================================

def _choose_turn_direction():
    """Randomly choose left, right, or straight with probabilities"""
    p_left = random.uniform(0.1, 0.3)    
    p_right = random.uniform(0.1, 0.3)   
    
    turn_choice = random.random()
    if turn_choice < p_left:
        return "left"
    elif turn_choice < p_left + p_right:
        return "right"
    return "straight"


def _get_spawn_index(lane_name, turn_type):
    """Determine which spawn point based on lane and turn"""
    direction = lane_name.split('_')[-1]
    
    if turn_type == "left":
        return 0 if direction == "bottom" else 1
    elif turn_type == "right":
        return 1 if direction == "bottom" else 0
    return random.randint(0, 1)


def _spawn_new_cars():
    """Spawn cars ONLY at the 8 outer edges"""
    spawn_lanes = [
        "j1_top", "j1_left",
        "j2_top", "j2_right",
        "j3_bottom", "j3_left",
        "j4_bottom", "j4_right"
    ]
    
    for lane_name in spawn_lanes:
        config = LANES[lane_name]
        if random.random() < config["density"] * 0.7:  # Reduce spawn rate
            turn_type = _choose_turn_direction()
            spawn_index = _get_spawn_index(lane_name, turn_type)
            spawn_data = config["spawn"][spawn_index]
            spawn_tag, spawn_x, spawn_y = spawn_data
            
            if can_spawn((spawn_x, spawn_y), lane_name):
                cars.append({
                    "x": float(spawn_x),
                    "y": float(spawn_y),
                    "lane": lane_name,
                    "spawn_lane": spawn_tag.split('_')[0],
                    "turn": turn_type,
                    "turning": False,
                    "done_turning": False,
                    "path_index": 0,
                    "angle": 0,
                    "velocity": 0,
                    "junction": config["junction"],
                    "stopped_at_red": False  # Track if stopped at red
                })


# ============================================================================
# COLLISION DETECTION
# ============================================================================

def _has_collision_with_any_car(car):
    """Check if car is within collision radius of ANY other car"""
    for other in cars:
        if other is car:
            continue
        dist = distance(car, other)
        if dist < MIN_COLLISION_DISTANCE:
            return True, dist
    return False, float('inf')


def _find_car_ahead_in_lane(car):
    """Find closest car ahead in same lane"""
    car_ahead = None
    min_dist = float('inf')
    
    for other in cars:
        if other is car or other["lane"] != car["lane"]:
            continue
        if other.get("turning") or other.get("done_turning"):
            continue
        
        direction = car["lane"].split('_')[-1]
        
        same_sublane = (abs(car["x"] - other["x"]) < 12 if direction in ["bottom", "top"] 
                       else abs(car["y"] - other["y"]) < 12)
        
        if not same_sublane:
            continue
        
        ahead, dist = False, 0
        if direction == "bottom":
            ahead = other["y"] < car["y"]
            dist = car["y"] - other["y"]
        elif direction == "top":
            ahead = other["y"] > car["y"]
            dist = other["y"] - car["y"]
        elif direction == "left":
            ahead = other["x"] > car["x"]
            dist = other["x"] - car["x"]
        elif direction == "right":
            ahead = other["x"] < car["x"]
            dist = car["x"] - other["x"]
        
        if ahead and dist < min_dist:
            min_dist = dist
            car_ahead = other
    
    return car_ahead, min_dist


# ============================================================================
# ABSOLUTE RED LIGHT ENFORCEMENT
# ============================================================================

def _get_distance_to_stop_line(car, config):
    """Get signed distance to stop line (positive = before, negative = after)"""
    direction = car["lane"].split('_')[-1]
    
    if direction == "bottom":
        return car["y"] - config["stop_y"]
    elif direction == "top":
        return config["stop_y"] - car["y"]
    elif direction == "left":
        return config["stop_x"] - car["x"]
    elif direction == "right":
        return car["x"] - config["stop_x"]
    return 0


def _can_cross_stop_line(car, signal_color, config):
    """
    ABSOLUTE CHECK: Can this car cross the stop line?
    Returns True ONLY if:
    - Signal is GREEN, OR
    - Car has already crossed the line
    """
    distance_to_line = _get_distance_to_stop_line(car, config)
    
    # Already past the line - allow movement
    if distance_to_line < -5:
        return True
    
    # At or before the line - check signal
    if signal_color == "green":
        return True
    
    # RED or YELLOW - CANNOT CROSS
    return False


def _should_start_turn(car, signal_color, config):
    """Check if car should start turning"""
    if car["turn"] == "straight" or car["turning"] or car["done_turning"]:
        return False
    
    if signal_color != "green":
        return False
    
    direction = car["lane"].split('_')[-1]
    
    if direction == "bottom" and car["y"] <= config["stop_y"] - 50:
        return True
    elif direction == "top" and car["y"] >= config["stop_y"] + 50:
        return True
    elif direction == "left" and car["x"] >= config["stop_x"] + 50:
        return True
    elif direction == "right" and car["x"] <= config["stop_x"] - 50:
        return True
    return False


# ============================================================================
# CAR MOVEMENT
# ============================================================================

def _move_turning_car(car):
    """Move car along turn path"""
    direction = car["lane"].split('_')[-1]
    junction_id = car["junction"]
    path_key = f"{junction_id}_{direction}_{car['turn']}"
    path = TURN_PATHS.get(path_key, [])
    
    if car["path_index"] < len(path):
        target = path[car["path_index"]]
        dx = target[0] - car["x"]
        dy = target[1] - car["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < car_speed * 0.7:
            car["path_index"] += 1
            if car["path_index"] >= len(path):
                car["done_turning"] = True
                car["turning"] = False
        else:
            move_speed = min(car_speed * 0.7, dist)
            car["x"] += (dx / dist) * move_speed
            car["y"] += (dy / dist) * move_speed
        
        car["angle"] = math.degrees(math.atan2(dy, dx)) + 90


def _move_post_turn_car(car):
    """Move car after completing turn"""
    direction = car["lane"].split('_')[-1]
    
    if direction == "bottom":
        car["x"] += car_speed * 0.7 if car["turn"] == "right" else -car_speed * 0.7
    elif direction == "top":
        car["x"] += car_speed * 0.7 if car["turn"] == "left" else -car_speed * 0.7
    elif direction == "left":
        car["y"] += car_speed * 0.7 if car["turn"] == "right" else -car_speed * 0.7
    elif direction == "right":
        car["y"] += car_speed * 0.7 if car["turn"] == "left" else -car_speed * 0.7
    
    if car["x"] < -70 or car["x"] > 1510 or car["y"] < -70 or car["y"] > 1510:
        if car in cars:
            cars.remove(car)
            driver_logic_4junctions.cars_passed += 1


def _calculate_velocity(car, can_cross, distance_to_line, car_ahead, dist_ahead, has_collision, config):
    """
    Velocity calculation with PHYSICAL BARRIER at red lights
    """
    max_speed = car_speed * 0.7
    
    # PRIORITY 1: COLLISION
    if has_collision:
        car["velocity"] = 0
        return
    
    # PRIORITY 2: RED LIGHT - ABSOLUTE BARRIER
    if not can_cross and distance_to_line > -5:
        # Approaching red light
        if distance_to_line < 2:
            # AT THE LINE - COMPLETE STOP
            car["velocity"] = 0
            car["stopped_at_red"] = True
        elif distance_to_line < 10:
            # Very close - emergency brake
            car["velocity"] = max(0, car["velocity"] - DECELERATION * 3)
        elif distance_to_line < 25:
            # Close - hard brake
            target = max_speed * 0.2
            if car["velocity"] > target:
                car["velocity"] = max(0, car["velocity"] - DECELERATION * 2)
        elif distance_to_line < 50:
            # Approaching - brake
            target = max_speed * (distance_to_line / 50) * 0.5
            if car["velocity"] > target:
                car["velocity"] = max(0, car["velocity"] - DECELERATION * 1.5)
        return
    
    # Green light or past the line - reset flag
    car["stopped_at_red"] = False
    
    # PRIORITY 3: CAR AHEAD
    if car_ahead and dist_ahead < CAR_SPACING * 1.5:
        if dist_ahead < MIN_COLLISION_DISTANCE * 1.2:
            car["velocity"] = max(0, car["velocity"] - DECELERATION * 2)
        elif dist_ahead < CAR_SPACING:
            target = max_speed * (dist_ahead / CAR_SPACING) * 0.6
            if car["velocity"] > target:
                car["velocity"] = max(0, car["velocity"] - DECELERATION)
            else:
                car["velocity"] = min(target, car["velocity"] + ACCELERATION * 0.5)
        else:
            if car["velocity"] < max_speed:
                car["velocity"] = min(car["velocity"] + ACCELERATION, max_speed)
        return
    
    # PRIORITY 4: NORMAL DRIVING
    if car["velocity"] < max_speed:
        car["velocity"] = min(car["velocity"] + ACCELERATION, max_speed)
    
    car["velocity"] = max(0, car["velocity"])


# ============================================================================
# MAIN LOOP
# ============================================================================

def update_car(all_signals):
    """Main update function - ENFORCES RED LIGHTS"""
    _spawn_new_cars()
    
    for car in cars[:]:
        if "velocity" not in car:
            car["velocity"] = 0
        if "stopped_at_red" not in car:
            car["stopped_at_red"] = False
        
        signal_color = get_signal_for_lane(car["lane"], all_signals)
        config = LANES[car["lane"]]
        
        # Handle turning
        if _should_start_turn(car, signal_color, config):
            car["turning"] = True
            car["path_index"] = 0
        
        if car["turning"]:
            _move_turning_car(car)
            continue
        
        if car["done_turning"]:
            _move_post_turn_car(car)
            continue
        
        # === NORMAL DRIVING ===
        
        has_collision, _ = _has_collision_with_any_car(car)
        car_ahead, dist_ahead = _find_car_ahead_in_lane(car)
        distance_to_line = _get_distance_to_stop_line(car, config)
        can_cross = _can_cross_stop_line(car, signal_color, config)
        
        # Calculate velocity
        _calculate_velocity(car, can_cross, distance_to_line, car_ahead, dist_ahead, has_collision, config)
        
        # === MOVEMENT WITH RED LIGHT BARRIER ===
        # If cannot cross and at line, DO NOT MOVE
        if not can_cross and distance_to_line >= 0 and distance_to_line < 3:
            car["velocity"] = 0  # Force stop
        
        # Apply movement
        new_x = car["x"] + config["move"][0] * car["velocity"]
        new_y = car["y"] + config["move"][1] * car["velocity"]
        
        # Double-check: Don't let car cross stop line on red
        if not can_cross:
            direction = car["lane"].split('_')[-1]
            
            # Calculate if new position would cross the line
            would_cross = False
            if direction == "bottom" and new_y < config["stop_y"] and car["y"] >= config["stop_y"]:
                would_cross = True
            elif direction == "top" and new_y > config["stop_y"] and car["y"] <= config["stop_y"]:
                would_cross = True
            elif direction == "left" and new_x > config["stop_x"] and car["x"] <= config["stop_x"]:
                would_cross = True
            elif direction == "right" and new_x < config["stop_x"] and car["x"] >= config["stop_x"]:
                would_cross = True
            
            # BLOCK crossing on red
            if would_cross:
                # Snap to stop line
                if direction == "bottom":
                    car["y"] = config["stop_y"]
                elif direction == "top":
                    car["y"] = config["stop_y"]
                elif direction == "left":
                    car["x"] = config["stop_x"]
                elif direction == "right":
                    car["x"] = config["stop_x"]
                car["velocity"] = 0
            else:
                # Safe to move
                car["x"] = new_x
                car["y"] = new_y
        else:
            # Green or past line - normal movement
            car["x"] = new_x
            car["y"] = new_y
        
        # Despawn off screen
        if car["x"] < -70 or car["x"] > 1510 or car["y"] < -70 or car["y"] > 1510:
            if car in cars:
                cars.remove(car)
                driver_logic_4junctions.cars_passed += 1