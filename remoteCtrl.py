import os
import sys
from time import sleep,clock

##################
### Parameters ###
##################
picture_path = datetime.now().strftime("%Y-%m-%d_Photomaton")
picture_suffix = "_Photomaton.jpeg"

###############
### Classes ###
###############
class PictureList:
    """A simple helper class.
    It provides the filenames for the assembled pictures and keeps count
    of taken and previously existing pictures."""

    def __init__(self,path,suffix):
        """Initialize filenames to the given basename and search for existing files.
        Set the counter accordingly"""

        # Set basename and suffix
        self.path = path
        self.suffix = suffix

        # Ensure directory exists
        dirname = os.path.dirname(self.path)

        # Find existing files
        self.pictures = find_pictures()
        
        # Sort picture
        self.pictures.sort()

    def find_pictures(self):
        """ Find pictures """
        return glob(self.path + "*" + self.suffix)

    def get_pictures_list(self):
        """ Get the sorted list of picture """
        return self.pictures
