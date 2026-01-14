import pygame
from utils import *

class Button:
    def __init__(self, texture: pygame.Surface, pos: Vec, top_left: Vec, size: Vec, action):
        self.texture = texture
        self.pos = pos
        self.top_left = top_left
        self.size = size
        self.action = action

    def try_click(self, mouse_pos: Vec, run_action: bool):
        flag = (mouse_pos.x >= self.pos) and (mouse_pos.y >= self.pos) and (mouse_pos.x < self.pos + self.size) and (mouse_pos.y < self.pos + self.size)
        if (flag and run_action): self.click()
        return flag

    def click(self):
        self.action()

class Menu:
    pass