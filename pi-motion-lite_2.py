#!/usr/bin/python

# This script implements a motion capture surveillace cam for raspery pi using picam.
# It uses the motion vecors magnitude of the h264 hw-encoder to detect motion activity.
# At the time of motion detection a jpg snapshot is saved together with a h264 video stream
# some seconds before, during and after motion activity to the 'filepath' directory.
# Orginally posted by killagreg on Raspberry Pi Forum 
# at http://www.raspberrypi.org/forums/viewtopic.php?p=656881#p656881
# can be downloaded to RPI per following
# wget https://raw.github.com/pageauc/pi-motion-lite/master/pi-motion-lite_2.py

import os
import subprocess
import io
import picamera
import picamera.array
import numpy as np
import datetime as dt
import time
from PIL import Image

#debug mode?
debug = 1
#seup filepath for motion capure data
filepath = '/home/pi/motion/video'
# setup pre and post video recording around motion event
video_preseconds = 3
video_postseconds = 3
#setup video/snapshot resolution
video_width = 640   #1280
video_height = 480  #720
#setup video rotation (0, 180)
video_rotation = 180

# setup motion detection resolution, equal or smaller than video resolution
motion_width = 640
motion_height = 480
# setup motion detection threshold, i.e. magnitude of a motion block to count as  motion
motion_threshold = 30
# setup motion detection sensitivity, i.e number of motion blocks that trigger a motion detection
motion_sensitivity = 6
# motion masks define areas within the motion analysis picture that are used for motion analysis
 # [ [[start pixel on left side,end pixel on right side],[start pixel on top side,stop pixel on bottom side]] ]
# default this is the whole image frame
#motion_mask_count = 1
#motion_masks = [ [[1,motion_width],[1,motion_height]] ]
# another example
motion_mask_count = 1
motion_masks = [ [[270,370],[190,290]]  ]
# exaple for 2 mask areas
#motion_mask_count = 2
#motion_masks = [ [[1,320],[1,240]], [[400,500],[300,400]] ]

# do not change code behind that line
#--------------------------------------
motion_detected = False
motion_timestamp = time.time()
motion_cols = (motion_width  + 15) // 16 + 1
motion_rows = (motion_height + 15) // 16
motion_array = np.zeros((motion_rows, motion_cols), dtype = np.uint8)
# create motion mask
motion_array_mask = np.zeros((motion_rows, motion_cols), dtype = np.uint8)
for count in xrange(0, motion_mask_count):
   for col in xrange( (motion_masks[count][0][0]-1)//16, (motion_masks[count][0][1]-1+15)//16 ):
      for row in xrange( (motion_masks[count][1][0]-1)//16, (motion_masks[count][1][1]-1+15)//16 ):
         motion_array_mask[row][col] = 1

#motion_array_mask[4:8, 3:9] = 255

#call back handler for motion output data from h264 hw encoder
class MyMotionDetector(picamera.array.PiMotionAnalysis):
   def analyse(self, a):
      global motion_detected, motion_timestamp, motion_array, motion_array_mask
      # calcuate length of motion vectors of mpeg macro blocks
      a = np.sqrt(
          np.square(a['x'].astype(np.float)) +
          np.square(a['y'].astype(np.float))
          ).clip(0, 255).astype(np.uint8)
      a = a * motion_array_mask
      # If there're more than 'sensitivity' vectors with a magnitude greater
      # than 'threshold', then say we've detected motion
      th = ((a > motion_threshold).sum() > motion_sensitivity)
      now = time.time()
      # motion logic, trigger on motion and stop after 2 seconds of inactivity
      if th:
         motion_timestamp = now

      if motion_detected:
          if (now - motion_timestamp) >= video_postseconds:
               motion_detected = False
      else:
        if th:
             motion_detected = True
        if debug:
                idx = a > motion_threshold
                a[idx] = 255
                motion_array = a


def write_video(stream):
# Write the entire content of the circular buffer to disk. No need to
# lock the stream here as we're definitely not writing to it
# simultaneously
     global motion_filename

     with io.open(motion_filename + '-before.h264', 'wb') as output:
         for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
         while True:
            buf = stream.read1()
            if not buf:
               break
            output.write(buf)
     # Wipe the circular stream once we're done
     stream.seek(0)
     stream.truncate()


os.system('clear')
print "Motion Detection"
print "----------------"
print "                "
with picamera.PiCamera() as camera:
   camera.resolution = (video_width, video_height)
   camera.framerate = 25
   camera.rotation = video_rotation
   camera.video_stabilization = True
   camera.annotate_background = True
   # setup a circular buffer
   stream = picamera.PiCameraCircularIO(camera, seconds = video_preseconds)
   # hi resolution video recording into circular buffer from splitter port 1
   camera.start_recording(stream, format='h264', splitter_port=1)
   #camera.start_recording('test.h264', splitter_port=1)
   # low resolution motion vector analysis from splitter port 2
   camera.start_recording('/dev/null', splitter_port=2, resize=(motion_width,motion_height) ,format='h264', motion_output=MyMotionDetector(camera, size=(motion_width,motion_height)))
   # wait some seconds for stable video data
   camera.wait_recording(2, splitter_port=1)
   motion_detected = False

   print "Motion Capture ready!"
   try:
       while True:
          # motion event must trigger this action here
          camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          if motion_detected:
             print "Motion detected: " , dt.datetime.now()
             motion_filename = filepath + "/" + time.strftime("%Y%m%d-%H%M%S", time.gmtime(motion_timestamp))
             camera.split_recording(motion_filename + '-after.h264', splitter_port=1)
             # catch an image as video preview during video recording (uses splitter port 0) at time of the motion event
             camera.capture_sequence([motion_filename + '.jpg'], use_video_port=True, splitter_port=0)
             # dump motion array as image
                            if debug:
                img = Image.fromarray(motion_array)
                img.save(motion_filename + "-motion.png")
             # save circular buffer before motion event
             write_video(stream)
             #wait for end of motion event here
             while motion_detected:
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.wait_recording(1, splitter_port=1)
             #split video recording back in to circular buffer
             camera.split_recording(stream, splitter_port=1)
             subprocess.call("cat %s %s > %s && rm -f %s" % (motion_filename + "-before.h264", motion_filename + "-after.h264", motion_filename + ".h264", motion_filename + "-*.h264"), shell=True)
             print "Motion stopped:" , dt.datetime.now()


   finally:
       camera.stop_recording(splitter_port=1)
       camera.stop_recording(splitter_port=2)