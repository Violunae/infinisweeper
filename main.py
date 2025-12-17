import pygame
import game
from utils import *
from globals import Globals

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(500, 500)
    Globals.screen = pygame.display.set_mode(Globals.resolution.getTuple())
    pygame.display.set_caption("InfiniSweeper")

    map = game.Map()

    running = True
    clock = pygame.time.Clock()

    zoom_speed = 1.0
    min_zoom = 10.0
    max_zoom = 50.0

    dragging = False
    last_mouse_pos = Vec(0, 0)

    dirty = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    dragging = True
                    last_mouse_pos = Vec(*event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    dragging = False

            elif event.type == pygame.MOUSEWHEEL:
                old_zoom = map.camera.zoom
                map.camera.zoom += zoom_speed * event.y
                map.camera.zoom = max(min_zoom, min(max_zoom, map.camera.zoom))

                if map.camera.zoom != old_zoom:
                    dirty = True

        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            current_mouse_pos = Vec(mouse_x, mouse_y)
            delta = current_mouse_pos - last_mouse_pos

            if delta.x != 0 or delta.y != 0:
                map.camera.pos.x -= delta.x / map.camera.zoom
                map.camera.pos.y -= delta.y / map.camera.zoom
                dirty = True

            last_mouse_pos = current_mouse_pos

        if dirty:
            map.update()
            map.draw()
            pygame.display.update()
            dirty = False

        clock.tick(60)

    pygame.quit()import pygame
import game
from utils import *
from globals import Globals

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(500, 500)
    Globals.screen = pygame.display.set_mode(Globals.resolution.getTuple())
    pygame.display.set_caption("InfiniSweeper")

    map = game.Map()

    running = True
    clock = pygame.time.Clock()

    # Camera control settings
    zoom_speed = 1.0
    min_zoom = 10.0
    max_zoom = 50.0

    # Dragging state
    dragging = False
    last_mouse_pos = Vec(0, 0)

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Start dragging (middle mouse button)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:  # 2 = middle mouse button
                    dragging = True
                    last_mouse_pos = Vec(*event.pos)

            # Stop dragging
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    dragging = False

            # Zooming
            elif event.type == pygame.MOUSEWHEEL:
                map.camera.zoom += zoom_speed * event.y
                map.camera.zoom = max(min_zoom, min(max_zoom, map.camera.zoom))

        # Camera dragging
        if dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            current_mouse_pos = Vec(mouse_x, mouse_y)
            delta = current_mouse_pos - last_mouse_pos

            # Move camera opposite to mouse movement
            map.camera.pos.x -= delta.x / map.camera.zoom
            map.camera.pos.y -= delta.y / map.camera.zoom

            last_mouse_pos = current_mouse_pos

        # Update and draw
        map.update()
        map.draw()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()

