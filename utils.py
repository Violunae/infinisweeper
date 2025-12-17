from dataclasses import dataclass
import math

@dataclass(frozen=True)
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
    
    def getTuple(self):
        return (self.x, self.y)
    
class Camera:
    def __init__(self):
        self.pos = Vec(0, 0)
        self.zoom = 5.0

    def transform(self, point: Vec):
        return Vec((point.x - self.pos.x) * self.zoom + 250, (point.y - self.pos.y) * self.zoom + 250)
