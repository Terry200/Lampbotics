# Lampbotics Visionsystem.

# Dependencies 
Python 2.7.9 OpenCV 3.2.0
cv2,serial,numpy, time, imutils
Harrcascade
# cam.py      
1. Face detection
This includes x, y, d & Flags for each face detected.
2. Object Tracking
Developing --------
Store in location and run from cmd line (C:\location>python cam.py)
No serial write yet for object

Set WRTIE to True for serial write.
# Change To True, for write out on serial
WRITE = False

All other commands available while running

# Change press d when Program is running
DEBUG = False
"""Display Options"""
# Change press o when Program is running
OBJECT = False
# Change press b when Program is running
BOX = False
# Change press c when Program is running
CIRCLE = False
# Change press z when Program is running
ZOOM = False
# Change press f when Program is running
TEXT = False
# Change press t when Program is running
TIME = False


# mbed_text.txt    Basic serial read
copy to online compiler.
Ensure servo mod:
https://developer.mbed.org/teams/RedBearLab/code/BLENano_SimpleControls/
#Quick ref for using git:
https://www.youtube.com/watch?v=Y9XZQO1n_7c