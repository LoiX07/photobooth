# -*- coding: utf-8 -*-

"""
GUI-related classes
"""

import pygame

class GuiException(Exception):
    """
    Custom exception class to handle GUI class errors
    """

class GUIModule:
    """ GUI Display using PyGame """

    def __init__(self, name, size):
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

    def clear(self, color=(46, 52, 54)):
        """
        Clears the screen
        """
        self.screen.fill(color)
        self.surface_list = []

    def apply(self):
        """
        Updates the display
        """
        for surface in self.surface_list:
            self.screen.blit(surface[0], surface[1])
        pygame.display.update()

    def get_size(self):
        """
        Getter for the size of the display
        """
        return self.size

    def show_picture(self, filename, size=(0, 0), offset=(0, 0), flip=False):
        """
        Display of a picture
        """
        # Use window size if none given
        if size == (0, 0):
            size = self.size
        try:
            # Load image from file
            image = pygame.image.load(filename)
        except pygame.error as exc:
            raise GuiException("ERROR: Can't open image '" + filename + "': " +
                               exc.message)
        # Extract image size and determine scaling
        image_size = image.get_rect().size
        image_scale = min([min(a, b) / b for a, b in zip(size, image_size)])
        # New image size
        new_size = [int(a * image_scale) for a in image_size]
        # Update offset
        offset = tuple(a + int((b - c) / 2)
                       for a, b, c in zip(offset, size, new_size))
        # Apply scaling and display picture
        image = pygame.transform.scale(image, new_size).convert()
        # Create surface and blit the image to it
        surface = pygame.Surface(new_size)
        surface.blit(image, (0, 0))
        if flip:
            surface = pygame.transform.flip(surface, True, False)
        self.surface_list.append((surface, offset))

    def show_message(self,
                     msg,
                     color=(0, 0, 0),
                     background=(230, 230, 230),
                     transparency=True,
                     outline=(245, 245, 245)):
        # Choose font
        font = pygame.font.Font(None, 144)
        # Wrap and render text
        wrapped_text, text_height = self.wrap_text(msg, font, self.size)
        rendered_text = self.render_text(wrapped_text, text_height, 1, 1, font,
                                         color, background, transparency,
                                         outline)

        self.surface_list.append((rendered_text, (0, 0)))

    def show_button(self,
                    text,
                    pos,
                    size=(0, 0),
                    color=(230, 230, 230),
                    background=(0, 0, 0),
                    transparency=True,
                    outline=(230, 230, 230)):
        # Choose font
        font = pygame.font.Font(None, 72)
        text_size = font.size(text)
        if size == (0, 0):
            size = (text_size[0] + 4, text_size[1] + 4)
        offset = ((size[0] - text_size[0]) // 2, (size[1] - text_size[1]) // 2)

        # Create Surface object and fill it with the given background
        surface = pygame.Surface(self.size)
        surface.fill(background)

        # Render text
        rendered_text = font.render(text, 1, color)
        surface.blit(rendered_text, pos)

        # Render outline
        pygame.draw.rect(surface, outline,
                         (pos[0] - offset[0], pos[1] - offset[0], size[0],
                          size[1]), 1)

        # Make background color transparent
        if transparency:
            surface.set_colorkey(background)

        self.surface_list.append((surface, (0, 0)))

    def wrap_text(self, msg, font, size):
        final_lines = []  # resulting wrapped text
        requested_lines = msg.splitlines()  # wrap input along line breaks
        accumulated_height = 0  # accumulated height

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

    def render_text(self, text, text_height, valign, halign, font, color,
                    background, transparency, outline):
        # Determine vertical position
        if valign == 0:  # top aligned
            voffset = 0
        elif valign == 1:  # centered
            voffset = int((self.size[1] - text_height) / 2)
        elif valign == 2:  # bottom aligned
            voffset = self.size[1] - text_height
        else:
            raise GuiException("Invalid valign argument: " + str(valign))

        # Create Surface object and fill it with the given background
        surface = pygame.Surface(self.size)
        surface.fill(background)

        # Blit one line after another
        accumulated_height = 0
        for line in text:
            maintext = font.render(line, 1, color)
            shadow = font.render(line, 1, outline)
            if halign == 0:  # left aligned
                hoffset = 0
            elif halign == 1:  # centered
                hoffset = (self.size[0] - maintext.get_width()) / 2
            elif halign == 2:  # right aligned
                hoffset = rect.width - maintext.get_width()
            else:
                #TODO: where the f*ck does justification come from?
                raise GuiException("Invalid halign argument: " +
                                   str(justification))
            pos = (hoffset, voffset + accumulated_height)
            # Outline
            surface.blit(shadow, (pos[0] - 1, pos[1] - 1))
            surface.blit(shadow, (pos[0] - 1, pos[1] + 1))
            surface.blit(shadow, (pos[0] + 1, pos[1] - 1))
            surface.blit(shadow, (pos[0] + 1, pos[1] + 1))
            # Text
            surface.blit(maintext, pos)
            accumulated_height += font.size(line)[1]

        # Make background color transparent
        if transparency:
            surface.set_colorkey(background)

        # Return the rendered surface
        return surface

    def teardown(self):
        pygame.quit()
