import pygame
import game
from utils import *
from globals import Globals
from sprites import Sprites

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(500, 500)
    Globals.screen = pygame.display.set_mode(Globals.resolution.getTuple())
    pygame.display.set_caption("InfiniSweeper")

    Sprites.field = pygame.image.load("assets/textures/field.png").convert()

    map = game.Map()

    running = True
    clock = pygame.time.Clock()

    # Camera control settings
    zoom_speed = 1.0
    min_zoom = 8.0
    max_zoom = 64.0

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
                if (event.button == 1):
                    mouse_pos = Vec(*event.pos)
                    global_pos = map.camera.reverse_transform(mouse_pos)
                    map.openCell(global_pos.floor())
                elif event.button == 2:  # 2 = middle mouse button
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
        clock.tick(30)

    pygame.quit()

