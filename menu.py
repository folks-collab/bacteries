import pygame 
import pygame_menu
from pygame_menu.themes import*


class Menu(pygame_menu.Menu):
    def __init__(self, screen, title):
        super().__init__(height=screen.get_height(), width=screen.get_width(), title=title, theme=THEME_DARK)
        self.screen = screen

    def flip(self, events):
        if self.is_enabled():
            self.update(events)
        if self.is_enabled():
            self.draw(self.screen)


        