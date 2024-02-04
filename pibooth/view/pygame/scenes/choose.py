# -*- coding: utf-8 -*-

from pygame_imslider import ImSlider, ImSliderRenderer, STYPE_LOOP

from pibooth import evts
from pibooth import pictures
from pibooth.language import get_translated_text
from pibooth.view.pygame.window import PygameScene
from pibooth.view.pygame.sprites import LeftArrowSprite, RightArrowSprite, TextSprite


class Renderer(ImSliderRenderer):

    def __init__(self, scene):
        super().__init__(arrow_color=((182, 183, 184), (124, 183, 62)),
                         dot_color=((182, 183, 184), (124, 183, 62)),
                         slide_color=None,
                         selection_color=(124, 183, 62),
                         selection_page_color=(180, 220, 130),
                         background_color=None)
        self.scene = scene

    @property
    def arrow_color(self):
        return (self.scene.text_color, tuple(int(c * 0.5) for c in self.scene.text_color))

    @arrow_color.setter
    def arrow_color(self, color):
        pass

    @property
    def dot_color(self):
        return self.arrow_color

    @dot_color.setter
    def dot_color(self, color):
        pass

    @property
    def slide_color(self):
        return self.scene.background.get_color(0.7)

    @slide_color.setter
    def slide_color(self, color):
        pass

    def draw_background(self, surface):
        surface.blit(self.scene.background.image, (0, 0), self.scene.slider.get_rect())


class ChooseScene(PygameScene):

    def __init__(self):
        super().__init__()
        self.choices = ()
        self.slider = ImSlider((200, 100), focus=False, renderer=Renderer(self), stype=STYPE_LOOP)
        self.text = TextSprite(self, get_translated_text('choose'))
        self.left_arrow = LeftArrowSprite(self)
        self.right_arrow = RightArrowSprite(self)

        self.right_arrow.set_skin('arrow_double.png')
        self.left_arrow.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_CAPTURE)
        self.right_arrow.on_pressed = lambda: evts.post(evts.EVT_PIBOOTH_PRINT)

    def resize(self, size):
        # Slider
        slider_width, slider_height = self.rect.width * 3 // 4, self.rect.height * 6 // 8
        x, y = (self.rect.width - slider_width) // 2, (self.rect.height - slider_height) // 2
        if self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            self.slider.set_arrows_visible(False)
        else:
            self.slider.set_arrows_visible(True)
        self.slider.set_position(x, y)
        self.slider.set_size(slider_width, slider_height)

        # Text
        self.text.set_text(get_translated_text('choose'))  # In case of text has changed
        if self.arrow_location == self.ARROW_TOP:
            self.text.set_rect(10, self.rect.bottom - y, self.rect.width - 20, y - 10)
        else:
            self.text.set_rect(10, 10, self.rect.width - 20, y - 10)

        # Left arrow
        size = (self.rect.height * 0.15, self.rect.height * 0.15)
        if self.arrow_location == self.ARROW_TOUCH:
            self.left_arrow.set_skin('touch_thumb.png')
            x = self.rect.right - size[0] - 10
        else:
            self.left_arrow.set_skin('arrow.png')
            x = self.rect.left + self.rect.width // 4 - size[0] // 2
        if self.arrow_location == self.ARROW_TOP:
            y = self.rect.top + 10
        else:
            y = self.rect.bottom - size[1] - 10
        self.left_arrow.set_rect(x, y, size[0], size[1])

        # Right arrow
        size = (self.rect.width * 0.1, self.rect.height * 0.1)
        if self.arrow_location == self.ARROW_TOUCH:
            self.right_arrow.hide()
        elif self.arrow_location in (self.ARROW_BOTTOM, self.ARROW_TOP):
            x = self.rect.right - self.rect.width // 4 - size[0] // 2
            if self.arrow_location == self.ARROW_TOP:
                y = self.rect.top + 10
            else:
                y = self.rect.bottom - size[1] - 10
            self.right_arrow.set_rect(x, y, size[0], size[1])

    def update(self, events):
        super().update(events)
        self.slider.update(events)

    def draw(self, surface, force=False):
        rects = super().draw(surface, force)
        rects += self.slider.draw(surface, force)
        return rects

    def next(self):
        """Display next possible layout.
        """
        self.slider.on_next()

    def set_choices(self, choices):
        """Set the list of possible number of captures.
        """
        if choices != self.choices:
            # Reload pictures
            self.choices = choices
            self.slider.load_images([pictures.get_layout_asset(
                c, self.background.get_color(), self.text_color) for c in choices])

    def get_selection(self):
        """Return curretly selected number of captures.
        """
        return self.choices[self.slider.get_index()]
