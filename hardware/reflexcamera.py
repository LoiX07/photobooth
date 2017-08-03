# -*- coding: utf-8 -*-
"""Module that contains the definition of the reflex camera"""

from datetime import datetime

import logging
import os
import gphoto2 as gp

from .camera import Camera

if 'PHOTO_LOG' in globals():
    log = PHOTO_LOG
else:
    log = logging.getLogger("REFLEXCAM_LOG")

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

    def take_picture(self, path, name):
        """ Take a picture with the camera """
        
        # Ensure directory exists or create it
        if (not os.path.exists(path)) or (not os.path.isdir(path)):
            log.debug("Creating the directory : " + path)
            os.makedirs(path)
        
        # TODO To review...

        print('Capturing image')
        try:
            file_path = gp.check_result(gp.gp_camera_capture(
                                        self.camera, gp.GP_CAPTURE_IMAGE, self.context))
        except:
            return
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.camera, file_path.folder, file_path.name,
            gp.GP_FILE_TYPE_NORMAL, self.context))  # TODO define context ??
        target = os.path.join(path, name)
        gp.check_result(gp.gp_file_save(camera_file, target))
        return target

    def close(self):
        """ Free the camera ressources to avoid GPU memory leaks """
        gp.check_result(gp.gp_camera_exit(self.camera, self.context))
