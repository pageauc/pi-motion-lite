                      pi-motion-lite
        raspberry pi with camera module using picamera python module
              to do simple motion detection
                 
Introduction
------------
This is a raspberry pi computer minimal motion detection python script.
The script requires the picamera python module to be installed.
It uses piRGBArray data streams to detect motion (pixel differences). 
Day and night camera settings are supported for streams.  
This is a minimal code implementation for use in projects.

Hardware
--------
Raspberry Pi computer A, A+, B, or B+ or compute module
Raspberry Pi camera module

additiona support hardware eg SD card, PowerSupply, cables, etc.
I will not list the details for setup since you can google for this information
check out  http://www.raspberrypi.org/downloads/ for one source of information.

This assumes you have a raspbian image installed and operational with
the picamera module installed and operational

Software
--------
This code is available on github at https://www.github.com/pageauc

To setup pi-motion-lite on your raspberry pi perform the following
from a putty ssh session or pi monitor console.

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-picamera
cd ~
mkdir pi-motion-lite
cd pi-motion-lite
wget https://raw.github.com/pageauc/pi-motion-lite/master/pi-motion-lite.py
chmod + x pi-motion-lite.py
./pi-motion-lite.py
or
python ./pi-motion-lite.py

Use IDLE, nano or any other text editor to modify code for your project needs.
adjust threshold and sensitivity to suit conditions.

threshold   - How Much a pixel needs to change before it is counted.
              Normal value would be 10 but can be between 1 and 254
              254 would be full black to white change.
sensitivity - How Many pixels need to change before motion detected. 
              Higher value is less sensitive.  default=200
              for 100x75 stream max value would be 7500             

Important
---------
If you are using a previous Picamera python module and images are black
or have problems with an older raspbian install, then update Raspberry PI
firmware per commands below. From a (putty) ssh login or monitor terminal
execute the following commands to upgrade to latest firmware.
This should resolve any picamera issues.

# Update Raspbian
sudo apt-get update
# Update RPI firmware
sudo rpi-update
# Hard boot to update firmware
sudo shutdown -h now

Note the checkForMotion function uses the green (1) portion of the RGB stream for
pixel diff comparison. You might want to change the pixColor variable to Red(0) or Blue(2)
in the checkForMotion function.

Let me know what type of projects you implement with this.

I also have pi-timolo python program on my github repository that implements
timelapse, motion detection and low light including auto detect of day, night, twilight
changes without the need for a clock or time calculation.  There are
also various previous versions that use raspistill rather than picamera python module

Claude Pageau
email: pageauc@gmail.com