from dataclasses import dataclass
import math
from globals import Globals

@dataclass
class Vec:
    x: float
    y: float

    def __add__(self, other: "Vec") -> "Vec":
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec") -> "Vec":
        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vec":
        return Vec(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vec":
        mag = self.magnitude() or 1
        return Vec(self.x / mag, self.y / mag)

    def dot(self, other: "Vec") -> float:
        return self.x * other.x + self.y * other.y
    
    def floor(self) -> "Vec":
        return Vec(math.floor(self.x), math.floor(self.y))
    
    def ceil(self) -> "Vec":
        mag = self.magnitude() or 1
        return Vec(math.ceil(self.x), math.ceil(self.y))
    
    def get_tuple(self):
        return (self.x, self.y)
    
class Camera:
    def __init__(self):
        self.pos = Vec(0, 0)
        self.zoom = 32.0

    def transform(self, point: Vec):
        return Vec((point.x - self.pos.x) * self.zoom + (Globals.resolution.x / 2), (point.y - self.pos.y) * self.zoom + (Globals.resolution.y / 2))
    
    def reverse_transform(self, point: Vec):
        return Vec(
            (point.x - (Globals.resolution.x / 2)) / self.zoom + self.pos.x,
            (point.y - (Globals.resolution.y / 2)) / self.zoom + self.pos.y
        )


    def get_view_bounds(self):
        half_w = Globals.resolution.x / (2 * self.zoom)
        half_h = Globals.resolution.y / (2 * self.zoom)

        min_x = self.pos.x - half_w
        max_x = self.pos.x + half_w
        min_y = self.pos.y - half_h
        max_y = self.pos.y + half_h

        return min_x, min_y, max_x, max_y
