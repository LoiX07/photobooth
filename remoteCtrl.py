#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote control module for the photobooth project
"""

import os
import threading
from multiprocessing import Process, Queue
from time import sleep
from datetime import datetime
import argparse
from socketserver import TCPServer
import pygame
from utils.gui import GUIModule
from utils.tcp import PhotoServer

##################
### Parameters ###
##################
PICTURE_PATH = datetime.now().strftime("%Y-%m-%d_Photomaton")
PICTURE_SUFFIX = "_Photomaton.jpeg"

#####################
### Configuration ###
#####################
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')


###############
### Classes ###
###############
class Slideshow:
    """ Slideshow : displays pictures in a folder and when a new picture is
    taken, displays it during a few time and let user choose if he wants to
    delete it """

    def __init__(self, *args, **kwargs):
        self.directory = kwargs.get('path')
        self.recursive = kwargs.get('recursive')
        self.filelist = []
        self.display = GUIModule("Slideshow", kwargs.get('size'))
        self.display_time = kwargs.get('time')
        self.next = 0
        self.time_before_next = self.display_time
        self.scrolling = True
        self.quitting = False
        self.step = 0.1
        self._queue = kwargs.get('queue')
        self._monitoring_thread = threading.Thread(target=self.monitorEvents)
        self._monitoring_thread.start()  # Run

    def scan(self):
        """ Scan the photo dir in order to get a list of files """
        filelist = []
        if self.recursive:
            # Recursively walk all entries in the directory
            for root, _, filenames in os.walk(
                    self.directory, followlinks=True):
                for filename in filenames:
                    filelist.append(os.path.join(root, filename))
        else:
            # Add all entries in the directory
            for item in os.listdir(self.directory):
                filename = os.path.join(self.directory, item)
                if os.path.isfile(filename):
                    filelist.append(filename)

        self.filelist = filelist
        self.next = 0

    def display_next(self, text=""):
        """ Display the next file in the list """
        if self.next >= len(self.filelist):
            self.scan()
        if not self.filelist:
            self.display.clear()
            if text:
                self.display.show_message(text)
            else:
                self.display.show_message("No pictures available!")
            self.display.apply()
        else:
            filename = self.filelist[self.next]
            self.next += 1
            self.display.clear()
            self.display.show_picture(filename)
            if text:
                self.display.show_message(text)
            self.display.apply()
            self.time_before_next = self.display_time

    def monitorEvents(self):
        """ Monitor the Slideshow events """
        while not self.quitting:
            self.handle_event(pygame.event.wait())

    def run(self):
        """ Main loop """
        while not self.quitting:
            if not self._queue.empty():
                self.display.show_message(
                    self._queue.get(), transparency=False)
                self.display.apply()
            self.display_next()
            while self.time_before_next > 0 and self.scrolling and not self.quitting:
                sleep(self.step)
                self.time_before_next -= self.step

    def handle_event(self, event):
        """ Handle events of the GUI"""
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            self.handle_clic(pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key_pressed(event.key)

    def get_size(self):
        """ Getter for the size of the display """
        return self.display.size

    def handle_key_pressed(self, key):
        """ Handle a pressed key """
        if key == pygame.constants.K_q:
            self._teardown()

    def handle_clic(self, pos):
        """ Handle a clic or a touch on the screen """
        # TODO

    def _teardown(self):
        """ Display closing method """
        self.quitting = True
        self.display.teardown()


#################
### Functions ###
#################


def parse_args():
    """
    Helper function that parses the command-line arguments
    """
    parser = argparse.ArgumentParser(
        description='Remote control for the photobooth')
    parser.add_argument(
        '--path', type=str, help='path to the pictures', required=True)
    parser.add_argument(
        '--size',
        type=int,
        nargs=2,
        help='size of the display',
        default=(1920, 1080))
    parser.add_argument(
        '--port',
        type=int,
        nargs=1,
        help='port on which to listen for incoming TCP connections',
        default=5817)
    parser.add_argument(
        '--address',
        type=str,
        help='address on which to bind the socket',
        default='localhost')
    parser.add_argument(
        '--time', type=int, help='slideshow frequency', default=1)
    args = parser.parse_args()
    return args


def main():
    """
    Main function
    """
    # Parse the args
    args = parse_args()

    queue = Queue()

    # Init the TCP server
    TCPServer.allow_reuse_address = True
    server = PhotoServer(address=args.address, port=args.port, queue=queue)
    server_process = Process(target=server.serve_forever)
    server_process.daemon = True
    server_process.start()

    # Start the slideshow
    slideshow = Slideshow(
        size=tuple(args.size),
        time=args.time,
        path=args.path,
        queue=queue,
        recursive=True)
    slideshow.run()

    server_process.terminate()
    return 0


if __name__ == "__main__":
    exit(main())
