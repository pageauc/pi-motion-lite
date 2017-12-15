#!/usr/bin/env python
# Minimal Motion Detection Logic written by Claude Pageau Dec-2014
# Version 0.5

# Import Libraries
import time
import datetime
from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread
import numpy as np
from fractions import Fraction

# Display Log Info
verbose = True     # Display showMessage if True

# Motion Settings
threshold = 20     # How Much a pixel has to change
sensitivity = 300  # How Many pixels need to change for motion detection

# Camera Settings
CAMERA_WIDTH = 128
CAMERA_HEIGHT = 80     
CAMERA_HFLIP = True
CAMERA_VFLIP = True
CAMERA_ROTATION= 0
CAMERA_FRAMERATE = 35

#-------------------------------------------------------------------------------------------  
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
            
#------------------------------------------------------------------------------------------- 
def userMotionCode():
    # Users can put code here that needs to be run prior to taking motion capture images
    # Eg Notify or activate something.
    # User code goes here
    
    msgStr = "Motion Found So Do Something ..."
    showMessage("userMotionCode",msgStr)  
    return   

#-------------------------------------------------------------------------------------------    
def showTime():
    rightNow = datetime.datetime.now()
    currentTime = "%04d%02d%02d-%02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return currentTime    

#-------------------------------------------------------------------------------------------     
def showMessage(functionName, messageStr):
    if verbose:
        now = showTime()
        print ("%s %s - %s " % (now, functionName, messageStr))
    return

#----------------------------------------------------------------------------------------------- 
def checkForMotion(data1, data2):
    # Find motion between two data streams based on sensitivity and threshold
    motionDetected = False
    pixColor = 3 # red=0 green=1 blue=2 all=3  default=1
    if pixColor == 3:
        pixChanges = (np.absolute(data1-data2)>threshold).sum()/3
    else:
        pixChanges = (np.absolute(data1[...,pixColor]-data2[...,pixColor])>threshold).sum()
    if pixChanges > sensitivity:
        motionDetected = True
        msgStr = ("Found Motion threshold=%s  sensitivity=%s changes=%s" % ( threshold, sensitivity, pixChanges ))
        showMessage("checkForMotion", msgStr)         
    return motionDetected  

#-------------------------------------------------------------------------------------------    
def Main():
    msgStr = "Checking for Motion"
    showMessage("Main", msgStr)   
    frame_1 = vs.read()    
    while True:
        frame_2 = vs.read()  
        if checkForMotion(frame_1, frame_2):
            userMotionCode()
        frame_1 = frame_2   
    return

#-------------------------------------------------------------------------------------------     
if __name__ == '__main__':
    try:
        msgStr = "Loading .... One Moment Please"
        showMessage("Init", msgStr)    
        vs = PiVideoStream().start()   # Initialize video stream
        vs.camera.hflip = CAMERA_HFLIP
        vs.camera.vflip = CAMERA_VFLIP
        vs.camera.rotation = CAMERA_ROTATION        
        time.sleep(2.0)    # Let camera warm up         
        Main()
    finally:
        print("")
        print("+++++++++++++++++++")
        print("  Exiting Program")
        print("+++++++++++++++++++")
        print("")
               
            
