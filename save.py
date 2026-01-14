import os
import struct
import shutil

REGION_SIZE = 16

def _region_path(slot, rx, ry):
    return f"saves/{slot}/r.{rx}.{ry}.msreg"


def _ensure_save_dir(slot):
    os.makedirs(f"saves/{slot}", exist_ok=True)


def save_chunk(slot, cx, cy, chunk_size, cell_bytes: bytes):
    _ensure_save_dir(slot)

    rx = cx // REGION_SIZE
    ry = cy // REGION_SIZE
    lx = cx % REGION_SIZE
    ly = cy % REGION_SIZE

    path = _region_path(slot, rx, ry)
    chunks = {}

    if os.path.exists(path):
        with open(path, "rb") as f:
            count = struct.unpack("H", f.read(2))[0]
            for _ in range(count):
                x, y = struct.unpack("bb", f.read(2))
                size = struct.unpack("I", f.read(4))[0]
                chunks[(x, y)] = f.read(size)

    chunks[(lx, ly)] = cell_bytes

    with open(path, "wb") as f:
        f.write(struct.pack("H", len(chunks)))
        for (x, y), data in chunks.items():
            f.write(struct.pack("bb", x, y))
            f.write(struct.pack("I", len(data)))
            f.write(data)


def reload_chunk(slot, cx, cy):
    rx = cx // REGION_SIZE
    ry = cy // REGION_SIZE
    lx = cx % REGION_SIZE
    ly = cy % REGION_SIZE

    path = _region_path(slot, rx, ry)
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        count = struct.unpack("H", f.read(2))[0]
        for _ in range(count):
            x, y = struct.unpack("bb", f.read(2))
            size = struct.unpack("I", f.read(4))[0]
            data = f.read(size)
            if x == lx and y == ly:
                return data

    return None

def delete_save(slot):
    shutil.rmtree(f"saves/{slot}", ignore_errors=True)
