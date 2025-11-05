"""
Handles spawning ambulances and giving them priority at intersections
"""
import time
import random
from driver_logic import cars, car_speed
from lane_config import LANES
import signal_control

# Track active ambulance
active_ambulance = None
ambulance_spawn_time = None
PRIORITY_DELAY = 1.0  # Seconds to wait before turning lane green


def spawn_ambulance(lane_name):
    global active_ambulance, ambulance_spawn_time
    
    if lane_name not in LANES:
        print(f"Invalid lane: {lane_name}")
        return None
    
    config = LANES[lane_name]
    
    spawn_index = random.randint(0, len(config["spawn"]) - 1)
    spawn_data = config["spawn"][spawn_index]
    spawn_tag, spawn_x, spawn_y = spawn_data
    
    ambulance = {
        "x": float(spawn_x),
        "y": float(spawn_y),
        "lane": lane_name,
        "spawn_lane": spawn_tag.split('_')[0],
        "turn": "straight",
        "turning": False,
        "done_turning": False,
        "path_index": 0,
        "angle": 0,
        "velocity": car_speed * 1.5,  
        "is_ambulance": True  
    }
    
    cars.append(ambulance)
    active_ambulance = ambulance
    ambulance_spawn_time = time.time()
    
    return ambulance


def update_ambulance_priority():
    global active_ambulance, ambulance_spawn_time
    
    if active_ambulance is None or ambulance_spawn_time is None:
        return
    
    # Check if ambulance still exists
    if active_ambulance not in cars:
        active_ambulance = None
        ambulance_spawn_time = None
        return
    
    elapsed = time.time() - ambulance_spawn_time
    if elapsed < PRIORITY_DELAY:
        return
    
    ambulance_lane = active_ambulance["lane"]
    
    if signal_control.signals[ambulance_lane] != "green":
        if signal_control.current_green:
            signal_control.signals[signal_control.current_green] = "red"
        
        # Turn ambulance lane green
        signal_control.signals[ambulance_lane] = "green"
        signal_control.current_green = ambulance_lane
        signal_control.phase = "green"
        signal_control.last_switch = time.time()
        signal_control.green_counts[ambulance_lane] += 1
    
    # clear lane and return to normal
    ambulance_spawn_time = None


def is_ambulance(car):
    # check if an object is an ambulance
    return car.get("is_ambulance", False)


def get_active_ambulance():
    return active_ambulance


# from ambulance import spawn_ambulance
# spawn_ambulance("bottom")  # example