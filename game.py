import random
import time
import struct

import draw
import save
import audio

from utils import *

class ExplosionWave:
    def __init__(self, pos: Vec):
        self.life = 1
        self.pos = pos

    def update(self):
        self.life = self.life - 0.01

    def get_tile_offset(self, cell_pos):
        life = self.life
        dist = self.pos.distance_to(cell_pos)

        screenshake = math.sin(life * 150) * (life ** 12)
        offset_x = screenshake * 0.5
        offset_y = 0.0

        if (1.0 - life) * 5.0 - dist * 0.2 <= 0.0:
            return Vec(offset_x, offset_y)

        phase = (dist * 0.2 + life * 5.0) * math.tau
        val = -math.sin(phase) * (life ** 2) * 1.5

        dx = cell_pos.x - self.pos.x
        dy = cell_pos.y - self.pos.y
        length = math.hypot(dx, dy)

        if length > 0.0:
            inv_len = 1.0 / length
            offset_x += dx * inv_len * val * 0.25
            offset_y += dy * inv_len * val * 0.25

        offset_y -= val * 0.5

        return Vec(offset_x, offset_y)
    
    def alive(self):
        return self.life > 0

class Cell:
    def __init__(self, mines: int):
        self.mines = mines
        self.flags = 0
        self.opened = False
        self.cached_num = -1

    def open(self, map: "Map", pos: Vec):
        if (not(self.opened)):
            self.opened = True
            if (self.mines > 0):
                map.bombs_exploded = map.bombs_exploded + 1
                map.explode(pos)
            else:
                map.cells_opened = map.cells_opened + 1

    def draw(self, camera: Camera, pos: Vec):
        frame = 0
        if (self.opened):
            if (self.mines == 0):
                if (self.cached_num <= 0):
                    frame = 1
                else:
                    frame = 3 + self.cached_num
            else:
                frame = 2 + self.mines
        elif (self.flags > 0):
            frame = 1 + self.flags

        draw.draw_texture(camera, Globals.texture_field, pos, Vec(frame * 32, 32 if Globals.dark_mode else 0), Vec(32, 32))

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
        data = save.reload_chunk(map.slot, self.x, self.y)
        if (data):
            loaded = Chunk.from_bytes(self.x, self.y, data)
            self.cells = loaded.cells
            self.generated = True
        else:
            self.cells = [[Cell(0) for _ in range(self.CHUNK_SIZE)] for _ in range(self.CHUNK_SIZE)]
            self.generated = False

    def unload(self, map):
        if (self.generated and (map.slot >= 0)):
            save.save_chunk(map.slot, self.x, self.y, self.to_bytes())

    def get_cell(self, map, pos: Vec):
        if (self.generated == False):
            self.generate(map)
        return self.cells[pos.y][pos.x]
    
    def get_cell_pos(self, cell_x, cell_y):
        return Vec(self.CHUNK_SIZE * self.x + cell_x, self.CHUNK_SIZE * self.y + cell_y)

    def draw(self, map: "Map"):
        for cell_y in range(self.CHUNK_SIZE):
            for cell_x in range(self.CHUNK_SIZE):
                pos = self.get_cell_pos(cell_x, cell_y)
                pos = map.offset_tile_pos(pos)
                self.cells[cell_y][cell_x].draw(map.camera, pos)

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

    def __init__(self, slot: int, seed=-1, flags_placed=0, cells_opened=0, bombs_exploded=0, playtime=0):
        self.slot = slot
        self.chunks = {}
        self.camera = Camera()
        self.last_save_time = int(time.time())
        self.explosion_waves = []

        self.seed = seed if (seed != -1) else random.randint(0, 999999)
        self.flags_placed = flags_placed
        self.cells_opened = cells_opened
        self.bombs_exploded = bombs_exploded
        self.playtime = playtime

    @staticmethod
    def load(slot, create):
        data = save.reload_map(slot)
        if (data == None):
            if (create): return Map(slot, -1)
            return None
        return Map.from_bytes(slot, data)

    def update(self):
        self.handle_waves()
        if (self.slot == -1):
            self.demo()
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

        if ((cell.flags > 0) or (cell.opened and (depth != 0))): return False

        wasOpen = cell.opened 
        cell.open(self, pos)
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

        return True

    def flag_cell(self, pos: Vec):
        cell = self.get_cell(pos)
        if (cell.opened): return
        if (cell.flags == 0):
            cell.flags = 1
            self.flags_placed = self.flags_placed + 1
        else:
            cell.flags = 0
            self.flags_placed = self.flags_placed - 1

    def get_score(self):
        return (self.cells_opened * 5) - (self.bombs_exploded * 200)
    
    def get_playtime(self):
        current_time = int(time.time())
        return self.playtime + (current_time - self.last_save_time)
        
    def get_formated_playtime(self):
        return get_formated_time(self.get_playtime())

    def draw(self):
        for chunk in self.chunks.values():
            chunk.draw(self)

    def explode(self, pos: Vec):
        if (self.slot != -1):
            audio.play_sound(Globals.sound_explosion)
        self.explosion_waves.append(ExplosionWave(pos))

    def offset_tile_pos(self, pos: Vec):
        new_pos = pos
        for wave in self.explosion_waves:
            new_pos = new_pos + wave.get_tile_offset(pos)
        return new_pos
            

    def save(self):
        if (self.slot < 0): return
        self.playtime = self.get_playtime()
        self.last_save_time = int(time.time())
        save.save_map(self)
        self.unload_chunks()
    
    def delete(self):
        save.delete_save(self.slot)

    def to_bytes(self):
        return struct.pack(
            "<IIIIIddf",
            self.seed,
            self.flags_placed,
            self.cells_opened,
            self.bombs_exploded,
            self.playtime,
            self.camera.pos.x,
            self.camera.pos.y,
            self.camera.zoom
        )
    
    @staticmethod
    def from_bytes(slot, data):
        seed, flags_placed, cells_opened, bombs_exploded, playtime, camera_x, camera_y, camera_zoom = struct.unpack(
            "<IIIIIddf", data
        )

        map = Map(
            slot,
            seed,
            flags_placed,
            cells_opened,
            bombs_exploded,
            playtime
        )

        map.camera.pos = Vec(camera_x, camera_y)
        map.camera.zoom = camera_zoom
    
        return map
    
    def handle_waves(self):
        for wave in self.explosion_waves:
            wave.update()
        self.explosion_waves = [wave for wave in self.explosion_waves if wave.alive()]
    
    def demo(self):
        self.camera.pos += Vec(0.05, 0.025)
        cell_pos = self.camera.pos.floor() + Vec(7, 4 + random.randrange(-8, 8))
        cell = self.get_cell(cell_pos)
        if ((cell.mines == 0) or (random.randint(1, 100) <= 1)):
            if (not(cell.opened)):
                self.open_cell(cell_pos)
        else:
            if (cell.flags == 0):
                self.flag_cell(cell_pos)
