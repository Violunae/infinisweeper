import pygame
from globals import Globals

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