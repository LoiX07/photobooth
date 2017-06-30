# Imports
import exceptions
import wiringpi2 as wiringpi
import sys
from time import sleep
from picamera import PiCamera


##################
### Parameters ###
##################
gpio_lamp_channel = 18
gpio_trigger_channel = 23
gpio_shutdown_channel = 24
gpio_7segments_display = {"A" : 2, "B" : 3, "C" : 4, "D" : 17, "E" : 27, "F" : 22, "G" : 5} 
gpio_shutdown_led = 12 
gpio_trigger_led = 25
picture_basename = datetime.now().strftime("%Y-%m-%d_Photomaton")
typeCamera = 1 # 1 for raspberry pi camera, 2 for a reflex camera
versionCamera = 1 # 1 or 2 depending of the camera version

#####################
### Configuration ###
#####################
wiringpi.wiringPiSetupGpio() # use wiringpi numerotation

###############
### Classes ###
###############
class Camera:
    """ Objet camera """
    
    def prepareCamera(self):
        """ Camera initialization """
        raise NotImplemented

    def takeAPicture(self,path):
        raise NotImplemented

class Raspicam(Camera):
    """ Camera Raspberry """

    def __init__(self):
        self.camera = PiCamera()
        # Configuration
        if versionCamera==1:
            camera.resolution = (1024, 768)
        elif versionCamera==2:
            camera.resolution = (3280,2464)
    
    def prepareCamera(self):
        """ Camera preparation """
        # Camera warm-up
        camera.start_preview()

    def takeAPicture(self,path):
        """ Take a picture with the camera """
        camera.capture(path + "/" + datetime.now().strftime("Photomaton_%H-%M"))
        camera.stop_preview()

    def close():
        """ Free the camera ressources to avoid GPU memory leaks """
        camera.close()

class ReflexCam(Camera):
    """ REFLEX Camera """
    def prepareCamera(self):
        """ Prepare the camera for the picture """

    def takeAPicture(self,path):
        """ Take a picture with the camera """

    def close():
        """ Free the camera ressources to avoid GPU memory leaks """

class Lamp:
    """ Lighting for the Photobooth """
    def __init__(channel):
        """ Initialization """
        self.channel = channel
        wiringpi.pinMode(channel,2)
        wiringpi.pwmSetMode(channel,0)
        wiringpi.pwmWrite(0.1*1024)
    
    def setLevel(level):
        """ Lighting coefficient modification between 0 and 1 """
        wiringpi.pwmWrite(self.channel,level*1024)    

class CountDisplay:
    """ 7 segment display """
    
    def __init__(channels):
        """ Initialization of the 7 segment display """
        self.channels = channels
        # Pins configuration "
        for char in "ABCDEFG":
            wiringpi.pinMode(self.channels[char],1)
            wiringpi.digitalWrite(self.channels[char],1)

    def display(number):
        """ Display the requested number """
        wiringpi.digitalWrite(self.channels['A'], not number in [0,2,3,5,6,7,8,9])
        wiringpi.digitalWrite(self.channels['B'], not number in [0,1,2,3,4,7,8,9])
        wiringpi.digitalWrite(self.channels['C'], not number in [0,1,3,4,5,6,7,8,9])
        wiringpi.digitalWrite(self.channels['D'], not number in [0,2,3,5,6,8,9])
        wiringpi.digitalWrite(self.channels['E'], not number in [0,2,6,8])
        wiringpi.digitalWrite(self.channels['F'], not number in [0,4,5,6,8,9])
        wiringpi.digitalWrite(self.channels['G'], not number in [2,3,4,5,6,8,9])

    def switch_off():
        for char in "ABCDEF":
            wiringpi.digitalWrite(self.channels[char],1) # swith off the segment

class Photobooth:
    """ Photobooth """
    
    def __init__(self,picture_basename,picture_size,trigger_channel, trigger_led_channel, seven_segments_channels, shutdown_channel, shutdown_led_channel, lamp_channel):
        """ Initialization """
        # Initialize the parameters
        self.trigger_channel = trigger_channel
        self.shutdown_channel = shutdown_channel
        self.trigger_led_channel = trigger_led_channel
        self.shutdown_led_channel = shutdown_led_channel

        # Create the objects
        self.camera = 0000 #TODO
        self.countDisplay = CountDisplay(seven_segments_channels)
        self.lamp = Lamp(lamp_channel)

        # Events detection
        wiringpi.pinMode(trigger_channel,0)
        wiringpi.pullUpDnControl(trigger_channel,1)
        wiringpi.wiringPiISR(trigger_channel,2,takePicture)
        wiringpi.pinMode(shutdown_channel,0)
        wiringpi.pullUpDnControl(shutdown_channel,1)
        wiringpi.wiringPiISR(trigger_shutdown,2,quit)

        # semaphore on picture taking (to ignore a second clic during a taking picture sequence)
        self.takingPicture = False

    def takePicture():
        """ Launch the photo sequence """
        self.takingPicture = True
        #TODO 
        self.takingPicture = False

    def quit(self):
        self.camera.close()
        self.lamp.level(0)
        self.countDisplay.switch_off()
        wiringpi.digitalWrite(self.trigger_led_channel,0)
        wiringpi.digitalWrite(self.shutdown_led_channel,0)
        sys.exit()





# Eclairage en attente
# While true
    # Compte à rebourd
    # Eclairage plus puissant
    # Prise de la photo

