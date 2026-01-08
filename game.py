import random

import draw
from utils import *
import save
import struct

class Cell:
    def __init__(self, mines: int):
        self.mines = mines
        self.flags = 0
        self.opened = False
        self.cached_num = -1

    def open(self):
        self.opened = True

    def draw(self, camera: Camera, pos: Vec):
        #draw.draw_rect(camera, pos, Vec(1, 1), (255, 0, 0) if (self.mines > 0) else (0, 255, 0))
        frame = 0
        if (self.opened):
            if (self.mines == 0):
                if (self.cached_num <= 0):
                    frame = 1
                else:
                    frame = 7 + self.cached_num
            else:
                frame = 4 + self.mines
        elif (self.flags > 0):
            frame = 1 + self.flags

        draw.draw_field_tile(camera, frame, 1 if Globals.dark_mode else 0, pos)

class Chunk:
    CHUNK_SIZE = 16

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.generated = False
        self.cells = {}

    def generate(self, map):
        self.generated = True
        chunk_seed = hash((map.seed, self.x, self.y))
        rng = random.Random(chunk_seed)
        self.cells = [[Cell(1 if (rng.random() < 0.15) else 0) for x in range(self.CHUNK_SIZE)] for y in range(self.CHUNK_SIZE)]
        # self.cells = [[Cell(1 if ((x % 5 == 0) or (y % 5 == 0)) else 0) for x in range(self.CHUNK_SIZE)] for y in range(self.CHUNK_SIZE)]


    def load(self, map):
        data = save.reload_chunk(self.x, self.y)
        if data:
            loaded = Chunk.from_bytes(self.x, self.y, data)
            self.cells = loaded.cells
            self.generated = True
        else:
            self.cells = [[Cell(0) for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)]
            self.generated = False

    def unload(self, map):
        if self.generated:
            save.save_chunk(self.x, self.y, self.CHUNK_SIZE, self.to_bytes())

    def get_cell(self, map, pos: Vec):
        if (self.generated == False):
            self.generate(map)
        return self.cells[pos.y][pos.x]

    def draw(self, camera: Camera):
        for cellY in range(self.CHUNK_SIZE):
            for cellX in range(self.CHUNK_SIZE):
                self.cells[cellY][cellX].draw(camera, Vec(self.CHUNK_SIZE * self.x + cellX, self.CHUNK_SIZE * self.y + cellY))

    def to_bytes(self):
        data = bytearray()
        for y in range(self.CHUNK_SIZE):
            for x in range(self.CHUNK_SIZE):
                cell = self.cells[y][x]
                byte0 = ((cell.mines & 0xF) << 4) | (cell.flags & 0xF)
                data.append(byte0)
                data.append(struct.pack("b", cell.cached_num)[0])
        return bytes(data)
    
    @staticmethod
    def from_bytes(cx, cy, data):
        chunk = Chunk(cx, cy)
        chunk.generated = True
        chunk.cells = [[None]*Chunk.CHUNK_SIZE for _ in range(Chunk.CHUNK_SIZE)]

        i = 0
        for y in range(Chunk.CHUNK_SIZE):
            for x in range(Chunk.CHUNK_SIZE):
                byte0 = data[i]
                cached = struct.unpack("b", data[i+1:i+2])[0]
                i += 2

                mines = (byte0 >> 4) & 0xF
                flags = byte0 & 0xF

                cell = Cell(mines)
                cell.flags = flags
                cell.cached_num = cached
                cell.opened = cached >= 0
                chunk.cells[y][x] = cell

        return chunk
 
class Map:

    def __init__(self, seed=0):
        self.seed = seed if (seed != 0) else random.randint(1, 999999)
        self.chunks = {}
        self.camera = Camera()

    def update(self):
        self.load_chunks()
    
    def load_chunks(self):
        min_x, min_y, max_x, max_y = self.camera.get_view_bounds()

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

        for pos, chunk in self.chunks.items():
            if pos not in new_chunks:
                chunk.unload(self)

        self.chunks = new_chunks

    def unload_chunks(self):
        for chunk in self.chunks.values():
            chunk.unload(self)

    def load_chunk(self, pos: Vec):
        chunk = Chunk(pos.x, pos.y)
        chunk.load(self)
        self.chunks[pos.get_tuple()] = chunk
        return chunk

    def get_chunk(self, pos: Vec):
        if (pos.get_tuple() in self.chunks.keys()):
            return self.chunks[pos.get_tuple()]
        chunk = Chunk(pos.x, pos.y)
        chunk.load(self)
        return self.load_chunk(pos)
    
    @staticmethod
    def global_to_local_coord(pos: Vec):
        return Vec(pos.x % Chunk.CHUNK_SIZE, pos.y % Chunk.CHUNK_SIZE)

    @staticmethod
    def global_to_local_chunk(pos: Vec):
        return Vec(pos.x // Chunk.CHUNK_SIZE, pos.y // Chunk.CHUNK_SIZE)

    def get_cell(self, pos: Vec):
        chunk = self.get_chunk(Map.global_to_local_chunk(pos))
        return chunk.get_cell(self, Map.global_to_local_coord(pos))
    
    def count_mines_around(self, pos: Vec):
        mines = 0
        mines = mines + self.get_cell(pos + Vec(-1, -1)).mines
        mines = mines + self.get_cell(pos + Vec( 0, -1)).mines
        mines = mines + self.get_cell(pos + Vec( 1, -1)).mines
        mines = mines + self.get_cell(pos + Vec( 1,  0)).mines
        mines = mines + self.get_cell(pos + Vec( 1,  1)).mines
        mines = mines + self.get_cell(pos + Vec( 0,  1)).mines
        mines = mines + self.get_cell(pos + Vec(-1,  1)).mines
        mines = mines + self.get_cell(pos + Vec(-1,  0)).mines
        return mines

    def open_cell(self, pos: Vec, depth = 0):
        cell = self.get_cell(pos)

        if ((cell.flags > 0) or (cell.opened and (depth != 0))): return

        wasOpen = cell.opened 
        cell.opened = True
        mines = self.count_mines_around(pos)
        cell.cached_num = mines

        if (((mines == 0) and (depth < 512)) or (wasOpen and (depth == 0))):
            self.open_cell(pos + Vec(-1, -1), depth + 1)
            self.open_cell(pos + Vec( 0, -1), depth + 1)
            self.open_cell(pos + Vec( 1, -1), depth + 1)
            self.open_cell(pos + Vec( 1,  0), depth + 1)
            self.open_cell(pos + Vec( 1,  1), depth + 1)
            self.open_cell(pos + Vec( 0,  1), depth + 1)
            self.open_cell(pos + Vec(-1,  1), depth + 1)
            self.open_cell(pos + Vec(-1,  0), depth + 1)



    def flag_cell(self, pos: Vec):
        cell = self.get_cell(pos)
        if (cell.opened): return
        cell.flags = 1 - cell.flags

    def draw(self):
        draw.clear_screen((101, 119, 128))
        for chunk in self.chunks.values():
            chunk.draw(self.camera)
    
    def delete(self):
        save.delete_save()