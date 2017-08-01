# -*- coding: utf-8 -*-

"""Lighting module for the photobooth"""

import wiringpi

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
