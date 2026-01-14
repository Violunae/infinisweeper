import pygame
import game
from utils import *
from globals import Globals

class App:
    def run(self):
        running = True
        dragging = False
        last_mouse_pos = Vec(0, 0)
        slot = -1

        self.map = game.Map(slot)
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    map.save()
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
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

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        Globals.dark_mode = not Globals.dark_mode
                    elif event.key == pygame.K_DELETE:
                        self.map.delete()
                        self.map = game.Map(slot)
                    elif event.key == pygame.K_RETURN:
                        slot = slot + 1
                        self.map.save()
                        self.map = game.Map(slot)

            if dragging:
                current_mouse_pos = Vec(*pygame.mouse.get_pos())
                delta = current_mouse_pos - last_mouse_pos
                
                self.map.camera.pos.x -= delta.x / self.map.camera.zoom
                self.map.camera.pos.y -= delta.y / self.map.camera.zoom

                last_mouse_pos = current_mouse_pos

            self.map.update()
            self.map.draw()
            pygame.display.update()
            clock.tick(30)
