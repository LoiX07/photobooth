#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote control module for the photobooth project
"""

import argparse
from bisect import bisect
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

    def __init__(self, **kwargs):
        self.directory = kwargs.get('path')
        self.recursive = kwargs.get('recursive')
        self.filelist = []
        self.scan()
        self.size = kwargs.get('size')
        self.display = GUIModule("Slideshow",
                                 self.size, kwargs.get('fullscreen'))
        self.display_time = kwargs.get('time')
        self.next = 0
        self.remove = {
            'enabled': False,
            'index': -1,
            'pos': (375, 430),
            'size': (50, 50)
        }
        self.time_before_next = self.display_time
        self.scrolling = True
        self.quitting = False
        self.click_x = -1
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

        self.filelist = sorted(self.filelist)
        log.debug("Found the following files during the scan: %s",
                  str(self.filelist))
        self.next = 0

    def display_next(self, text=""):
        """ Display the next file in the list """
        log.debug("Displaying next picture")
        if self.next >= len(self.filelist):
            self.next = 0
        if not self.filelist:
            self.display.clear()
            if text:
                self.display.show_message(text)
            else:
                self.display.show_message("No pictures available!")
            self.display.apply()
            return None
        else:
            filename = self.filelist[self.next]
            self.next += 1
            self.display.clear()
            self.display.show_picture(filename)
            if text:
                self.display.show_message(text)
            self.display.apply()
            self.time_before_next = self.display_time
            log.debug("Next picture index is %s", str(self.next))
            log.debug("New picture name is %s", filename)
            return filename

    def display_prev(self, text=""):
        """ Display the previous file in the list """
        log.debug("Displaying prev picture")
        if self.next < 0:
            self.next = len(self.filelist) - 1
        if not self.filelist:
            self.display.clear()
            if text:
                self.display.show_message(text)
            else:
                self.display.show_message("No pictures available!")
            self.display.apply()
            return None
        else:
            filename = self.filelist[self.next]
            self.next -= 1
            self.display.clear()
            self.display.show_picture(filename)
            if text:
                self.display.show_message(text)
            self.display.apply()
            self.time_before_next = self.display_time
            log.debug("Next picture index is %s", str(self.next))
            log.debug("New picture name is %s", filename)
            return filename

    def _monitor_events(self):
        """ Monitor the Slideshow events """
        while not self.quitting:
            self.handle_event(pygame.event.wait())

    def run(self):
        """ Main loop """
        while not self.quitting:
            picture = self.display_next()
            log.debug('Displaying picture %s', picture)
            while self.time_before_next > 0 and self.scrolling and not self.quitting:
                # when a new messages arrives, we check whether it is a valid
                # file
                if not self._queue.empty():
                    self.deal_with_new_picture(picture)
                sleep(self.step)
                self.time_before_next -= self.step

    def deal_with_new_picture(self, picture):
        """Function that handles incoming pictures"""
        new_picture = os.path.join(self.directory,
                                   self._queue.get())
        log.debug('Trying to add new picture %s to the file list',
                  new_picture)
        # we check whether the new picture really exists
        if os.path.exists(new_picture):
            # just in case we discard any previous clickdown event
            self.click_x = -1
            # we add the new picture at the end of the list
            self.remove['index'] = bisect(self.filelist, new_picture)
            self.filelist.insert(self.remove['index'], new_picture)
            log.debug('File list is now: %s', str(self.filelist))
            # now we display the picture during 15s
            self.display.show_picture(new_picture)
            self.remove['enabled'] = True
            log.debug('The remove button is now enabled')
            self.remove['size'] = self.display.show_picture(
                "trash.jpg", self.remove["size"], self.remove['pos'], alpha=255)
            log.debug('Size of the display button is %s', self.remove["size"])
            self.display.apply()
            for _ in range(0, 150):
                sleep(self.step)
                if not self.remove['enabled']:
                    break
            self.remove['enabled'] = False
            self.remove['index'] = -1
            log.debug('The remove button is now disabled')
            log.debug('Displaying picture %s', picture)
            self.display.clear()
            self.display.show_picture(picture)
            self.display.apply()

    def handle_event(self, event):
        """ Handle events of the GUI"""
        if event.type == pygame.MOUSEBUTTONUP:
            log.debug('Received a new event: %s', str(event))
            pos = pygame.mouse.get_pos()
            self.handle_mouseup(pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            log.debug('Received a new event: %s', str(event))
            pos = pygame.mouse.get_pos()
            self.handle_mousedown(pos)
        elif event.type == pygame.KEYDOWN:
            log.debug('Received a new event: %s', str(event))
            self.handle_key_pressed(event.key)

    def get_size(self):
        """ Getter for the size of the display """
        return self.display.size

    def handle_key_pressed(self, key):
        """ Handle a pressed key """
        if key == pygame.constants.K_q:
            self._teardown()

    def handle_mouseup(self, pos):
        """ Handle a clic (mouseup) or a touch on the screen """
        # we check whether the remove button is enabled and
        # it is a click within the remove button
        if self.remove['enabled'] and self.remove['pos'][0] <= pos[0] and pos[0] <= self.remove['pos'][0] + \
                self.remove['size'][0] and self.remove['pos'][1] <= pos[1] and pos[1] <= self.remove['pos'][1] + self.remove['size'][1]:
            log.debug('Click on the remove button')
            log.debug('Removing the picture %s',
                      self.filelist[self.remove['index']])
            os.remove(self.filelist[self.remove['index']])
            del self.filelist[self.remove['index']]
            self.remove['index'] = -1
            self.remove['enabled'] = False
            return
        # if the remove button is disabled and we registered we mouseup
        # beforehand
        if not self.remove['enabled'] and self.click_x != -1:
            # if the click is within the rightmost 10th of the screen
            # or we swiped toward the right direction for more than 1/10th
            # of the screen width
            if (self.size[0] - pos[0]) <= (self.size[0] /
                                           10) or (pos[0] - self.click_x) >= (self.size[0] / 10):
                log.debug("Detecting a swipe right event")
                # we reset the click variable
                self.click_x = -1
                # and we display the next picture
                self.display_next()
                return
            # if the click is within the leftmost 20th of the screen
            # or we swiped toward the left direction for more than 1/10th
            # of the screen width
            elif pos[0] <= (self.size[0] / 10) or (self.click_x - pos[0]) >= (self.size[0] / 10):
                log.debug("Detecting a swipe left event")
                # we reset the click variable
                self.click_x = -1
                # and we display the previous picture
                self.display_prev()
                return
            # otherwise we ignore the click
            # and reset the previous position
            else:
                self.click_x = -1
                return

    def handle_mousedown(self, pos):
        """ Handle a click (mouse down) on the screen """
        # if the remove button is disabled, we register the x coordinates of
        # the click
        if not self.remove['enabled']:
            self.click_x = pos[0]

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
