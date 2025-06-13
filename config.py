# config.py

# Serial communication settings
SERIAL_PORT = "COM8"  # or "/dev/ttyUSB0" for Linux/macOS
BAUD_RATE = 9600

# ==== Robot Leg Parameters ====

NUM_LEGS = 4
NUM_JOINTS = 3

JOINT_NAMES = ["knee", "Hip-Leg", "Hip-Body"]
JOINT_RANGES = [(30,180), (-150, 30), (-20,20)]
# Joint angles initial position
JOINT_ANGLES_INIT = [(JOINT_RANGES[i][1] + JOINT_RANGES[i][0]) / 2 for i in range(NUM_JOINTS)]

HIP_KNEE_LENGTH = 100  # Hip to knee
KNEE_FOOT_LENGTH = 156  # Knee to foot
