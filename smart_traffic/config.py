"""
Configuration file for traffic simulation
Contains all timing and display settings
"""

import os

# ========================
# Paths
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_DIR = os.path.join(BASE_DIR, 'photo')

# ========================
# Signal Timing (seconds)
# ========================
GREEN_LIGHT_DURATION = 10
YELLOW_LIGHT_DURATION = 3

# ========================
# Traffic Generation
# ========================
SPAWN_INTERVAL_MIN = 2.0        # Min seconds between spawns per side
SPAWN_INTERVAL_MAX = 4.0        # Max seconds between spawns per side
MAX_VEHICLES_PER_SIDE = 8
GREEN_START_DELAY = 1.0         # Seconds to wait after green before vehicles move

# ========================
# Vehicle Properties
# ========================
VEHICLE_SPEED = 2               # Pixels per frame (smooth movement)

# Display sizes (width x length) for scaling images
VEHICLE_DISPLAY_SIZES = {
    'CAR': (35, 55),
    'TRUCK': (38, 65),
    'AMBULANCE': (35, 58)
}

# Vehicle type spawn probabilities (must sum to 1.0)
VEHICLE_PROBABILITIES = {
    'CAR': 0.65,
    'TRUCK': 0.28,
    'AMBULANCE': 0.07
}

# Vehicle image files (inside photo/ folder)
VEHICLE_IMAGES = {
    'CAR': ['car.jpg', 'car1.png', 'car2.jpg', 'car3.jpg', 'car4.png'],
    'TRUCK': ['truck.png', 'truck1.jpg', 'truck3.jpg', 'truck4.png', 'truck5.jpg'],
    'AMBULANCE': ['ambulance.jpg']
}

# Image base direction: "UP" if images face north, "RIGHT" if they face east
IMAGE_FACES = "UP"

# Per-image facing direction (the direction the raw image points).
# After loading, each image is pre-rotated so it faces UP.
# Options: "UP", "DOWN", "LEFT", "RIGHT"
IMAGE_DIRECTION = {
    'car.jpg':       'RIGHT',    # wide side-view, faces right
    'car1.png':      'LEFT',     # square, faces left
    'car2.jpg':      'RIGHT',    # wide side-view, faces right
    'car3.jpg':      'UP',       # square, faces up
    'car4.png':      'RIGHT',    # wide side-view, faces right
    'truck.png':     'UP',       # tall, faces up
    'truck1.jpg':    'LEFT',     # wide side-view, faces left
    'truck3.jpg':    'UP',       # tall, faces up
    'truck4.png':    'RIGHT',    # wide side-view, faces right
    'truck5.jpg':    'LEFT',     # wide side-view, faces left
    'ambulance.jpg': 'UP',       # square, faces up
}

# ========================
# License Plate
# ========================
LICENSE_PLATE_STATES = ['UP', 'DL', 'MH', 'KA', 'TN', 'HR', 'RJ', 'GJ', 'MP', 'WB']
LICENSE_PLATE_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# ========================
# Display Settings
# ========================
FULLSCREEN = True
FPS = 60

# ========================
# Colors (RGB)
# ========================
COLOR_BACKGROUND = (34, 40, 49)
COLOR_ROAD = (68, 68, 68)
COLOR_ROAD_LINE = (255, 255, 255)
COLOR_ROAD_MARKING = (255, 255, 100)
COLOR_SIGNAL_RED = (231, 76, 60)
COLOR_SIGNAL_YELLOW = (241, 196, 15)
COLOR_SIGNAL_GREEN = (46, 204, 113)
COLOR_TEXT = (255, 255, 255)

# ========================
# Intersection Layout
# ========================
ROAD_WIDTH = 220
LANE_OFFSET = ROAD_WIDTH // 4       # Center of each lane from road center (~55px)
SIGNAL_SIZE = 25
STOP_LINE_OFFSET = 130              # Distance from center to stop line
SPAWN_DISTANCE = 550                # Distance from center to spawn point (near screen edge)

# ========================
# Vehicle Spacing
# ========================
MIN_FOLLOWING_DISTANCE = 70         # Minimum gap between vehicles in queue
