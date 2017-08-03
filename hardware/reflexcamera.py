# -*- coding: utf-8 -*-
"""Module that contains the definition of the reflex camera"""

from datetime import datetime
from os.path import join
import gphoto2 as gp

from .camera import Camera


class ReflexCam(Camera):
    """ REFLEX Camera """

    def __init__(self):
        """ Initialization of the camera """
        gp.check_result(gp.use_python_logging())
        self.context = gp.gp_context_new()
        self.camera = gp.check_result(gp.gp_camera_new())
        gp.check_result(gp.gp_camera_init(self.camera, self.context))

    def prepare_camera(self):
        """ Prepare the camera for the picture """

    def take_picture(self, path, basename):
        """ Take a picture with the camera """
        # TODO To review...
        print('Capturing image')
        file_path = gp.check_result(gp.gp_camera_capture(
                                    self.camera, gp.GP_CAPTURE_IMAGE, self.context))
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.camera, path, basename,
            gp.GP_FILE_TYPE_NORMAL, context))  # TODO define context ??
        gp.check_result(gp.gp_file_save(camera_file, target))
        new_name = join(path, datetime.now().strftime(basename))
        return new_name

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """
        gp.check_result(gp.gp_camera_exit(self.camera, self.context))
