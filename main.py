import pygame
import game
from utils import *
from globals import Globals
from sprites import Sprites

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(1000, 1000)
    Globals.screen = pygame.display.set_mode(Globals.resolution.get_tuple())

    pygame.display.set_caption("InfiniSweeper")

    Sprites.field = pygame.image.load("assets/textures/field.png").convert()

    map = game.Map()

    running = True
    clock = pygame.time.Clock()

    zoom_speed = 1.0
    min_zoom = 8.0
    max_zoom = 64.0

    dragging = False
    last_mouse_pos = Vec(0, 0)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                map.unload_chunks()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    dragging = True
                    last_mouse_pos = Vec(*event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if ((event.button == 1) or (event.button == 3)):
                    mouse_pos = Vec(*event.pos)
                    global_pos = map.camera.reverse_transform(mouse_pos)
                    if (event.button == 1):
                        map.open_cell(global_pos.floor())
                    else:
                        map.flag_cell(global_pos.floor())
                elif event.button == 2:
                    dragging = False

            elif event.type == pygame.MOUSEWHEEL:
                map.camera.zoom += zoom_speed * event.y
                map.camera.zoom = max(min_zoom, min(max_zoom, map.camera.zoom))

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    Globals.dark_mode = not Globals.dark_mode
                if event.key == pygame.K_DELETE:
                    map.delete()
                    map = game.Map()

        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            current_mouse_pos = Vec(mouse_x, mouse_y)
            delta = current_mouse_pos - last_mouse_pos

            map.camera.pos.x -= delta.x / map.camera.zoom
            map.camera.pos.y -= delta.y / map.camera.zoom

            last_mouse_pos = current_mouse_pos

        map.update()
        map.draw()
        pygame.display.update()
        clock.tick(30)

    pygame.quit()

