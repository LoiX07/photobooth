# -*- coding: utf-8 -*-
"""
Utils: list of pictures
"""

from glob import glob
import os

class PictureList:
    """
    Class used to construct a list of pictures
    """

    def __init__(self, path, suffix):
        """Initialize filenames to the given basename and search for existing files.
        Set the counter accordingly"""

        # Set basename and suffix
        self.path = path
        self.suffix = suffix
        # Ensure directory exists
        if (not os.path.exists(self.path)) or (not os.path.isdir(self.path)):
            raise Exception("Invalid path")

        # Find existing files
        self.pictures = self.find_pictures()

        # Sort picture
        self.pictures.sort()

    def find_pictures(self):
        """ Find pictures """
        return glob(self.path + "*" + self.suffix)

    def get_pictures_list(self):
        """ Get the sorted list of picture """
        return self.pictures
