import random

import draw
from utils import *

class Cell:
    def __init__(self, mines: int):
        self.flag = False
        self.mines = mines

    def draw(self, camera: Camera, pos: Vec):
        draw.drawRect(camera, pos, Vec(1, 1), "red" if (self.mines > 0) else "green")

class Chunk:
    CHUNK_SIZE = 16

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def generate(self):
        self.cells = [[Cell(1 if (random.random() < 0.1) else 0) for x in range(self.CHUNK_SIZE)] for y in range(self.CHUNK_SIZE)]

    def load(self):
        self.generate()

    def unload(self):
        pass

    def draw(self, camera: Camera):
        for cellY in range(self.CHUNK_SIZE):
            for cellX in range(self.CHUNK_SIZE):
                self.cells[cellY][cellX].draw(camera, Vec(self.CHUNK_SIZE * self.x + cellX, self.CHUNK_SIZE * self.y + cellY))

class Map:

    RENDER_DISTANCE = 2

    def __init__(self):
        self.chunks = {}
        self.camera = Camera()

    def update(self):
        self.load_chunks()
    
    def load_chunks(self):
        cam_chunk_x = int(self.camera.pos.x // Chunk.CHUNK_SIZE)
        cam_chunk_y = int(self.camera.pos.y // Chunk.CHUNK_SIZE)

        new_chunks = {}

        for dx in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
            for dy in range(-self.RENDER_DISTANCE, self.RENDER_DISTANCE + 1):
                dist = (dx**2 + dy**2)**0.5
                if dist <= self.RENDER_DISTANCE:
                    chunk_pos = (cam_chunk_x + dx, cam_chunk_y + dy)
                    if chunk_pos not in self.chunks:
                        chunk = Chunk(*chunk_pos)
                        chunk.load()
                        new_chunks[chunk_pos] = chunk
                    else:
                        new_chunks[chunk_pos] = self.chunks[chunk_pos]

        for pos, chunk in self.chunks.items():
            if pos not in new_chunks:
                chunk.unload()

        self.chunks = new_chunks

    def draw(self):
        draw.clearScreen()
        for chunk in self.chunks.values():
            chunk.draw(self.camera)