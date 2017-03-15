import cv2
import serial, time
""" Constants"""
#cv2.namedWindow("video", cv2.WINDOW_AUTOSIZE) # | cv2.WINDOW_KEEPRATIO)
# Change to TRUE to Serial write
WRITE = False
# Change to True for print outs
DEBUG = True 
Type = 0
# Servo position
xygo = (0,0) 
#size of the video    width = 160 height = 120   -----------------------    FPS = 45 --->>> 30 depending on faces
#Video Size 1024x768 min distance of harr  24*24 px 640*480
vid_width = 1024
vid_height =768
# Center point
cam_c = (vid_width/2, vid_height/2)
#Ref distance
KNOWN_D = 80.0
# initialize the known object width
KNOWN_W = 15.0
# Servo degree ints ------------------ 175 = 1 degree(4px) 350 = 0.5 degree(2px) 700 = 0.25 degree(1px)
CONVERT = 175
# Controls same position into buffer.
control = []
control.append(xygo)
control.append(xygo)
print control
DISTANCE = 0
BUFFER ="T"+str(Type)+"F "+'{:01d}'.format(1)+"x"+'{:04d}'.format(xygo[0])+"y"+'{:04d}'.format(xygo[1])+"d"+ '{:03d}'.format(int(DISTANCE))
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 60.0, (640,480))

# Set up Buffer
if DEBUG:
	print("BUFFER",BUFFER)
if WRITE:				# Set up serial
	ser=serial.Serial(port='COM5',baudrate=9600,timeout=0)
	ser.write('r')
	ser.write(str(BUFFER))
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
    if not WRITE:
        print "Serial write is off"
	ret, frame = video_capture.read()
	if ret == True:            # If previous frame flip image
		print 'HERE'
		frame = cv2.flip(frame,1)
       #write the flipped frame
		#out.write(frame)
	gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# Start a timer
	if DEBUG:
	   start = time.time()	  
	#Find faces
	faces = face_cascade.detectMultiScale(gray_image,
										  scaleFactor=1.2,
										  minNeighbors=5,
										  minSize=(30, 30),
										  flags=cv2.CASCADE_SCALE_IMAGE
										  )
	if( len(faces) ):																                                                  # IF Face found else skip
		i = 0
		for face in faces:					                                                                                 # For each face
			i +=1							                                                                                     # ID
			(x, y, w, h) = face																		                                 # Get Deminsions
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)					
			center_point = ((x+(x+w))/2, (y+(y+h))/2)												                                 # C.pt  of Face
			cv2.circle(frame, center_point, 5, color=(0, 0, 255), thickness=1, lineType=8, shift=0)                         # Draw Circle @ Face C.pt
			cv2.rectangle(frame, center_point, center_point, (255, 0, 0), 2)
			cv2.circle(frame, cam_c, 5, color=(0, 255, 255), thickness=1, lineType=8, shift=0)						             # Draw Circle @ Video C.pt
			xygo = (((cam_c[0]-center_point[0])/(vid_width/CONVERT)),((cam_c[1]-center_point[1])/(vid_height/CONVERT)) )		# Convert pixels to Degree
			focal = (152*KNOWN_D)/KNOWN_W																			#Define focal
			DISTANCE = (KNOWN_W*focal)/((x+w)-x)																	# Slove for Distance
			BUFFER = "T"+str(Type)+"F"+'{:02d}'.format(i)+"x"+'{:04d}'.format(xygo[0])+"y"+'{:04d}'.format(xygo[1])+"d"+'{:03d}'.format(int(DISTANCE))
			if xygo is not None:					                                                            # Controls Buffer
				control[1] = xygo                                                                          # Update
				if control[0][0] != control[1][0] or control[0][1] != control[1][1]:
					control[0] = control[1]
					time.sleep(0.016)
					if WRITE:
						ser.write(str(BUFFER))
				else:
					print"Sleep"
					time.sleep(0)
			if DEBUG:
				# Comment out what you dont want to see
				#print(i)												# Face Number
				#print("Face Centre", center_point)    					# Face C.Point
				#print("Cam Centre", cam_c)								# Cam C.Point
				#print("x y", xygo)										# Servo Pos
				#print													# Serial Data
				print('Serial String',BUFFER)							# Serial Data
				#print ('Length',len(BUFFER))							# Length of serial
				#print													# Length of serial
				#print('distance', int(DISTANCE))						# Distance to object
				#print control											# Control to make buffer sleep (Con for odd occ)
	cv2.imshow('Video', frame)
	#THIS IS NOT WORKING CORRECTLY 
	if DEBUG:
		end = time.time()
		# Time elapsed
		seconds = end - start
		print "Time taken : {0} ms".format(seconds*1000)
		#fps = video_capture.get(cv2.CAP_PROP_FPS)
		#print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)
	if cv2.waitKey(1) == 27:
		break

video_capture.release()
out.release()
cv2.destroyAllWindows()