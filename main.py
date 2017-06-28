# Imports
import exceptions
import wiringpi2 as wiringpi
from time import sleep
from picamera import PiCamera


##################
### Parameters ###
##################
gpio_lamp_channel = 18
gpio_trigger_channel = 23
gpio_shutdown_channel = 24
picture_basename = datetime.now().strftime("%Y-%m-%d_Photomaton")

#####################
### Configuration ###
#####################
wiringpi.wiringPiSetup() # use wiringpi numerotation

###############
### Classes ###
###############
class Camera:
    """ Objet camera """
    
    def prepareCamera(self):
        """ Préparation de la camera pour la photo"""
        raise NotImplemented

    def takeAPicture(self,path):
        raise NotImplemented

class Raspicam(Camera):
    """ Camera Raspberry """
    def prepareCamera(self):
        """ Camera preparation """

    def __init__(self):
        self.camera = PiCamera()

    def takeAPicture(self,path):
        """ Take a picture with the camera """

class ReflexCam(Camera):
    """ REFLEX Camera """
    def prepareCamera(self):
        """ Prepare the camera for the picture """

    def takeAPicture(self,path):
        """ Take a picture with the camera """

class Lamp:
    """ Eclairage Photobooth """
    def __init__(channel):
        """ Initialisation """
        self.channel = channel
        wiringpi.pinMode(channel,2)
        wiringpi.pwmSetMode(channel,0)
        wiringpi.pwmWrite(0.1*1024)
    
    def setLevel(level):
        """ Modification du coefficient de l'éclairage, entre 0 et 1 """
        wiringpi.pwmWrite(self.channel,level*1024)    

class CountDisplay:
    """ 7 segment display """

class Photobooth:
    """ Photobooth """
    
    def __init__(self,picture_basename,picture_size,trigger_channel, shutdown_channel, lamp_channel):
        """ Initialisation """
        # Initialize the parameters
        self.trigger_channel = trigger_channel
        self.shutdown_channel = shutdown_channel
        
        # Create the objects
        self.camera = 0000
        self.countDisplay = CountDisplay()
        self.lamp = Lamp(lamp_channel)
        # Détection d'évènements
        wiringpi.pinMode(trigger_channel,0)
        wiringpi.pullUpDnControl(trigger_channel,1)
        wiringpi.wiringPISR(trigger_channel,2,takePicture)
        wiringpi.pinMode(shutdown_channel,0)
        wiringpi.pullUpDnControl(shutdown_channel,1)
        wiringpi.wiringPISR(trigger_shutdown,2,quit)
        

    def quit(self):
        self.lamp.level(0)
        # GPIO.cleanup()

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

