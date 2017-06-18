# Imports
import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera


# Constante
versionCamera = 1 # 1 ou 2 en fonction de la version de la pi camera utilisée

# Initialisation
camera = PiCamera()

# Configuration
if versionCamera==1
    camera.resolution = (1024, 768)
elif versionCamera==2
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

