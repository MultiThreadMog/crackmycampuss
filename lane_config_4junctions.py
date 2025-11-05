'''
    LANE CONFIGURATION FOR 4 JUNCTIONS
    Each junction has its own lane config with scaled coordinates
'''

# Scale factor for smaller junctions (720/1080 = 0.6667)
SCALE = 0.6667

def scale_coord(coord):
    """Scale a coordinate by the scale factor"""
    return int(coord * SCALE)

# Original single junction lane config (for reference)
'''SINGLE_JUNCTION_LANES = {
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
}'''

# Junction offsets
JUNCTION_OFFSETS = {
    "j1": (0, 0),
    "j2": (720, 0),
    "j3": (0, 720),
    "j4": (720, 720)
}

def create_junction_lanes(junction_id, offset_x, offset_y):
    """Create lane config for a specific junction with proper offsets and scaling"""
    return {
        f"{junction_id}_bottom": {
            "spawn": [
                (f"{junction_id}_bottom_right", offset_x + scale_coord(459), offset_y + 720 + 50),
                (f"{junction_id}_bottom_left", offset_x + scale_coord(512), offset_y + 720 + 50)
            ],
            "stop_y": offset_y + scale_coord(685),
            "move": (0, -1),
            "density": 0.008,
            "junction": junction_id
        },
        f"{junction_id}_top": {
            "spawn": [
                (f"{junction_id}_top_right", offset_x + scale_coord(568), offset_y - 50),
                (f"{junction_id}_top_left", offset_x + scale_coord(621), offset_y - 50)
            ],
            "stop_y": offset_y + scale_coord(385),
            "move": (0, 1),
            "density": 0.006,
            "junction": junction_id
        },
        f"{junction_id}_left": {
            "spawn": [
                (f"{junction_id}_left_right", offset_x - 50, offset_y + scale_coord(505)),
                (f"{junction_id}_left_left", offset_x - 50, offset_y + scale_coord(462))
            ],
            "stop_x": offset_x + scale_coord(385),
            "move": (1, 0),
            "density": 0.007,
            "junction": junction_id
        },
        f"{junction_id}_right": {
            "spawn": [
                (f"{junction_id}_right_right", offset_x + 720 + 50, offset_y + scale_coord(566)),
                (f"{junction_id}_right_left", offset_x + 720 + 50, offset_y + scale_coord(619))
            ],
            "stop_x": offset_x + scale_coord(695),
            "move": (-1, 0),
            "density": 0.006,
            "junction": junction_id
        }
    }

# Create all lanes for all 4 junctions
ALL_LANES = {}
for junction_id, (offset_x, offset_y) in JUNCTION_OFFSETS.items():
    ALL_LANES.update(create_junction_lanes(junction_id, offset_x, offset_y))

# For backward compatibility, keep LANES as the complete set
LANES = ALL_LANES