import time

YELLOW = (255, 215, 0)
RED = (220, 50, 50)
GREEN = (100, 220, 100)

signals = {
    "top": "red",
    "bottom": "red",
    "left": "red",
    "right": "red"
}

signal_colors = {
    "red": RED,
    "yellow": YELLOW,
    "green": GREEN
}

vehicle_counts = {
    "top": 0,
    "bottom": 0,
    "left": 0,
    "right": 0
}

# Timing
MIN_GREEN = 3
MAX_GREEN = 15
TIME_PER_VEHICLE = 1.2
YELLOW_TIME = 2

last_switch = time.time()
current_green = None
phase = "green"

def update_vehicle_counts(cars):
    """Count cars approaching intersection (before stop line)"""
    from lane_config import LANES
    counts = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    
    for car in cars:
        if car.get("turning") or car.get("done_turning"):
            continue
            
        lane = car["lane"]
        config = LANES[lane]
        
        # Count ALL cars that haven't passed the intersection yet
        if lane == "bottom":
            # Count cars approaching from bottom (y > stop_y)
            if car["y"] >= config["stop_y"]:
                counts[lane] += 1
        elif lane == "top":
            # Count cars approaching from top (y < stop_y)
            if car["y"] <= config["stop_y"]:
                counts[lane] += 1
        elif lane == "left":
            # Count cars approaching from left (x < stop_x)
            if car["x"] <= config["stop_x"]:
                counts[lane] += 1
        elif lane == "right":
            # Count cars approaching from right (x > stop_x)
            if car["x"] >= config["stop_x"]:
                counts[lane] += 1
    
    vehicle_counts.update(counts)

def compute_green_time():
    if current_green is None:
        return MIN_GREEN
    count = vehicle_counts.get(current_green, 0)
    green_time = MIN_GREEN + count * TIME_PER_VEHICLE
    return min(green_time, MAX_GREEN)

def get_next_green():
    """Pick lane with most waiting cars, with fairness consideration"""
    # Prioritize lanes that haven't been green recently
    sorted_lanes = sorted(vehicle_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Get the lane with most vehicles (excluding current)
    for lane, count in sorted_lanes:
        if lane != current_green and count > 0:
            return lane
    
    # If no waiting vehicles, cycle through all lanes
    lanes = ["bottom", "right", "top", "left"]
    if current_green in lanes:
        idx = (lanes.index(current_green) + 1) % 4
        return lanes[idx]
    return "bottom"

green_counts = {"top": 0, "bottom": 0, "left": 0, "right": 0}

WAIT_AFTER_CLEAR = 0.5  # Brief pause between signals

def update_signals():
    global last_switch, current_green, phase

    now = time.time()
    elapsed = now - last_switch

    if phase == "green":
        if current_green is None:
            current_green = "bottom"
            signals[current_green] = "green"
            green_counts[current_green] += 1
            last_switch = now
            return
        
        green_time = compute_green_time()

        # Switch to yellow if: max time reached OR (min time passed AND no cars waiting)
        if elapsed > green_time or (elapsed > MIN_GREEN and vehicle_counts[current_green] == 0):
            signals[current_green] = "yellow"
            phase = "yellow"
            last_switch = now

    elif phase == "yellow":
        if elapsed > YELLOW_TIME:
            signals[current_green] = "red"
            phase = "wait"
            last_switch = now

    elif phase == "wait":
        if elapsed > WAIT_AFTER_CLEAR:
            next_green = get_next_green()
            current_green = next_green
            signals[current_green] = "green"
            green_counts[current_green] += 1
            phase = "green"
            last_switch = now


def get_green_count():
    return green_counts