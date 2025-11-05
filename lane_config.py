''' 

    THIS FILE CONTAINS LANE INFORMATION 
    SPAWN POINTS;
    TURNING START POINT;
    VEHICLE LANE DENSITY

'''

LANES = {
    "bottom": {
        "spawn": [("bottom_right", 459, 1060), ("bottom_left", 512, 1060)],
        "stop_y": 685,
        "move": (0, -1),
        "density": 0.008 
    },
    "top": {
        "spawn": [("top_right", 568, 10), ("top_left", 621, 10)],
        "stop_y": 385,
        "move": (0, 1),
        "density": 0.006  
    },
    "left": {
        "spawn": [("left_right", 10, 505), ("left_left", 10, 462)],
        "stop_x": 385,
        "move": (1, 0),
        "density": 0.007
    },
    "right": {
        "spawn": [("right_right", 1070, 566), ("right_left", 1070, 619)],
        "stop_x": 695,
        "move": (-1, 0),
        "density": 0.006 
    }
}