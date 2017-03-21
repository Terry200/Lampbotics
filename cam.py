import cv2
from config import *
import serial, time, numpy as np
# Set up Buffer
BUFFER = buffer_struct(Type, i,xygo,DISTANCE)
if DEBUG:
	print("BUFFER",BUFFER)
if WRITE:				# Set up serial
	ser=serial.Serial(port='COM3',baudrate=9600,timeout=0)
	ser.write('r')
	ser.write(str(BUFFER))
if DEBUG:
	print control
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FPS, 60.0)
#SET UP VIDEO
if vid_width is None:
	vid_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
else:
	video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, vid_width) 
if vid_height is None:
	vid_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
else:
	video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, vid_height)
#LOOP
while True:
	# Dummy proof serial OFF!!!
	if not WRITE:
		print "Serial write is OFF"
	# Start a timer
	if TIME:
		start = time.time()
	ret, frame = video_capture.read()
	if ret == True:            																# If previous frame flip image
		frame = cv2.flip(frame,1)
		frame2 = frame.copy()																# Copy image
	gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)									# Gray image
	# resize the frame, blur it, and convert it to the HSV
	# color space
	if OBJECT:
		frame2 = imutils.resize(frame2, width=640)
		# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)
		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)[-2]
		centero = None
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			centero = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				cv2.circle(frame2, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame2, centero, 5, (0, 0, 255), -1)
		pts.appendleft(centero)														# update the points queue
		for i in xrange(1, len(pts)):												# loop over the set of tracked points
			# if either of the tracked points are None, ignore them
			if pts[i - 1] is None or pts[i] is None:
				continue
			thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)			# otherwise, compute the thickness of the line and
			cv2.line(frame2, pts[i - 1], pts[i], (0, 0, 255), thickness)			# draw the connecting lines
		if DEBUG:
			print"radius", radius													# DEBUG PRINTS
			print"center", centero
			print "Line len", len(pts)
	#Find faces
	if not OBJECT:
		faces = face_cascade.detectMultiScale(gray_image,
											  scaleFactor=1.2,
											  minNeighbors=5,
											  minSize=(30, 30),
											  flags=cv2.CASCADE_SCALE_IMAGE
											  )
		if( len(faces) ):																                                         # IF Face found else skip
			i = 0
			for face in faces:					                                                                                 # For each face
				i += 1							                                                                                 # ID
				(x, y, w, h) = face																		                         # Get Deminsions
				if BOX:
					cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)					
				center_point = ((x+(x+w))/2, (y+(y+h))/2)												                         # C.pt  of Face
				if CIRCLE:
					cv2.circle(frame, center_point, 5, color=(0, 0, 255), thickness=1, lineType=8, shift=0)                      # Draw Circle @ Face C.pt
				if BOX:
					cv2.rectangle(frame, center_point, center_point, (255, 0, 0), 2)
				if CIRCLE:
					cv2.circle(frame, cam_c, 5, color=(0, 255, 255), thickness=1, lineType=8, shift=0)						     	# Draw Circle @ Video C.pt
				if TEXT:
					cv2.putText(frame,"FACE "+str(i), (x , y - 5), cv2.FONT_HERSHEY_SIMPLEX, .3, (255,0,0), 2)						# Display ID of Face
				xygo = ( ( (cam_c[0]-center_point[0])/(vid_width/CONVERT) ),( (cam_c[1]-center_point[1])/(vid_height/CONVERT) ) )	# Convert pixels to Degree
				focal = (152*KNOWN_D)/KNOWN_W																						#Define focal
				DISTANCE = (KNOWN_W*focal)/((x+w)-x)																				# Slove for Distance
				BUFFER = buffer_struct(Type, i,xygo,DISTANCE)																		# "T"+'{:01d}'.format(Type)+
				if xygo is not None:					                                                            				# Controls Buffer
					control[1] = xygo																								# Set Control Check
					control = buffer_write(control, BUFFER)																			# Buffer write, Updates control
				if DEBUG:
					# Comment out what you dont want to see
					#print(i)												# Face Number
					#print("Face Centre", center_point)    					# Face C.Point
					#print("Cam Centre", cam_c)								# Cam C.Point
					#print("x y", xygo)										# Servo Pos
					#print													# Serial Data
					print('Serial String',BUFFER)							# Serial Data
					print ('Length',len(BUFFER))							# Length of serial
					#print													# Length of serial
					#print('distance', int(DISTANCE))						# Distance to object
					#print control											# Control to make buffer sleep (Con for odd occ)
	"""Display avails
	1 Frame
	2 Frame2
	3 gray_image
	4 hsv
	5 mask
	Show 2 together (Must be same demenions)
	6 display = np.hstack([frame,frame2])
	"""
	if OBJECT:
		cv2.imshow('Video', frame2)										# Show video stream
	else:
		cv2.imshow('Video', frame)
	#THIS IS NOT WORKING CORRECTLY 
	if TIME:															# Toggle Time
		end = time.time()
		# Time elapsed
		seconds = end - start
		if TIME and DEBUG: 
			print "Time taken : {0} ms".format(seconds*1000)
		fps = video_capture.get(cv2.CAP_PROP_FPS)
		print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
	if cv2.waitKey(1) == 27:											# Esc ENDS program 
		break
	if cv2.waitKey(1) == ord("f"):										# Remove\ Add text
		TEXT = not TEXT
	if cv2.waitKey(1) == ord("b"):										# Remove\ Add text
		BOX = not BOX
	if cv2.waitKey(1) == ord("c"):										# Remove Circle Debug
		CIRCLE = not CIRCLE
	if cv2.waitKey(1) == ord("z"):										# Zoom!!!!!!! NEEDS WORK
		ZOOM = not ZOOM
	if cv2.waitKey(1) == ord("t"):										# TIME DISPLAY
		TIME = not TIME
	if cv2.waitKey(1) == ord("d"):										# DEBUG DISPLAY
		DEBUG = not DEBUG
	if cv2.waitKey(1) == ord("o"):										# DEBUG DISPLAY
		OBJECT = not OBJECT

video_capture.release()
out.release()
cv2.destroyAllWindows()