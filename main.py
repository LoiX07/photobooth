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
gpio_7segment_display = {"A" : 2, "B" : 3, "C" : 4, "D" : 17, "E" : 27, "F" : 22, "G" : 10} 
picture_basename = datetime.now().strftime("%Y-%m-%d_Photomaton")

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
        """ Initialization """
        self.channel = channel
        wiringpi.pinMode(channel,2)
        wiringpi.pwmSetMode(channel,0)
        wiringpi.pwmWrite(0.1*1024)
    
    def setLevel(level):
        """ Modification du coefficient de l'éclairage, entre 0 et 1 """
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

class Photobooth:
    """ Photobooth """
    
    def __init__(self,picture_basename,picture_size,trigger_channel, shutdown_channel, lamp_channel):
        """ Initialization """
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
        

    def takePicture():
        """ Launch the photo sequence """
        #TODO : penser à bloquer le 2nd appel si 2 clics sur le bouton

    def quit(self):
        self.lamp.level(0)

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

