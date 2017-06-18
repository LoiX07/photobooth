# Imports
from time import sleep
from picamera import PiCamera

# Initialisation
camera = PiCamera()

# Configuration
camera.resolution = (1024, 768)


camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('foo.jpg')

