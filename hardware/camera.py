# -*- coding: utf-8 -*-

"""Module that contains the abstraction for a camera"""

from abc import ABCMeta, abstractmethod


class Camera(object):
    """ Metaclass for a camera (raspi or reflex) """
    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare_camera(self):
        """ Abstract method for camera initialization """
        pass

    @abstractmethod
    def take_picture(self, path, basename):
        """ Abstract method for taking pictures"""
        pass
