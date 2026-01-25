import pygame
import game
import draw
import save
from utils import *
from globals import Globals
from sprites import Sprites

class App:
    def run(self):
        self.slot = -1
        self.running = True

        dragging = False
        last_mouse_pos = Vec(0, 0)

        self.map = game.Map(self.slot)
        clock = pygame.time.Clock()

        self.menu = self.create_menu()
        self.bar = self.create_bar()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 2:
                        dragging = True
                        last_mouse_pos = Vec(*event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button in (1, 3):
                        mouse_pos = Vec(*event.pos)

                        if (self.menu.click(Vec(*event.pos), True) != None): continue
                        if (self.bar.click(Vec(*event.pos), True) != None): continue

                        global_pos = self.map.camera.reverse_transform(mouse_pos).floor()
                        if event.button == 1:
                            self.map.open_cell(global_pos)
                        else:
                            self.map.flag_cell(global_pos)
                    elif event.button == 2:
                        dragging = False

                elif event.type == pygame.MOUSEWHEEL:
                    if (self.slot != -1):
                        self.map.camera.zoom = max(8.0, min(64.0, self.map.camera.zoom + event.y))

                elif event.type == pygame.QUIT:
                    self.map.save()
                    self.running = False

            current_mouse_pos = Vec(*pygame.mouse.get_pos())

            pointer_menu = self.menu.click(current_mouse_pos, False)
            pointer_bar = self.bar.click(current_mouse_pos, False)
            pointer = True
            if (pointer_menu != None): pointer = pointer_menu
            if (pointer_bar != None): pointer = pointer_bar
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
            self.bar.draw()
            pygame.display.update()

            clock.tick(30)

    def start_slot(self, slot):
        self.slot = slot
        self.map = game.Map.load(slot, True)
        self.menu.active = False
        self.bar.active = True
    
    def delete_slot(self, slot):
        save.delete_save(slot)
        self.menu = self.create_menu()

    def toggle_dark_mode(self):
        Globals.dark_mode = not Globals.dark_mode

    def quit(self):
        self.running = False

    def back(self):
        self.map.save()
        self.map = game.Map(-1)
        self.menu = self.create_menu()
        self.bar.active = False

    def create_menu(self):

        def _renderer(menu):
            draw.draw_fade((0, 0, 0, 127))

            logo_sway = math.sin(pygame.time.get_ticks() * 0.002) * 8
            Menu.draw_ui(Vec(99, 23 + logo_sway), Vec(0, 336), Vec(302, 102))

            Menu.draw_ui(Vec(130, 138), Vec(0, 112), Vec(240, 224))

            for i in range(0, 3):
                Menu.draw_ui(Vec(142, 150 + (i * 48)), Vec(12, 60), Vec(216, 40))

        menu = Menu(self, _renderer, Vec(0, 0), Vec(500, 500))

        for i in range(0, 3):
            map = game.Map.load(i, False)
            exists = map != None
            menu.add_button(Button(Vec(146, 154 + (i * 48)), Vec(0 if (exists) else 48, 0), Vec(34, 34), lambda slot=i: self.start_slot(slot)))
            if (exists):
                menu.add_button(Button(Vec(322, 154 + (i * 48)), Vec(96, 0), Vec(34, 34), lambda slot=i: self.delete_slot(slot)))

        menu.add_button(Button(Vec(146, 314), Vec(144, 0), Vec(34, 34), self.quit))
        menu.add_button(Button(Vec(234, 314), Vec(240, 64), Vec(34, 34), lambda slot=-2: self.start_slot(slot)))
        menu.add_button(Button(Vec(322, 314), Vec(192, 0), Vec(34, 34), self.toggle_dark_mode))

        return menu
    
    def create_bar(self):

        def _renderer(menu):
            draw.draw_rect(None, Vec(0, 0), Vec(500, 11), (255, 255, 255) if (Globals.dark_mode) else (0, 0, 0))

        bar = Menu(self, _renderer, Vec(0, 0), Vec(500, 11), False)

        bar.add_button(Button(Vec(1, 1), Vec(240, 48), Vec(18, 9), self.back))

        return bar


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

    def draw(self):
        Menu.draw_ui(self.pos, self.top_left, self.size)

class Menu:

    @staticmethod
    def draw_ui(pos: Vec, top_left: Vec, size: Vec):
        draw.draw_texture(None, Sprites.gui, pos * 2, top_left + Vec(0, 448 if (Globals.dark_mode) else 0), size)

    def __init__(self, app: App, renderer, top_left: Vec, size: Vec, active = True):
        self.app = app
        self.renderer = renderer
        self.top_left = top_left
        self.size = size
        self.active = active

        self.buttons = []

    def add_button(self, button: Button):
        self.buttons.append(button)

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
            b.draw()