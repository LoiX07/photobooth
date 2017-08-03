#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Picture taking module"""

import argparse
from multiprocessing import Process, Queue
import logging
import socket
import sys
from datetime import datetime
from time import sleep

from wiringpi import *
from hardware import CountDisplay, Lamp
from tools.photo_log import PHOTO_LOG as log

##################
### Parameters ###
##################

# GPIO connections
GPIO_LAMP_CHANNEL = 18
GPIO_TRIGGER_CHANNEL = 23
GPIO_TRIGGER_LED_CHANNEL = 25
GPIO_SHUTDOWN_CHANNEL = 24
GPIO_SHUTDOWN_LED_CHANNEL = 12
GPIO_7SEGMENTS_DISPLAY = {
    "A": 2,
    "B": 3,
    "C": 4,
    "D": 17,
    "E": 27,
    "F": 22,
    "G": 5
}

# Camera type and version
TYPE_CAMERA = 2  # 1 for raspberry pi camera, 2 for a reflex camera
VERSION_CAMERA = 2  # 1 or 2 depending of the camera version

if TYPE_CAMERA == 1:
    from hardware import RaspiCam
elif TYPE_CAMERA == 2:
    from hardware import ReflexCam

# Pictures properties
PICTURE_FOLDER = datetime.now().strftime("%Y-%m-%d_Photomaton")
PICTURE_BASENAME = "%H-%M-%S_Photomaton.jpeg"
PICTURE_SIZE = 0  # TODO: fill in the value

# Network parameters
HOST, PORT = "localhost", 5817

#####################
### Configuration ###
#####################
wiringPiSetupGpio()  # use wiringpi numerotation


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
        self.picture_path = picture_path + "/" + PICTURE_FOLDER
        self.picture_basename = picture_basename
        self.picture_size = picture_size
        self.trigger_channel = trigger_channel
        self.shutdown_channel = shutdown_channel
        self.trigger_led_channel = trigger_led_channel
        self.shutdown_led_channel = shutdown_led_channel

        # Create the objects
        if TYPE_CAMERA == 1:
            self.camera = RaspiCam(version=VERSION_CAMERA)
        elif TYPE_CAMERA == 2:
            self.camera = ReflexCam()
        self.count_display = CountDisplay(seven_segments_channels)
        self.lamp = Lamp(lamp_channel)

        # Switch on the lights
        pinMode(self.trigger_led_channel, OUTPUT)
        digitalWrite(self.trigger_led_channel, HIGH)
        pinMode(self.shutdown_led_channel, OUTPUT)
        digitalWrite(self.shutdown_led_channel, HIGH)

        # Events detection
        pinMode(trigger_channel, INPUT)
        pullUpDnControl(trigger_channel, PUD_UP)
        wiringPiISR(trigger_channel, INT_EDGE_FALLING, self.take_picture)
        pinMode(shutdown_channel, INPUT)
        pullUpDnControl(shutdown_channel, PUD_UP)
        wiringPiISR(shutdown_channel, INT_EDGE_FALLING, self.quit)

        # semaphore on picture taking (to ignore a second clic during a taking
        # picture sequence)
        self.taking_picture = False

        # create the compressing process
        self.queue = Queue()
        self.process = Process(target=self.process_new_picture, args=())
        self.process.start()

    def take_picture(self):
        """ Launch the photo sequence """
        # equivalent: if self.taking_picture is False
        if not self.taking_picture:
            self.taking_picture = True
            digitalWrite(self.trigger_led_channel, 0)
            self.camera.prepare_camera()
            # python3 range is python2 xrange
            for i in range(5, 0, -1):
                self.lamp.set_level(
                    (5 - i) / 5)  # Progressive increase of the lights
                self.count_display.display(i)  # Countdown update
                if i != 0:
                    sleep(1)
            self.count_display.display(0)  # Countdown update
            # Take a picture
            new_name = self.camera.take_picture(
                self.picture_path, self.picture_basename)
            # Reset the buttons
            self.count_display.switch_off()
            digitalWrite(self.trigger_led_channel, HIGH)
            # send the picture name through a TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # Connect to server and send data
                sock.connect((HOST, PORT))
                sock.sendall(bytes(new_name + "\n", "utf-8"))
            # now put it into the queue
            self.queue.put(new_name)
            sleep(1)  # TODO : to adjust
            self.lamp.idle()
            self.count_display.switch_off()
            digitalWrite(self.shutdown_led_channel, 1)
            self.taking_picture = False

    def process_new_picture(self):
        while True:
            if not self.queue.empty():
                name = self.queue.get()
                if name == 'exit':
                    return
                # TODO somehow process the new picture
                # send the picture name through a TCP socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    # Connect to server and send data
                    sock.connect((HOST, PORT))
                    # TODO name needs to be changed
                    sock.sendall(bytes(name + "\n", "utf-8"))

    def quit(self):
        """ Cleanup function """
        self.queue.put("exit")
        self.camera.close()
        self.lamp.set_level(0)
        self.count_display.switch_off()
        digitalWrite(self.trigger_led_channel, 0)
        digitalWrite(self.shutdown_led_channel, 0)
        sys.exit()


#################
### Functions ###
#################


def parse_args():
    """
    Helper function that parses the command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Programme principal du Photobooth')
    parser.add_argument(
        '--path', type=str, help='path to save the pictures', required=True)
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        help='verbose logging')
    args = parser.parse_args()
    return args


def main():
    """
    Main function
    """
    # Parse the args
    args = parse_args()

    # set up the logging
    console = logging.StreamHandler()

    formatter = logging.Formatter('%(levelname)s: %(name)s: %(message)s')
    console.setFormatter(formatter)

    if args.verbose:
        log.setLevel(logging.DEBUG)
        console.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.ERROR)
        console.setLevel(logging.ERROR)

    log.addHandler(console)

    Photobooth(args.path, PICTURE_BASENAME, PICTURE_SIZE,
               GPIO_TRIGGER_CHANNEL, GPIO_TRIGGER_LED_CHANNEL,
               GPIO_7SEGMENTS_DISPLAY, GPIO_SHUTDOWN_CHANNEL,
               GPIO_SHUTDOWN_LED_CHANNEL, GPIO_LAMP_CHANNEL)
    while True:
        sleep(10)


if __name__ == "__main__":
    exit(main())
