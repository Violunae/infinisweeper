import pygame

from globals import Globals

from utils import * 

def clear_screen(color=(0, 0, 0)):
    Globals.screen.fill(color)

def draw_polygon(camera: Camera, points, color = (255, 255, 255)):
    if (camera != None):
        trans_points = [camera.transform().get_tuple() for point in points]
    else:
        trans_points = [(point * 2).get_tuple() for point in points]

    #flat_points = [coord for point in trans_points for coord in point]

    pygame.draw.polygon(Globals.screen, color, trans_points)

def draw_rect(camera: Camera, pos: Vec, size: Vec, color=(255, 255, 255)):
    top_left = pos
    top_right = Vec(pos.x + size.x, pos.y)
    bottom_right = Vec(pos.x + size.x, pos.y + size.y)
    bottom_left = Vec(pos.x, pos.y + size.y)
    
    draw_polygon(camera, [top_left, top_right, bottom_right, bottom_left], color)

def draw_texture(camera: Camera, texture: pygame.Surface, pos: Vec, top_left: Vec, size: Vec):
    # t = pygame.time.get_ticks() * 0.002 + (pos.x * 0.2) + (pos.y * 0.2)
    # tx = math.cos(t)
    # ty = math.sin(t)
    # pos = pos + Vec(tx, ty)

    surf = texture.subsurface(pygame.Rect(top_left.x, top_left.y, size.x, size.y))
    zoom = camera.zoom if (camera != None) else 64
    surf_scaled = pygame.transform.scale_by(surf, (zoom / 32.0, zoom / 32.0))
    trans_pos = Camera.static_transform(camera, pos)
    Globals.screen.blit(surf_scaled, trans_pos.get_tuple())
    #if (camera == None): raise 4564645

fade_surface = pygame.Surface((1000, 1000), pygame.SRCALPHA)
def draw_fade(color = (0, 0, 0, 127)):
    pygame.draw.polygon(fade_surface, color, [(0, 0), (2000, 0), (0, 2000)])
    Globals.screen.blit(fade_surface, (0, 0))

def draw_text(pos: Vec, text: str, color, font):
    pos = pos * 2 + Vec(0, -8)
    surf = font.render(text, False, color)
    surf_scaled = pygame.transform.scale_by(surf, (2, 2))
    Globals.screen.blit(surf_scaled, pos.get_tuple())
