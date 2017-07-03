import os
import sys
import pygame
from time import sleep,clock

##################
### Parameters ###
##################
picture_path = datetime.now().strftime("%Y-%m-%d_Photomaton")
picture_suffix = "_Photomaton.jpeg"

#####################
### Configuration ###
#####################
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

###############
### Classes ###
###############
class PictureList:

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

class GUI_Display:
    """ GUI Display using PyGame """

    def __init__(self,name,size):
        # Call init routines
        pygame.init()

        # Window name
        pygame.display.set_caption(name)

        # Hide mouse cursor
        pygame.mouse.set_visible(False)

        # Store screen and size
        self.size = size
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

        # Clear screen
        self.clear()
        self.apply()

    def clear(self, color=(46,52,54)):
        self.screen.fill(color)
        self.surface_list = []

    def apply(self):
        for surface in self.surface_list:
            self.screen.blit(surface[0], surface[1])
        pygame.display.update()

    def get_size(self):
        return self.size

    def trigger_event(self, event_channel):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, channel=event_channel))

    def show_picture(self, filename, size=(0,0), offset=(0,0), flip=False):
        # Use window size if none given
        if size == (0,0):
            size = self.size
        try:
            # Load image from file
            image = pygame.image.load(filename)
        except pygame.error as e:
            raise GuiException("ERROR: Can't open image '" + filename + "': " + e.message)
        # Extract image size and determine scaling
        image_size = image.get_rect().size
        image_scale = min([min(a,b)/b for a,b in zip(size, image_size)])
        # New image size
        new_size = [int(a*image_scale) for a in image_size]
        # Update offset
        offset = tuple(a+int((b-c)/2) for a,b,c in zip(offset, size, new_size))
        # Apply scaling and display picture
        image = pygame.transform.scale(image, new_size).convert()
        # Create surface and blit the image to it
        surface = pygame.Surface(new_size)
        surface.blit(image, (0,0))
        if flip:
            surface = pygame.transform.flip(surface, True, False)
        self.surface_list.append((surface, offset))

    def show_message(self, msg, color=(0,0,0), bg=(230,230,230), transparency=True, outline=(245,245,245)):
        # Choose font
        font = pygame.font.Font(None, 144)
        # Wrap and render text
        wrapped_text, text_height = self.wrap_text(msg, font, self.size)
        rendered_text = self.render_text(wrapped_text, text_height, 1, 1, font, color, bg, transparency, outline)

        self.surface_list.append((rendered_text, (0,0)))

    def show_button(self, text, pos, size=(0,0), color=(230,230,230), bg=(0,0,0), transparency=True, outline=(230,230,230)):
        # Choose font
        font = pygame.font.Font(None, 72)
        text_size = font.size(text)
        if size == (0,0):
            size = (text_size[0] + 4, text_size[1] + 4)
        offset = ( (size[0] - text_size[0]) // 2, (size[1] - text_size[1]) // 2 )

        # Create Surface object and fill it with the given background
        surface = pygame.Surface(self.size) 
        surface.fill(bg) 

        # Render text
        rendered_text = font.render(text, 1, color)
        surface.blit(rendered_text, pos)

        # Render outline
        pygame.draw.rect(surface, outline, (pos[0]-offset[0], pos[1]-offset[0], size[0], size[1]), 1)

        # Make background color transparent
        if transparency:
            surface.set_colorkey(bg)

        self.surface_list.append((surface, (0,0)))

    def wrap_text(self, msg, font, size):
        final_lines = []                   # resulting wrapped text
        requested_lines = msg.splitlines() # wrap input along line breaks
        accumulated_height = 0             # accumulated height

        # Form a series of lines
        for requested_line in requested_lines:
            # Handle too long lines
            if font.size(requested_line)[0] > size[0]:
                # Split at white spaces
                words = requested_line.split(' ')
                # if any of our words are too long to fit, trim them
                for word in words:
                    while font.size(word)[0] >= size[0]:
                        word = word[:-1]
                # Start a new line
                accumulated_line = ""
                # Put words on the line as long as they fit
                for word in words:
                    test_line = accumulated_line + word + " "
                    # Build the line while the words fit.   
                    if font.size(test_line)[0] < size[0]:
                        accumulated_line = test_line 
                    else:
                        # Start a new line
                        line_height = font.size(accumulated_line)[1]
                        if accumulated_height + line_height > size[1]:
                            break
                        else:
                            accumulated_height += line_height
                            final_lines.append(accumulated_line)
                            accumulated_line = word + " " 
                # Finish requested_line
                line_height = font.size(accumulated_line)[1]
                if accumulated_height + line_height > size[1]:
                    break
                else:
                    accumulated_height += line_height
                    final_lines.append(accumulated_line)
            # Line fits as it is
            else:
                accumulated_height += font.size(requested_line)[1] 
                final_lines.append(requested_line)

        # Check height of wrapped text
        if accumulated_height >= size[1]:
            raise GuiException("Wrapped text is too high to fit.")

        return final_lines, accumulated_height

    def render_text(self, text, text_height, valign, halign, font, color, bg, transparency, outline):
        # Determine vertical position
        if valign == 0:     # top aligned
            voffset = 0
        elif valign == 1:   # centered
            voffset = int((self.size[1] - text_height) / 2)
        elif valign == 2:   # bottom aligned
            voffset = self.size[1] - text_height
        else:
            raise GuiException("Invalid valign argument: " + str(valign))

        # Create Surface object and fill it with the given background
        surface = pygame.Surface(self.size) 
        surface.fill(bg) 

        # Blit one line after another
        accumulated_height = 0 
        for line in text: 
            maintext = font.render(line, 1, color)
            shadow = font.render(line, 1, outline)
            if halign == 0:     # left aligned
                hoffset = 0
            elif halign == 1:   # centered
                hoffset = (self.size[0] - maintext.get_width()) / 2
            elif halign == 2:   # right aligned
                hoffset = rect.width - maintext.get_width()
            else:
                raise GuiException("Invalid halign argument: " + str(justification))
            pos = (hoffset, voffset + accumulated_height)
            # Outline
            surface.blit(shadow, (pos[0]-1,pos[1]-1))
            surface.blit(shadow, (pos[0]-1,pos[1]+1))
            surface.blit(shadow, (pos[0]+1,pos[1]-1))
            surface.blit(shadow, (pos[0]+1,pos[1]+1))
            # Text
            surface.blit(maintext, pos)
            accumulated_height += font.size(line)[1]

        # Make background color transparent
        if transparency:
            surface.set_colorkey(bg)

        # Return the rendered surface
        return surface

    def wait_for_event(self):
        # Repeat until a relevant event happened
        while True:
            # Discard all input that happened before entering the loop
            pygame.event.get()

            # Wait for event
            event = pygame.event.wait()

            # Return the event 
            return event

    def teardown(self):
        pygame.quit()
        
class Slideshow:
    def __init__(self, display_size, display_time, directory, recursive = True):
        self.directory    = directory
        self.recursive    = recursive
        self.filelist     = []
        self.display      = GuiModule("Slideshow", display_size)
        self.display_time = display_time
        self.next         = 0
        self.time_before_next = display_time

    def scan(self):
        filelist = []

        if self.recursive:
            # Recursively walk all entries in the directory
            for root, dirnames, filenames in os.walk(self.directory, followlinks=True):
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

    def handle_event(self, event):
        """ Events handling of the slideshow """
        if (event.type is pygame.MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            self.andle_touch(pos)
        else:
            pass

    def handle_touch(self, pos):
        """ Handle a touch on the screen """
        # TODO

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
        """ Monitoring of the Slideshow events """
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            sleep(0.1)

    def run(self):
        while True:
            self.display_next()
            while self.time_before_next > 0:
                sleep(self.step)
                self.time_before_next -= self.step
            self.display_next()

    def teardown(self):
        self.display.teardown()
        exit(0)
def main():
    # Start the slideshow
    slideshow = Slideshow(display_size, display_time, slideshow_directory, True)
    slideshow.run()

    return 0
if __name__ == "__main__":
    exit(main())
