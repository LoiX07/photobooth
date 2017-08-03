# -*- coding: utf-8 -*-
"""Display module for the photobooth"""

import wiringpi


class CountDisplay:
    """ 7 segment display """

    def __init__(self, channels):
        """ Initialization of the 7 segment display """
        self.channels = channels
        # Pins configuration "
        for char in "ABCDEFG":
            wiringpi.pinMode(self.channels[char], 1)
            wiringpi.digitalWrite(self.channels[char], 0)

    def display(self, number):
        """ Display the requested number """
        wiringpi.digitalWrite(self.channels['A'],
                              number in [0, 2, 3, 5, 6, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['B'],
                              number in [0, 1, 2, 3, 4, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['C'],
                              number in [0, 1, 3, 4, 5, 6, 7, 8, 9])
        wiringpi.digitalWrite(self.channels['D'],
                              number in [0, 2, 3, 5, 6, 8, 9])
        wiringpi.digitalWrite(self.channels['E'],
                              number in [0, 2, 6, 8])
        wiringpi.digitalWrite(self.channels['F'],
                              number in [0, 4, 5, 6, 8, 9])
        wiringpi.digitalWrite(self.channels['G'],
                              number in [2, 3, 4, 5, 6, 8, 9])

    def switch_off(self):
        """ Shutdown of the display """
        for char in "ABCDEF":
            wiringpi.digitalWrite(self.channels[char],
                                  1)  # swith off the segment
