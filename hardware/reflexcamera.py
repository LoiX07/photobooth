# -*- coding: utf-8 -*-
"""Module that contains the definition of the reflex camera"""

import gphoto2 as gp

from .camera import Camera


class ReflexCam(Camera):
    """ REFLEX Camera """

    def __init__(self):
        """ Initialization of the camera """
        gp.check_result(gp.use_python_logging())
        context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera, context))

    def prepare_camera(self):
        """ Prepare the camera for the picture """

    def take_picture(self, path, basename):
        """ Take a picture with the camera """

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """
