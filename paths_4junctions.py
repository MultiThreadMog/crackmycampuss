'''
    TURN PATHS FOR 4 JUNCTIONS
    Each junction has its own set of turn paths with scaled and offset coordinates
'''

# Scale factor for smaller junctions
SCALE = 0.6667

# Original single junction turn paths
SINGLE_JUNCTION_PATHS = {
    "bottom_left": [(454, 630), (435, 617), (405, 613), (371, 612), (340, 612)],
    "bottom_right": [(515, 620), (525, 584), (525, 584), (547, 543), (577, 525), (621, 506), (621, 506), (657, 499), (657, 499), (714, 498), (714, 498)],
    "top_left": [(623, 440), (623, 440), (626, 455), (626, 455), (637, 465), (654, 473), (654, 473), (681, 474), (712, 477)],
    "top_right": [(566, 453), (566, 453), (564, 478), (554, 500), (540, 527), (520, 543), (478, 559), (447, 570), (447, 570), (412, 571), (383, 573), (360, 572)],
    "left_left": [(447, 454), (464, 448), (470, 427), (474, 397), (474, 380)],
    "left_right": [(452, 506), (486, 520), (486, 520), (523, 549), (547, 583), (562, 620), (575, 655), (575, 655), (575, 688)],
    "right_left": [(653, 624), (636, 633), (624, 641), (615, 657), (609, 675), (609, 685), (607, 698), (607, 713)],
    "right_right": [(613, 565), (551, 548), (519, 509), (500, 472), (494, 422), (494, 422), (493, 364)]
}

def scale_path(path, offset_x, offset_y):
    """Scale and offset a turn path"""
    return [(int(x * SCALE) + offset_x, int(y * SCALE) + offset_y) for x, y in path]

def create_junction_paths(junction_id, offset_x, offset_y):
    """Create turn paths for a specific junction"""
    junction_paths = {}
    for path_name, path in SINGLE_JUNCTION_PATHS.items():
        new_key = f"{junction_id}_{path_name}"
        junction_paths[new_key] = scale_path(path, offset_x, offset_y)
    return junction_paths

# Junction offsets
JUNCTION_OFFSETS = {
    "j1": (0, 0),
    "j2": (720, 0),
    "j3": (0, 720),
    "j4": (720, 720)
}

# Create all turn paths for all 4 junctions
ALL_TURN_PATHS = {}
for junction_id, (offset_x, offset_y) in JUNCTION_OFFSETS.items():
    ALL_TURN_PATHS.update(create_junction_paths(junction_id, offset_x, offset_y))

# For backward compatibility
TURN_PATHS = ALL_TURN_PATHS