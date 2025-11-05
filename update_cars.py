from driver_logic import cars, signals, random, car_speed, can_spawn, math, STOP_MARGIN
import driver_logic
from paths import TURN_PATHS
from lane_config import LANES

CAR_SPACING = 60
MIN_SPACING = 40
ACCELERATION = 0.15
DECELERATION = 0.4
LOOK_AHEAD = 60  # Ray-cast scan distance

# ============================================================================
# SPAWNING
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
    if turn_type == "left":
        return 0 if lane_name == "bottom" else 1
    elif turn_type == "right":
        return 1 if lane_name == "bottom" else 0
    return random.randint(0, 1)


def _spawn_new_cars():
    """Try to spawn new cars at lane entrances"""
    for lane_name, config in LANES.items():
        if random.random() < config["density"]:
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
                    "velocity": 0,  # Start from 0 for smooth acceleration
                    "passed_signal": False  # Track if car passed signal
                })


# ============================================================================
# RAY-CAST COLLISION DETECTION (NEW SYSTEM)
# ============================================================================

def _get_obstacle_distance(car, signal_color, config):
    """
    Use ray-cast scanning from white dot position to detect obstacles ahead.
    Returns (distance, obstacle_type) or (None, None) if no obstacles.
    """
    direction = car["lane"]
    
    # Mark if car has passed signal
    if "passed_signal" not in car:
        car["passed_signal"] = False
    
    # Check if car passed the stop line
    if not car["passed_signal"]:
        if direction == "bottom" and car["y"] < config["stop_y"]:
            car["passed_signal"] = True
        elif direction == "top" and car["y"] > config["stop_y"]:
            car["passed_signal"] = True
        elif direction == "left" and car["x"] > config["stop_x"]:
            car["passed_signal"] = True
        elif direction == "right" and car["x"] < config["stop_x"]:
            car["passed_signal"] = True
    
    # Reset passed_signal once car is well past intersection
    if car["passed_signal"]:
        if direction == "bottom" and car["y"] < config["stop_y"] - 100:
            car["passed_signal"] = False
        elif direction == "top" and car["y"] > config["stop_y"] + 100:
            car["passed_signal"] = False
        elif direction == "left" and car["x"] > config["stop_x"] + 100:
            car["passed_signal"] = False
        elif direction == "right" and car["x"] < config["stop_x"] - 100:
            car["passed_signal"] = False
    
    # Calculate car center and white dot position
    car_center_x = car["x"] + 10  # Assuming 10px offset to center
    car_center_y = car["y"] + 10
    indicator_offset = 4
    
    # Get direction vector from white dot (unit vector)
    if car.get("turning") or car.get("angle", 0) != 0:
        # Use angle for turning cars
        angle_rad = math.radians(car.get("angle", 0) - 90)
        dx_unit = math.cos(angle_rad)
        dy_unit = math.sin(angle_rad)
    else:
        # Use direction for straight cars
        if direction == "bottom":
            dx_unit, dy_unit = 0, -1
        elif direction == "top":
            dx_unit, dy_unit = 0, 1
        elif direction == "left":
            dx_unit, dy_unit = 1, 0
        else:  # right
            dx_unit, dy_unit = -1, 0
    
    # White dot position (direction indicator)
    white_dot_x = car_center_x + indicator_offset * dx_unit
    white_dot_y = car_center_y + indicator_offset * dy_unit
    
    # Ray-cast scan ahead for obstacles
    scan_distance = LOOK_AHEAD
    obstacle_found = None
    min_distance = scan_distance
    
    # Scan each pixel ahead from white dot
    for dist in range(1, scan_distance + 1):
        scan_x = white_dot_x + dx_unit * dist
        scan_y = white_dot_y + dy_unit * dist
        
        # Check for other cars at this scan position
        for other in cars:
            if other is car:
                continue
            
            other_center_x = other["x"] + 10
            other_center_y = other["y"] + 10
            
            # Check if other car is within detection radius at scan point
            dist_to_other = math.sqrt((other_center_x - scan_x)**2 + (other_center_y - scan_y)**2)
            if dist_to_other < 12:  # Detection radius
                if dist < min_distance:
                    min_distance = dist
                    obstacle_found = 'car'
                break
        
        if obstacle_found:
            break
    
    # Only check signal if haven't passed it yet
    if not car["passed_signal"]:
        # Calculate distance to stop line
        if direction == "bottom":
            dist_to_signal = car["y"] - config["stop_y"]
        elif direction == "top":
            dist_to_signal = config["stop_y"] - car["y"]
        elif direction == "left":
            dist_to_signal = config["stop_x"] - car["x"]
        else:  # right
            dist_to_signal = car["x"] - config["stop_x"]
        
        # Only treat signal as obstacle if red/yellow and approaching
        if (signal_color in ["red", "yellow"] and 
            0 < dist_to_signal <= scan_distance):
            if dist_to_signal < min_distance:
                min_distance = dist_to_signal
                obstacle_found = 'signal'
    
    if obstacle_found:
        return min_distance, obstacle_found
    return None, None


def _calculate_velocity(car, obstacle_dist, obstacle_type):
    """
    Calculate velocity based on obstacle distance using smooth acceleration/deceleration.
    Different safe distances for signals vs cars.
    """
    max_speed = car_speed * 0.7
    
    # No obstacles - accelerate to max speed
    if obstacle_dist is None:
        if car["velocity"] < max_speed:
            car["velocity"] = min(car["velocity"] + ACCELERATION, max_speed)
        return
    
    # Different safe distances for signals vs cars
    safe_distance = 3 if obstacle_type == 'signal' else 12
    
    # Stop if very close
    if obstacle_dist <= safe_distance:
        car["velocity"] = 0
    # Slow down if approaching
    elif obstacle_dist < 20:
        target_speed = max_speed * (obstacle_dist - safe_distance) / 20
        car["velocity"] = max(0, min(car["velocity"] - DECELERATION, target_speed))
    # Moderate approach
    elif obstacle_dist < 40:
        target_speed = max_speed * 0.6
        if car["velocity"] > target_speed:
            car["velocity"] = max(target_speed, car["velocity"] - DECELERATION * 0.5)
        else:
            car["velocity"] = min(target_speed, car["velocity"] + ACCELERATION * 0.5)
    # Far away - gradual adjustment
    else:
        target_speed = max_speed * 0.8
        if car["velocity"] < target_speed:
            car["velocity"] = min(target_speed, car["velocity"] + ACCELERATION * 0.5)
    
    # Clamp velocity
    car["velocity"] = max(0, min(car["velocity"], max_speed))


# ============================================================================
# CAR MOVEMENT
# ============================================================================

def _should_start_turn(car, signal_color, config):
    """Check if car should start turning"""
    if car["turn"] == "straight" or car["turning"] or car["done_turning"]:
        return False
    if signal_color != "green":
        return False
    
    direction = car["lane"]
    
    # Start turn when past the stop line
    if direction == "bottom" and car["y"] <= config["stop_y"] - 30:
        return True
    elif direction == "top" and car["y"] >= config["stop_y"] + 30:
        return True
    elif direction == "left" and car["x"] >= config["stop_x"] + 30:
        return True
    elif direction == "right" and car["x"] <= config["stop_x"] - 30:
        return True
    return False


def _move_turning_car(car):
    """Move car along turn path"""
    path_key = f"{car['lane']}_{car['turn']}"
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
    if car["lane"] == "bottom":
        car["x"] += car_speed * 0.7 if car["turn"] == "right" else -car_speed * 0.7
    elif car["lane"] == "top":
        car["x"] += car_speed * 0.7 if car["turn"] == "left" else -car_speed * 0.7
    elif car["lane"] == "left":
        car["y"] += car_speed * 0.7 if car["turn"] == "right" else -car_speed * 0.7
    elif car["lane"] == "right":
        car["y"] += car_speed * 0.7 if car["turn"] == "left" else -car_speed * 0.7
    
    # Despawn off screen
    if car["x"] < -50 or car["x"] > 1130 or car["y"] < -50 or car["y"] > 1120:
        if car in cars:
            cars.remove(car)
            driver_logic.cars_passed += 1


# ============================================================================
# MAIN LOOP
# ============================================================================

def update_car():
    """Main update function called each frame"""
    _spawn_new_cars()
    
    for car in cars[:]:
        if "velocity" not in car:
            car["velocity"] = 0
        
        signal_color = signals.get(car["lane"], "red")
        config = LANES[car["lane"]]
        
        # Check if we should start turning
        if _should_start_turn(car, signal_color, config):
            car["turning"] = True
            car["path_index"] = 0
        
        # Handle turning cars
        if car["turning"]:
            _move_turning_car(car)
            continue
        
        # Handle post-turn cars
        if car["done_turning"]:
            _move_post_turn_car(car)
            continue
        
        # Handle normal straight-moving cars with NEW COLLISION SYSTEM
        obstacle_dist, obstacle_type = _get_obstacle_distance(car, signal_color, config)
        _calculate_velocity(car, obstacle_dist, obstacle_type)
        
        # Move car
        car["x"] += config["move"][0] * car["velocity"]
        car["y"] += config["move"][1] * car["velocity"]
        
        # Despawn when off screen
        if car["x"] < -50 or car["x"] > 1130 or car["y"] < -50 or car["y"] > 1120:
            if car in cars:
                cars.remove(car)
                driver_logic.cars_passed += 1