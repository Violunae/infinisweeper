import random

import draw
from utils import *

class Cell:
    def __init__(self, mines: int):
        self.flag = False
        self.mines = mines

    def draw(self, camera: Camera, pos: Vec):
        draw.drawRect(camera, pos, Vec(1, 1), (255, 0, 0) if (self.mines > 0) else (0, 255, 0))

class Chunk:
    CHUNK_SIZE = 16

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def generate(self, map):
        chunk_seed = hash((map.seed, self.x, self.y))
        rng = random.Random(chunk_seed)
        self.cells = [[Cell(1 if (rng.random() < 0.1) else 0) for x in range(self.CHUNK_SIZE)] for y in range(self.CHUNK_SIZE)]

    def load(self, map):
        self.generate(map)

    def unload(self, map):
        pass

    def draw(self, camera: Camera):
        for cellY in range(self.CHUNK_SIZE):
            for cellX in range(self.CHUNK_SIZE):
                self.cells[cellY][cellX].draw(camera, Vec(self.CHUNK_SIZE * self.x + cellX, self.CHUNK_SIZE * self.y + cellY))

class Map:

    def __init__(self, seed=0):
        self.seed = seed if (seed != 0) else random.randint(1, 999999)
        self.chunks = {}
        self.camera = Camera()

    def update(self):
        self.load_chunks()
    
    def load_chunks(self):
        min_x, min_y, max_x, max_y = self.camera.get_view_bounds()

        # Convert world bounds → chunk bounds
        min_chunk_x = int(min_x // Chunk.CHUNK_SIZE)
        max_chunk_x = int(max_x // Chunk.CHUNK_SIZE)
        min_chunk_y = int(min_y // Chunk.CHUNK_SIZE)
        max_chunk_y = int(max_y // Chunk.CHUNK_SIZE)

        new_chunks = {}

        for cx in range(min_chunk_x, max_chunk_x + 1):
            for cy in range(min_chunk_y, max_chunk_y + 1):
                pos = (cx, cy)

                if pos not in self.chunks:
                    chunk = Chunk(cx, cy)
                    chunk.load(self)
                    new_chunks[pos] = chunk
                else:
                    new_chunks[pos] = self.chunks[pos]

        # Unload chunks no longer visible
        for pos, chunk in self.chunks.items():
            if pos not in new_chunks:
                chunk.unload(self)

        self.chunks = new_chunks

    def draw(self):
        draw.clearScreen((0, 0, 0))
        for chunk in self.chunks.values():
            chunk.draw(self.camera)