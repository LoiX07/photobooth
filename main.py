# Imports
import exceptions
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera


##################
### Parameters ###
##################
gpio_lamp_channel = 
gpio_trigger_channel =
gpio_shutdown_channel = 
picture_basename = datetime.now().strftime("%Y-%m-%d_Photomaton")

#####################
### Configuration ###
#####################
GPIO.setmode(GPIO.BCM)



###############
### Classes ###
###############
class Camera:
""" Objet camera """
    def takeAPicture(self):
        raise NotImplemented

class Raspicam(Camera):
""" Camera Raspberry """
    def __init__(self):
        self.camera = PiCamera()

    def takeAPicture(self):

class ReflexCam(Camera):
""" Appareil photo REFLEX """
    def takeAPicture(self):

class Lamp:
""" Eclairage Photobooth """
    def __init__(channel):
    """ Initialisation """
        self.channel = channel
    
    def setLevel(level)
    """ Modification du coefficient de l'éclairage, entre 0 et 1 """

class CountDisplay
""" 7 segment display """

class Photobooth:
""" Photobooth """
    
    def __init__(self,picture_basename,picture_size,trigger_channel, shutdown_channel, lamp_channel):
        # Initialize the parameters
        self.trigger_channel = trigger_channel
        self.shutdown_channel = shutdown_channel
        
        # Create the objects
        self.camera = 0000
        self.countDisplay = CountDisplay()
        self.lamp = Lamp(lamp_channel)
        ### self.gpio = GPIO(self.handle_gpio, input_channels, output_channels)
        ### Ajouter la détection d'évènements

    def quit(self):
        self.lamp.level(0)
        GPIO.cleanup()

# Constante
versionCamera = 1 # 1 ou 2 en fonction de la version de la pi camera utilisée


# Configuration
if versionCamera==1:
    camera.resolution = (1024, 768)
elif versionCamera==2:
    camera.resolution = (3280,2464)

# Exception pour quitter la boucle

camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('foo.jpg')

# Eclairage en attente
# While true
    # Compte à rebourd
    # Eclairage plus puissant
    # Prise de la photo

