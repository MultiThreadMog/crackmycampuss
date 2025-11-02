"""
COMPLETE FIXED signal_control_4junctions.py - REPLACE ENTIRE FILE
FIXES: Independent signals, intersection clearing, no green until clear
"""

import time

YELLOW = (255, 215, 0)
RED = (220, 50, 50)
GREEN = (100, 220, 100)

signal_colors = {
    "red": RED,
    "yellow": YELLOW,
    "green": GREEN
}

# Timing constants
MIN_GREEN = 3
MAX_GREEN = 15
TIME_PER_VEHICLE = 1.2
YELLOW_TIME = 2
WAIT_AFTER_CLEAR = 0.5

# Initialize 4 independent junctions
JUNCTIONS = ["j1", "j2", "j3", "j4"]

# Each junction has its own signals
all_signals = {
    "j1": {"top": "red", "bottom": "red", "left": "red", "right": "red"},
    "j2": {"top": "red", "bottom": "red", "left": "red", "right": "red"},
    "j3": {"top": "red", "bottom": "red", "left": "red", "right": "red"},
    "j4": {"top": "red", "bottom": "red", "left": "red", "right": "red"}
}

# Vehicle counts per junction
all_vehicle_counts = {
    "j1": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j2": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j3": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j4": {"top": 0, "bottom": 0, "left": 0, "right": 0}
}

# Junction state tracking
junction_states = {
    "j1": {"last_switch": time.time(), "current_green": None, "phase": "green"},
    "j2": {"last_switch": time.time(), "current_green": None, "phase": "green"},
    "j3": {"last_switch": time.time(), "current_green": None, "phase": "green"},
    "j4": {"last_switch": time.time(), "current_green": None, "phase": "green"}
}

# Green counts for statistics
green_counts = {
    "j1": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j2": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j3": {"top": 0, "bottom": 0, "left": 0, "right": 0},
    "j4": {"top": 0, "bottom": 0, "left": 0, "right": 0}
}

# Junction boundaries for position checking
JUNCTION_BOUNDARIES = {
    "j1": {"x_min": 0, "x_max": 720, "y_min": 0, "y_max": 720},
    "j2": {"x_min": 720, "x_max": 1440, "y_min": 0, "y_max": 720},
    "j3": {"x_min": 0, "x_max": 720, "y_min": 720, "y_max": 1440},
    "j4": {"x_min": 720, "x_max": 1440, "y_min": 720, "y_max": 1440}
}

# Intersection areas (center box of each junction) - CRITICAL FOR CLEARING
INTERSECTION_AREAS = {
    "j1": {"x_min": 288, "x_max": 432, "y_min": 285, "y_max": 429},
    "j2": {"x_min": 720 + 288, "x_max": 720 + 432, "y_min": 285, "y_max": 429},
    "j3": {"x_min": 288, "x_max": 432, "y_min": 720 + 285, "y_max": 720 + 429},
    "j4": {"x_min": 720 + 288, "x_max": 720 + 432, "y_min": 720 + 285, "y_max": 720 + 429}
}


def get_vehicle_junction(x, y):
    """Determine which junction a vehicle is in based on position"""
    for junction_id, bounds in JUNCTION_BOUNDARIES.items():
        if (bounds["x_min"] <= x < bounds["x_max"] and 
            bounds["y_min"] <= y < bounds["y_max"]):
            return junction_id
    return None


def is_intersection_clear(junction_id, vehicles):
    """
    Check if intersection area is completely clear of vehicles.
    Returns True only if NO vehicles are in the intersection box.
    """
    intersection = INTERSECTION_AREAS[junction_id]
    
    for vehicle in vehicles:
        x = vehicle["x"]
        y = vehicle["y"]
        
        # Check if vehicle is inside intersection area
        if (intersection["x_min"] <= x <= intersection["x_max"] and
            intersection["y_min"] <= y <= intersection["y_max"]):
            return False  # Intersection occupied
    
    return True  # Intersection clear


def update_vehicle_counts(vehicles):
    """Count vehicles approaching each junction's intersection"""
    # Reset counts
    for junction_id in JUNCTIONS:
        all_vehicle_counts[junction_id] = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    
    for vehicle in vehicles:
        x = vehicle["x"]
        y = vehicle["y"]
        lane = vehicle["lane"]
        
        junction_id = get_vehicle_junction(x, y)
        if not junction_id:
            continue
        
        bounds = JUNCTION_BOUNDARIES[junction_id]
        junction_center_x = (bounds["x_min"] + bounds["x_max"]) / 2
        junction_center_y = (bounds["y_min"] + bounds["y_max"]) / 2
        
        # Extract direction from lane
        direction = lane.split('_')[-1] if '_' in lane else None
        if not direction:
            continue
        
        # Count vehicles approaching intersection (before stop line)
        threshold = 50
        if direction == "top" and y > junction_center_y + threshold:
            all_vehicle_counts[junction_id]["top"] += 1
        elif direction == "bottom" and y < junction_center_y - threshold:
            all_vehicle_counts[junction_id]["bottom"] += 1
        elif direction == "left" and x < junction_center_x - threshold:
            all_vehicle_counts[junction_id]["left"] += 1
        elif direction == "right" and x > junction_center_x + threshold:
            all_vehicle_counts[junction_id]["right"] += 1


def compute_green_time(junction_id):
    """Calculate green time based on waiting vehicles"""
    state = junction_states[junction_id]
    if state["current_green"] is None:
        return MIN_GREEN
    
    count = all_vehicle_counts[junction_id].get(state["current_green"], 0)
    green_time = MIN_GREEN + count * TIME_PER_VEHICLE
    return min(green_time, MAX_GREEN)


def get_next_green(junction_id):
    """Pick lane with most waiting cars for this junction"""
    current = junction_states[junction_id]["current_green"]
    counts = all_vehicle_counts[junction_id]
    
    # Get sorted lanes by vehicle count
    sorted_lanes = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    # Pick lane with most vehicles (excluding current green)
    for lane, count in sorted_lanes:
        if lane != current and count > 0:
            return lane
    
    # If no waiting vehicles, cycle through lanes
    lanes = ["bottom", "right", "top", "left"]
    if current in lanes:
        idx = (lanes.index(current) + 1) % 4
        return lanes[idx]
    return "bottom"


def update_signals(vehicles):
    """
    Update signals for all 4 junctions independently.
    CRITICAL: No green light until intersection is clear!
    """
    now = time.time()
    
    for junction_id in JUNCTIONS:
        state = junction_states[junction_id]
        signals = all_signals[junction_id]
        elapsed = now - state["last_switch"]
        
        # Check if intersection is clear
        intersection_clear = is_intersection_clear(junction_id, vehicles)
        
        if state["phase"] == "green":
            # Initialize first green
            if state["current_green"] is None:
                if intersection_clear:  # Only start if clear
                    state["current_green"] = "bottom"
                    signals[state["current_green"]] = "green"
                    green_counts[junction_id][state["current_green"]] += 1
                    state["last_switch"] = now
                continue
            
            green_time = compute_green_time(junction_id)
            current_count = all_vehicle_counts[junction_id][state["current_green"]]
            
            # Switch to yellow if max time or no cars waiting after min time
            if elapsed > green_time or (elapsed > MIN_GREEN and current_count == 0):
                signals[state["current_green"]] = "yellow"
                state["phase"] = "yellow"
                state["last_switch"] = now
        
        elif state["phase"] == "yellow":
            if elapsed > YELLOW_TIME:
                signals[state["current_green"]] = "red"
                state["phase"] = "wait_clear"  # New phase: wait for intersection to clear
                state["last_switch"] = now
        
        elif state["phase"] == "wait_clear":
            # Wait for intersection to clear before proceeding
            if intersection_clear:
                state["phase"] = "wait"
                state["last_switch"] = now
        
        elif state["phase"] == "wait":
            if elapsed > WAIT_AFTER_CLEAR:
                # Only turn next light green if intersection is CLEAR
                if intersection_clear:
                    next_green = get_next_green(junction_id)
                    state["current_green"] = next_green
                    signals[next_green] = "green"
                    green_counts[junction_id][next_green] += 1
                    state["phase"] = "green"
                    state["last_switch"] = now
                # else: keep waiting until clear


def get_signal_state(junction_id, direction):
    """Get the signal state for a specific direction at a junction"""
    return all_signals[junction_id][direction]


def get_green_counts():
    """Get green counts for all junctions"""
    return green_counts