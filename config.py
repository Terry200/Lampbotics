import serial, time, numpy as np
import imutils
from collections import deque
import argparse
#cv2.namedWindow("video", cv2.WINDOW_AUTOSIZE) # | cv2.WINDOW_KEEPRATIO)
""" DEVELOPMENT"""
# Change To write out on serial
WRITE = False
# Change press d when Program is running
DEBUG = True
# -------------------------------------------------
"""Display Options"""
# Change press o when Program is running
OBJECT = False
# Change press b when Program is running
BOX = True
# Change press c when Program is running
CIRCLE = True
# Change press z when Program is running
ZOOM = False
# Change press f when Program is running
TEXT = True
# Change press t when Program is running
TIME = False
# -------------------------------------------------------------
""" Constants"""
Type = 0																					# OBJ type: 0 Face. 1 Ball (GREEN) 
# Servo position
xygo = (0,0) 
# Controls same position into buffer.
control = []
control.append(xygo)
control.append(xygo)
i = 0
#size of the video    width = 160 height = 120   -----------------------    				FPS = 45 --->>> 30 depending on faces
#Video Size 1024x768 min distance of harr  24*24 px 640*480
vid_width = 680
vid_height = 480
# Center point
cam_c = (vid_width/2, vid_height/2)
#Ref distance 80cm
KNOWN_D = 80.0
# initialize the known object width
KNOWN_W = 15.0
# Servo degree ints ------------------ 175 = 1 degree(4px) 350 = 0.5 degree(2px) 700 = 0.25 degree(1px)
CONVERT = 175
BUFFER = None
DISTANCE = 0
ser = None
radius = None
#--------------------------------
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=20,#64
	help="max buffer size")
args = vars(ap.parse_args())
# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
pts = deque(maxlen=args["buffer"])
#---------------------------------------------
"""Colour To MASK"""
red_low = (136, 87,111)
red_up =  (180, 255,255)
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
#------------------------------------------/
# BUFFER Structure:  OBJ, Num, dif pos, Distance
def buffer_struct(Type, i, xygo, DISTANCE):																						# F.Header
	buf ="T"+'{:01d}'.format(Type)+"F"+'{:01d}'.format(i)+"x"+'{:03d}'.format(xygo[0])+"y"+'{:03d}'.format(xygo[1])+"d"+ '{:03d}'.format(int(DISTANCE))+"\n"
	return buf
# Write to serial
def buffer_write(control,BUFFER,ser):                                               												# F.Header
	if control[0][0] != control[1][0] or control[0][1] != control[1][1]:															# Check previous BUFFER
		control[0] = control[1]																										# Update
		time.sleep(0.016)																											# Sleep for 16ms
		if WRITE:
			ser.write(str(BUFFER))																									# Write
	else:																															# IF CONTROL[1] = CONTROL[0] Sleep
		if DEBUG:
			print"Sleep"
		time.sleep(0)
	return control																													# Return control
