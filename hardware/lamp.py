# -*- coding: utf-8 -*-

"""Lighting module for the photobooth"""

import RPi.GPIO as GPIO

from math import *


class Lamp:
    """ Lighting for the Photobooth """

    def __init__(self, channel):
        """ Initialization """
        self.channel = channel
        GPIO.setup(self.channel,GPIO.OUT,initial=GPIO.LOW)

    def off(self):
        """ Set the lights to idle level """
        GPIO.output(self.channel,GPIO.LOW)

    def on(self):
        """ Lighting coefficient modification between 0 and 1 """
        GPIO.output(self.channel,GPIO.HIGH)
