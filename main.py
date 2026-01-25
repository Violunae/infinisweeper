import pygame

from globals import Globals
from app import App

from utils import *

if __name__ == "__main__":
    pygame.init()

    Globals.resolution = Vec(1000, 1000)
    Globals.screen = pygame.display.set_mode(Globals.resolution.get_tuple())
    pygame.display.set_caption("InfiniSweeper")

    Globals.texture_field = pygame.image.load("assets/textures/field.png").convert()
    Globals.texture_gui = pygame.image.load("assets/textures/gui.png").convert_alpha()

    pygame.font.init()
    Globals.font_big = pygame.font.Font("assets/fonts/SmallGeorge.ttf", 16)
    Globals.font_small = pygame.font.Font("assets/fonts/MultipasMonospace.ttf", 16)

    app = App()
    app.run()

    pygame.quit()
