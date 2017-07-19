#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote control module for the photobooth project
"""

import os
import threading
from time import sleep
from datetime import datetime
import subprocess
import argparse
import pygame
from utils.gui import GUIModule

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

    def __init__(self, display_size, display_time, directory, recursive=True):
        self.directory = directory
        self.recursive = recursive
        self.filelist = []
        self.display = GUIModule("Slideshow", display_size)
        self.display_time = display_time
        self.next = 0
        self.time_before_next = display_time
        self.scrolling = True
        self.quitting = False
        self.step = 0.1
        self._monitoring_thread = threading.Thread(target=self.monitorEvents)
        self._monitoring_thread.start()  # Run

    def scan(self):
        filelist = []
        if self.recursive:
            # Recursively walk all entries in the directory
            for root, _, filenames in os.walk(self.directory, followlinks=True):
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


def sync_folders(source_directory, target_directory, wait_time):
    sleep(5)
    while True:
        print("[" + datetime.now().strftime("%H:%M:%S") + "] Sync " +
              source_directory + " --> " + target_directory)
        try:
            cmd = "rsync -rtu " + source_directory + " " + target_directory
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            print("ERROR executing '" + exc.cmd + "':\n" + exc.output)
        sleep(wait_time)


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
        '--time', type=int, help='slideshow frequency', default=1)
    args = parser.parse_args()
    return args


def main():
    """
    Main function
    """
    # Parse the args
    args = parse_args()
    display_size = tuple(args.size)
    display_time = args.time
    slideshow_directory = args.path

    # Start a thread for syncing files
    #if len(source_directory) > 0:
    #   thread.start_new_thread(sync_folders, (source_directory, slideshow_directory, sync_time) )

    # Start the slideshow
    slideshow = Slideshow(display_size, display_time, slideshow_directory,
                          True)
    slideshow.run()

    return 0


if __name__ == "__main__":
    exit(main())
