#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote control module for the photobooth project
"""

import argparse
from bisect import insort
import logging
import os
import threading
from datetime import datetime
from multiprocessing import Process, Queue
from socketserver import TCPServer
from time import sleep

import pygame

from tools.gui import GUIModule
from tools.tcp import PhotoServer
from tools.remote_log import REMOTE_LOG as log

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
        self.scan()
        self.display = GUIModule("Slideshow",
                                 kwargs.get('size'), kwargs.get('fullscreen'))
        self.display_time = kwargs.get('time')
        self.next = 0
        self.time_before_next = self.display_time
        self.scrolling = True
        self.quitting = False
        self.step = 0.1
        self._queue = kwargs.get('queue')
        self._monitoring_thread = threading.Thread(target=self._monitor_events)
        self._monitoring_thread.start()  # Run

    def scan(self):
        """ Scan the photo dir in order to get a list of files """
        if self.recursive:
            # Recursively walk all entries in the directory
            for root, _, filenames in os.walk(
                    self.directory, followlinks=True):
                for filename in filenames:
                    self.filelist.append(os.path.join(root, filename))
        else:
            # Add all entries in the directory
            for item in os.listdir(self.directory):
                filename = os.path.join(self.directory, item)
                if os.path.isfile(filename):
                    self.filelist.append(filename)

        sorted(self.filelist)
        log.debug("Found the following files during the scan: %s",
                  str(self.filelist))
        self.next = 0

    def display_next(self, text=""):
        """ Display the next file in the list """
        if self.next >= len(self.filelist):
            #TODO: what should we do about new files? Maybe it would be better
            # to do the scan once and to just insert them into an ordered list
            self.next = 0
            #self.scan()
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

    def _monitor_events(self):
        """ Monitor the Slideshow events """
        while not self.quitting:
            self.handle_event(pygame.event.wait())

    def run(self):
        """ Main loop """
        while not self.quitting:
            self.display_next()
            while self.time_before_next > 0 and self.scrolling and not self.quitting:
                # when a new messages arrives, we check whether it is a valid file
                if not self._queue.empty():
                    new_picture = os.path.join(self.directory,
                                               self._queue.get())
                    log.debug('Trying to add new picture %s to the file list',
                              new_picture)
                    if os.path.exists(new_picture):
                        # if so, we add it at the end of the list
                        insort(self.filelist, new_picture)
                        log.debug('File list is now: %s', str(self.filelist))
                        # TODO: and we launch the display of the new picture
                sleep(self.step)
                self.time_before_next -= self.step

    def handle_event(self, event):
        """ Handle events of the GUI"""
        log.debug('Received a new event: %s', str(event))
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
        help='port on which to listen for incoming TCP connections',
        default=5817)
    parser.add_argument(
        '--address',
        type=str,
        help='address on which to bind the socket',
        default='localhost')
    parser.add_argument(
        '--time', type=int, help='slideshow frequency', default=1)
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        help='verbose logging')
    parser.add_argument(
        '--windowed',
        dest='fullscreen',
        action='store_false',
        help='windowed mode')
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
        fullscreen=args.fullscreen,
        recursive=True)
    slideshow.run()

    server_process.terminate()
    return 0


if __name__ == "__main__":
    exit(main())
