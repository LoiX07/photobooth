#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Picture taking module"""

from abc import ABCMeta, abstractmethod
import logging
from os.path import join
import sys
from datetime import datetime
from time import sleep

import gphoto2 as gp
# Imports
import wiringpi2 as wiringpi

from picamera import PiCamera

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

#####################
### Configuration ###
#####################
wiringpi.wiringPiSetupGpio()  # use wiringpi numerotation


###############
### Classes ###
###############
class Camera(object):
    """ Metaclass for a camera (raspi or reflex) """
    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare_camera(self):
        """ Abstract method for camera initialization """
        pass

    @abstractmethod
    def take_picture(self, path, basename):
        """ Abstract method for taking pictures"""
        pass


class Raspicam(Camera):
    """ Camera Raspberry """

    def __init__(self):
        """ Initialization of the camera """
        self.camera = PiCamera()
        # Configuration
        if VERSION_CAMERA == 1:
            self.camera.resolution = (1024, 768)
        elif VERSION_CAMERA == 2:
            self.camera.resolution = (3280, 2464)
        # Camera warm-up
        self.camera.start_preview()
        sleep(2)

    def prepare_camera(self):
        """ Camera preparation """
        pass

    def take_picture(self, path, basename):
        """ Take a picture with the camera """
        self.camera.capture(join(path, datetime.now().strftime(basename)))

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """
        self.camera.stop_preview()
        self.camera.close()


class ReflexCam(Camera):
    """ REFLEX Camera """

    def __init__(self):
        """ Initialization of the camera """
        gp.check_result(gp.use_python_logging())
        context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera, context))

    def prepare_camera(self):
        """ Prepare the camera for the picture """
        pass

    def take_picture(self, path, basename):
        """ Take a picture with the camera """
        pass

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """


class Lamp:
    """ Lighting for the Photobooth """

    def __init__(self, channel):
        """ Initialization """
        self.channel = channel
        wiringpi.pinMode(channel, 2)
        wiringpi.pwmSetMode(channel, 0)

    def idle(self):
        """ Set the lights to idle level """
        #TODO: does it need to be a method?
        wiringpi.pwmWrite(0.1 * 1024)

    def set_level(self, level):
        """ Lighting coefficient modification between 0 and 1 """
        #TODO: does it need to be a method?
        wiringpi.pwmWrite(self.channel, level * 1024)


class CountDisplay:
    """ 7 segment display """

    def __init__(self, channels):
        """ Initialization of the 7 segment display """
        self.channels = channels
        # Pins configuration "
        for char in "ABCDEFG":
            wiringpi.pinMode(self.channels[char], 1)
            wiringpi.digitalWrite(self.channels[char], 1)

    def display(self, number):
        """ Display the requested number """
        wiringpi.digitalWrite(self.channels['A'],
                              not number in [0, 2, 3, 5, 6, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['B'],
                              not number in [0, 1, 2, 3, 4, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['C'],
                              not number in [0, 1, 3, 4, 5, 6, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['D'],
                              not number in [0, 2, 3, 5, 6, 8, 9])
        wiringpi.digitalWrite(self.channels['E'], not number in [0, 2, 6, 8])
        wiringpi.digitalWrite(self.channels['F'],
                              not number in [0, 4, 5, 6, 8, 9])
        wiringpi.digitalWrite(self.channels['G'],
                              not number in [2, 3, 4, 5, 6, 8, 9])

    def switch_off(self):
        """ Shutdown of the display """
        for char in "ABCDEF":
            wiringpi.digitalWrite(self.channels[char],
                                  1)  # swith off the segment


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
        self.camera = Raspicam()
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
            self.camera.preparation()
            # python3 range is python2 xrange
            for i in range(5, 0, -1):
                self.lamp.set_level(
                    (5 - i) / 5)  # Progressive increase of the lights
                self.count_display.display(i)  # Countdown update
                if i != 0:
                    sleep(1)
            # Take a picture
            self.camera.take_picture(self.picture_path, self.picture_basename)
            sleep(1)  #TODO : to adjust
            self.lamp.idle()
            self.count_display.switch_off()
            wiringpi.digitalWrite(self.shutdown_led_channel, 1)
            self.taking_picture = False

    def quit(self):
        """ Cleanup function """
        self.camera.close()
        self.lamp.level(0)
        self.count_display.switch_off()
        wiringpi.digitalWrite(self.trigger_led_channel, 0)
        wiringpi.digitalWrite(self.shutdown_led_channel, 0)
        sys.exit()


def main():
    """ Main script """
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)

    Photobooth(PICTURE_PATH, PICTURE_BASENAME, PICTURE_SIZE,
               GPIO_TRIGGER_CHANNEL, GPIO_TRIGGER_LED_CHANNEL,
               GPIO_7SEGMENTS_DISPLAY, GPIO_SHUTDOWN_CHANNEL,
               GPIO_SHUTDOWN_LED_CHANNEL, GPIO_LAMP_CHANNEL)
    while True:
        sleep(10)


if __name__ == "__main__":
    exit(main())
