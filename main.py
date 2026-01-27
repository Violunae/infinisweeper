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

    pygame.mixer.pre_init(44100, -16, 2, 2048)
    Globals.sound_click = pygame.mixer.Sound("assets/sounds/click.wav")
    Globals.sound_click.set_volume(0.25)
    Globals.sound_unclick = pygame.mixer.Sound("assets/sounds/unclick.wav")
    Globals.sound_unclick.set_volume(0.25)
    Globals.sound_open = pygame.mixer.Sound("assets/sounds/open.wav")
    Globals.sound_open.set_volume(0.2)
    Globals.sound_explosion = pygame.mixer.Sound("assets/sounds/explosion.wav")
    Globals.sound_explosion.set_volume(0.2)

    app = App()
    app.run()

    pygame.quit()
