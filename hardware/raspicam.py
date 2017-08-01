# -*- coding: utf-8 -*-
"""Module that contains the definition of the rasp pi camera"""

from datetime import datetime
from os.path import join
from time import sleep

from picamera import PiCamera

from .camera import Camera

class RaspiCam(Camera):
    """ Camera Raspberry """

    def __init__(self, **kwargs):
        """ Initialization of the camera """
        self.camera = PiCamera()
        version = kwargs.get('version', 0)
        # Configuration
        if version == 1:
            self.camera.resolution = (1024, 768)
        elif version == 2:
            self.camera.resolution = (3280, 2464)
        else:
            raise ValueError('Unsupported raspberry pi camera version')
        # Camera warm-up
        self.camera.start_preview()
        sleep(2)

    def prepare_camera(self):
        """ Camera preparation """

    def take_picture(self, path, basename):
        """ Take a picture with the camera """
        new_name = join(path, datetime.now().strftime(basename))
        self.camera.capture(new_name)
        return new_name

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """
        self.camera.stop_preview()
        self.camera.close()
