from driver_logic_4junctions import cars, car_speed, can_spawn, get_signal_for_lane
import driver_logic_4junctions
from paths_4junctions import TURN_PATHS
from lane_config_4junctions import LANES
import random
import math

MIN_COLLISION_DISTANCE = 18
ACCELERATION = 0.15
DECELERATION = 0.4
LOOK_AHEAD = 60

def _choose_turn_direction():
    p_left = random.uniform(0.1, 0.3)    
    p_right = random.uniform(0.1, 0.3)   
    turn_choice = random.random()
    if turn_choice < p_left:
        return "left"
    elif turn_choice < p_left + p_right:
        return "right"
    return "straight"

def _get_spawn_index(lane_name, turn_type):
    direction = lane_name.split('_')[-1]
    if turn_type == "left":
        return 0 if direction == "bottom" else 1
    elif turn_type == "right":
        return 1 if direction == "bottom" else 0
    return random.randint(0, 1)

def _spawn_new_cars():
    spawn_lanes = [
        "j1_top", "j1_left",
        "j2_top", "j2_right",
        "j3_bottom", "j3_left",
        "j4_bottom", "j4_right"
    ]
    
    for lane_name in spawn_lanes:
        config = LANES[lane_name]
        if random.random() < config["density"] * 0.7:
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
                    "junction": config["junction"]
                })

def _get_obstacle_distance(car, signal_color, config):
    direction = car["lane"].split('_')[-1]
    
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
    
    # Calculate white dot position (car center + indicator offset)
    car_center_x = car["x"] + 10
    car_center_y = car["y"] + 10
    indicator_offset = 4
    
    # Get direction vector from white dot
    if car.get("turning") or car.get("angle", 0) != 0:
        angle_rad = math.radians(car.get("angle", 0) - 90)
        dx_unit = math.cos(angle_rad)
        dy_unit = math.sin(angle_rad)
    else:
        if direction in ["bottom", "down"]:
            dx_unit, dy_unit = 0, -1
        elif direction in ["top", "up"]:
            dx_unit, dy_unit = 0, 1
        elif direction == "left":
            dx_unit, dy_unit = 1, 0
        else:  # right
            dx_unit, dy_unit = -1, 0
    
    white_dot_x = car_center_x + indicator_offset * dx_unit
    white_dot_y = car_center_y + indicator_offset * dy_unit
    
    # Scan ahead for obstacles
    scan_distance = 60
    obstacle_found = None
    min_distance = scan_distance
    
    # Check for cars ahead by scanning from white dot
    for dist in range(1, scan_distance + 1):
        scan_x = white_dot_x + dx_unit * dist
        scan_y = white_dot_y + dy_unit * dist
        
        for other in cars:
            if other is car:
                continue
            
            other_center_x = other["x"] + 10
            other_center_y = other["y"] + 10
            
            # Check if other car is at this scan position
            dist_to_other = math.sqrt((other_center_x - scan_x)**2 + (other_center_y - scan_y)**2)
            if dist_to_other < 12:
                if dist < min_distance:
                    min_distance = dist
                    obstacle_found = 'car'
                break
        
        if obstacle_found:
            break
    
    # Only check signal if haven't passed it yet
    if not car["passed_signal"]:
        # Calculate distance to stop line based on signal
        if direction == "bottom":
            dist_to_signal = car["y"] - config["stop_y"]
        elif direction == "top":
            dist_to_signal = config["stop_y"] - car["y"]
        elif direction == "left":
            dist_to_signal = config["stop_x"] - car["x"]
        else:
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
    
    car["velocity"] = max(0, min(car["velocity"], max_speed))

def _should_start_turn(car, signal_color, config):
    if car["turn"] == "straight" or car["turning"] or car["done_turning"]:
        return False
    if signal_color != "green":
        return False
    
    direction = car["lane"].split('_')[-1]
    
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

def update_car(all_signals):
    _spawn_new_cars()
    
    for car in cars[:]:
        if "velocity" not in car:
            car["velocity"] = 0
        
        signal_color = get_signal_for_lane(car["lane"], all_signals)
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
        
        # Handle normal straight-moving cars
        obstacle_dist, obstacle_type = _get_obstacle_distance(car, signal_color, config)
        _calculate_velocity(car, obstacle_dist, obstacle_type)
        
        # Move car
        car["x"] += config["move"][0] * car["velocity"]
        car["y"] += config["move"][1] * car["velocity"]
        
        # Remove cars that have left the screen
        if car["x"] < -70 or car["x"] > 1510 or car["y"] < -70 or car["y"] > 1510:
            if car in cars:
                cars.remove(car)
                driver_logic_4junctions.cars_passed += 1