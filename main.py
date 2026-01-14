import pygame
from globals import Globals
from sprites import Sprites
from app import run
from utils import *

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(1000, 1000)
    Globals.screen = pygame.display.set_mode(Globals.resolution.get_tuple())
    pygame.display.set_caption("InfiniSweeper")

    Sprites.field = pygame.image.load("assets/textures/field.png").convert()

    run()

    pygame.quit()
