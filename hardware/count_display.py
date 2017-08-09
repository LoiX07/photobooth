# -*- coding: utf-8 -*-
"""Display module for the photobooth"""

import RPi.GPIO as GPIO


class CountDisplay:
    """ 7 segment display """

    def __init__(self, channels):
        """ Initialization of the 7 segment display """
        self.channels = channels
        # Pins configuration "
        for char in "ABCDEFG":
            GPIO.setup(self.channels[char],GPIO.OUT,initial=GPIO.LOW)

    def display(self, number):
        """ Display the requested number """
        GPIO.output(self.channels['A'],
                              number in [0, 2, 3, 5, 6, 7, 8, 9])
        GPIO.output(self.channels['B'],
                              number in [0, 1, 2, 3, 4, 7, 8, 9])
        GPIO.output(self.channels['C'],
                              number in [0, 1, 3, 4, 5, 6, 7, 8, 9])
        GPIO.output(self.channels['D'],
                              number in [0, 2, 3, 5, 6, 8, 9])
        GPIO.output(self.channels['E'],
                              number in [0, 2, 6, 8])
        GPIO.output(self.channels['F'],
                              number in [0, 4, 5, 6, 8, 9])
        GPIO.output(self.channels['G'],
                              number in [2, 3, 4, 5, 6, 8, 9])

    def switch_off(self):
        """ Shutdown of the display """
        for char in "ABCDEFG":
            GPIO.output(self.channels[char],
                    GPIO.LOW)
                                  
