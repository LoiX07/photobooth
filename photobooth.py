#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Picture taking module"""

import logging
import socket
import sys
from datetime import datetime
from time import sleep

import wiringpi2 as wiringpi
from hardware import CountDisplay, Lamp, RaspiCam
from tools.photo_log import PHOTO_LOG as log

##################
### Parameters ###
##################
GPIO_LAMP_CHANNEL = 18
GPIO_TRIGGER_CHANNEL = 23
GPIO_SHUTDOWN_CHANNEL = 24
GPIO_7SEGMENTS_DISPLAY = {
    "A": 2,
    "B": 3,
    "C": 4,
    "D": 17,
    "E": 27,
    "F": 22,
    "G": 5
}
GPIO_SHUTDOWN_LED_CHANNEL = 12
GPIO_TRIGGER_LED_CHANNEL = 25
PICTURE_PATH = datetime.now().strftime("%Y-%m-%d_Photomaton")
PICTURE_BASENAME = "%H-%M-%S_Photomaton.jpeg"
#TODO: fill in the value
PICTURE_SIZE = 0
TYPE_CAMERA = 1  # 1 for raspberry pi camera, 2 for a reflex camera
VERSION_CAMERA = 1  # 1 or 2 depending of the camera version

HOST, PORT = "localhost", 5817

#####################
### Configuration ###
#####################
wiringpi.wiringPiSetupGpio()  # use wiringpi numerotation


###############
### Classes ###
###############
class Photobooth:
    """ Photobooth """

    def __init__(self, picture_path, picture_basename, picture_size,
                 trigger_channel, trigger_led_channel, seven_segments_channels,
                 shutdown_channel, shutdown_led_channel, lamp_channel):
        """ Initialization """
        # Initialize the parameters
        self.picture_path = picture_path
        self.picture_basename = picture_basename
        self.picture_size = picture_size
        self.trigger_channel = trigger_channel
        self.shutdown_channel = shutdown_channel
        self.trigger_led_channel = trigger_led_channel
        self.shutdown_led_channel = shutdown_led_channel

        # Create the objects
        self.camera = RaspiCam(version=VERSION_CAMERA)
        self.count_display = CountDisplay(seven_segments_channels)
        self.lamp = Lamp(lamp_channel)

        # Switch on the lights
        self.lamp.idle()
        wiringpi.digitalWrite(self.trigger_led_channel, 1)
        wiringpi.digitalWrite(self.shutdown_led_channel, 1)

        # Events detection
        wiringpi.pinMode(trigger_channel, 0)
        wiringpi.pullUpDnControl(trigger_channel, 1)
        wiringpi.wiringPiISR(trigger_channel, 2, self.take_picture)
        wiringpi.pinMode(shutdown_channel, 0)
        wiringpi.pullUpDnControl(shutdown_channel, 1)
        #TODO: undefined variable trigger_shutdown?
        wiringpi.wiringPiISR(trigger_shutdown, 2, self.quit)

        # semaphore on picture taking (to ignore a second clic during a taking picture sequence)
        self.taking_picture = False

    def take_picture(self):
        """ Launch the photo sequence """
        # equivalent: if self.taking_picture is False
        if not self.taking_picture:
            self.taking_picture = True
            wiringpi.digitalWrite(self.shutdown_led_channel, 0)
            self.camera.prepare_camera()
            # python3 range is python2 xrange
            for i in range(5, 0, -1):
                self.lamp.set_level(
                    (5 - i) / 5)  # Progressive increase of the lights
                self.count_display.display(i)  # Countdown update
                if i != 0:
                    sleep(1)
            # Take a picture
            new_name = self.camera.take_picture(self.picture_path, self.picture_basename)
            # send the picture name through a TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Connect to server and send data
                sock.connect((HOST, PORT))
                sock.sendall(bytes(new_name + "\n", "utf-8"))
            sleep(1)  #TODO : to adjust
            self.lamp.idle()
            self.count_display.switch_off()
            wiringpi.digitalWrite(self.shutdown_led_channel, 1)
            self.taking_picture = False

    def quit(self):
        """ Cleanup function """
        self.camera.close()
        self.lamp.set_level(0)
        self.count_display.switch_off()
        wiringpi.digitalWrite(self.trigger_led_channel, 0)
        wiringpi.digitalWrite(self.shutdown_led_channel, 0)
        sys.exit()


def main():
    """ Main script """
    # set up the logging
    console = logging.StreamHandler()

    formatter = logging.Formatter('%(levelname)s: %(name)s: %(message)s')
    console.setFormatter(formatter)
    log.setFormatter(formatter)

    log.setLevel(logging.WARNING)
    console.setLevel(logging.WARNING)

    log.addHandler(console)

    Photobooth(PICTURE_PATH, PICTURE_BASENAME, PICTURE_SIZE,
               GPIO_TRIGGER_CHANNEL, GPIO_TRIGGER_LED_CHANNEL,
               GPIO_7SEGMENTS_DISPLAY, GPIO_SHUTDOWN_CHANNEL,
               GPIO_SHUTDOWN_LED_CHANNEL, GPIO_LAMP_CHANNEL)
    while True:
        sleep(10)


if __name__ == "__main__":
    exit(main())
