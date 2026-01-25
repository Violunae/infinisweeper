import draw
from globals import Globals

from utils import *

class Button:
    def __init__(self, pos: Vec, top_left: Vec, size: Vec, action):
        self.pos = pos
        self.top_left = top_left
        self.size = size
        self.action = action

    def click(self, mouse_pos: Vec, run_action: bool):
        flag = mouse_pos.in_rect(self.pos, self.size)
        if (flag and run_action): self.activate()
        return flag

    def activate(self):
        self.action()

    def draw(self, menu):
        menu.draw_ui(self.pos, self.top_left, self.size)

class Label:
    def __init__(self, pos: Vec, text: str, color, font):
        self.pos = pos
        self.text = text
        self.color = color
        self.font = font

    def draw(self, menu):
        draw.draw_text(self.pos, self.text, self.color, self.font)

class Menu:

    def __init__(self, app, renderer, top_left: Vec, size: Vec, active = True):
        self.app = app
        self.renderer = renderer
        self.top_left = top_left
        self.size = size
        self.active = active

        self.buttons = []
        self.labels = []

    def add_button(self, button: Button):
        self.buttons.append(button)

    def add_label(self, label: Label):
        self.labels.append(label)

    def click(self, mouse_pos: Vec, run_action: bool):
        mouse_pos *= 0.5

        if (not(self.active)): return None
        if (not(mouse_pos.in_rect(self.top_left, self.size))): return None

        for b in self.buttons:
            if (b.click(mouse_pos, run_action)): return True
        return False
    
    def draw(self):
        if (not(self.active)): return

        if (self.renderer != None):
            self.renderer(self)

        for b in self.buttons:
            b.draw(self)

        for l in self.labels:
            l.draw(self)

    def draw_ui(self, pos: Vec, top_left: Vec, size: Vec):
        draw.draw_texture(None, Globals.texture_gui, pos * 2, top_left + Vec(0, 448 if (Globals.dark_mode) else 0), size)