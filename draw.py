import pygame
from globals import Globals
from sprites import Sprites

from utils import * 

def clearScreen(color=(0, 0, 0)):
    Globals.screen.fill(color)

def drawPolygon(camera: Camera, points, color=(255, 255, 255)):
    trans_points = [camera.transform(point).getTuple() for point in points]
    #flat_points = [coord for point in trans_points for coord in point]

    pygame.draw.polygon(Globals.screen, color, trans_points)

def drawRect(camera: Camera, pos: Vec, size: Vec, color=(255, 255, 255)):
    top_left = pos
    top_right = Vec(pos.x + size.x, pos.y)
    bottom_right = Vec(pos.x + size.x, pos.y + size.y)
    bottom_left = Vec(pos.x, pos.y + size.y)
    
    drawPolygon(camera, [top_left, top_right, bottom_right, bottom_left], color)

def drawTexture(camera: Camera, texture: pygame.Surface, pos: Vec, top_left: Vec, size: Vec):
    # t = pygame.time.get_ticks() * 0.002 + (pos.x * 0.2) + (pos.y * 0.2)
    # tx = math.cos(t)
    # ty = math.sin(t)
    # pos = pos + Vec(tx, ty)

    surf = texture.subsurface(pygame.Rect(top_left.x, top_left.y, size.x, size.y))
    surf_scaled = pygame.transform.scale(surf, (camera.zoom, camera.zoom))
    trans_pos = camera.transform(pos)
    Globals.screen.blit(surf_scaled, trans_pos.getTuple())

def drawFieldTile(camera: Camera, frame: int, pos: Vec):
    drawTexture(camera, Sprites.field, pos, Vec(frame * 34, 0), Vec(32, 32))