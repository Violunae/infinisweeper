import pygame
import game
import draw
from utils import *
from globals import Globals
from sprites import Sprites

class App:
    def run(self):
        running = True
        dragging = False
        last_mouse_pos = Vec(0, 0)
        slot = -1

        self.map = game.Map(slot)
        clock = pygame.time.Clock()

        self.menu = Menu(self)

        while running:
            for event in pygame.event.get():
                if (self.menu.active) :
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3):
                            self.menu.click(Vec(*event.pos), True)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 2:
                            dragging = True
                            last_mouse_pos = Vec(*event.pos)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button in (1, 3):
                            mouse_pos = Vec(*event.pos)
                            global_pos = self.map.camera.reverse_transform(mouse_pos).floor()
                            if event.button == 1:
                                self.map.open_cell(global_pos)
                            else:
                                self.map.flag_cell(global_pos)
                        elif event.button == 2:
                            dragging = False

                    elif event.type == pygame.MOUSEWHEEL:
                        self.map.camera.zoom = max(8.0, min(64.0, map.camera.zoom + event.y))

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        Globals.dark_mode = not Globals.dark_mode
                    elif event.key == pygame.K_DELETE:
                        self.map.delete()
                        self.map = game.Map(slot)
                    elif event.key == pygame.K_RETURN:
                        slot = slot + 1
                        self.map.save()
                        self.map = game.Map(slot)
                    elif event.key == pygame.K_ESCAPE:
                        self.map.save()
                        running = False
                if event.type == pygame.QUIT:
                    self.map.save()
                    running = False

            current_mouse_pos = Vec(*pygame.mouse.get_pos())

            pointer = True
            if (self.menu.active):
                pointer = self.menu.click(current_mouse_pos, False)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if (pointer) else pygame.SYSTEM_CURSOR_ARROW)

            if dragging:
                delta = current_mouse_pos - last_mouse_pos
                
                self.map.camera.pos.x -= delta.x / self.map.camera.zoom
                self.map.camera.pos.y -= delta.y / self.map.camera.zoom

                last_mouse_pos = current_mouse_pos

            self.map.update()

            draw.clear_screen((101, 119, 128))
            self.map.draw()
            self.menu.draw()
            pygame.display.update()

            clock.tick(30)

class Button:
    def __init__(self, pos: Vec, top_left: Vec, size: Vec, action):
        self.pos = pos
        self.top_left = top_left
        self.size = size
        self.action = action

    def click(self, mouse_pos: Vec, run_action: bool):
        mouse_pos *= 0.5
        flag = (mouse_pos.x >= self.pos.x) and (mouse_pos.y >= self.pos.y) and (mouse_pos.x < self.pos.x + self.size.x) and (mouse_pos.y < self.pos.y + self.size.y)
        if (flag and run_action): self.activate()
        return flag

    def activate(self):
        self.action()

    def draw(self):
        Menu.draw_ui(self.pos, self.top_left, self.size)

class Menu:

    @staticmethod
    def draw_ui(pos: Vec, top_left: Vec, size: Vec):
        draw.draw_texture(None, Sprites.gui, pos * 2, top_left + Vec(0, 352 if (Globals.dark_mode) else 0), size)

    def __init__(self, app: App):
        self.app = app
        self.buttons = []
        self.active = True
        self.fill()

    def add_button(self, button: Button):
        self.buttons.append(button)

    def click(self, mouse_pos: Vec, run_action: bool):
        for b in self.buttons:
            if (b.click(mouse_pos, run_action)): return True
        return False
    
    def draw(self):
        if (not(self.active)): return

        draw.draw_fade((255, 255, 255, 127) if (Globals.dark_mode) else (0, 0, 0, 127))

        Menu.draw_ui(Vec(130, 138), Vec(0, 112), Vec(240, 224))

        for i in range(0, 3):
            Menu.draw_ui(Vec(142, 150 + (i * 48)), Vec(12, 60), Vec(216, 40))

        for b in self.buttons:
            b.draw()
    
    def fill(self):
        def start_slot(slot):
            print(slot)
            self.app.map = game.Map(slot)
            self.active = False

        for i in range(0, 3):
            self.add_button(Button(Vec(146, 154 + (i * 48)), Vec(0, 0), Vec(34, 34), lambda slot=i: start_slot(slot)))