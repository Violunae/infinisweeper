import os
import struct
import shutil

REGION_SIZE = 16

#region paths

def _save_root(slot):
    return f"saves/{slot}"

def _regions_dir(slot):
    return f"{_save_root(slot)}/regions"

def _region_path(slot, rx, ry):
    return f"{_regions_dir(slot)}/r.{rx}.{ry}.msreg"

def _map_path(slot):
    return f"{_save_root(slot)}/map.msmap"

def _ensure_save_dirs(slot):
    os.makedirs(_regions_dir(slot), exist_ok=True)

#endregion

#region map

def save_map(map):
    _ensure_save_dirs(map.slot)
    with open(_map_path(map.slot), "wb") as f:
        f.write(map.to_bytes())


def reload_map(slot):
    path = _map_path(slot)
    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return f.read()
    
#endregion

#region chunks

def save_chunk(slot, cx, cy, cell_bytes: bytes):
    _ensure_save_dirs(slot)

    rx = cx // REGION_SIZE
    ry = cy // REGION_SIZE
    lx = cx % REGION_SIZE
    ly = cy % REGION_SIZE

    path = _region_path(slot, rx, ry)
    chunks = {}

    if os.path.exists(path):
        with open(path, "rb") as f:
            count = struct.unpack("<H", f.read(2))[0]
            for _ in range(count):
                x, y = struct.unpack("bb", f.read(2))
                size = struct.unpack("<I", f.read(4))[0]
                chunks[(x, y)] = f.read(size)

    chunks[(lx, ly)] = cell_bytes

    with open(path, "wb") as f:
        f.write(struct.pack("<H", len(chunks)))
        for (x, y), data in chunks.items():
            f.write(struct.pack("bb", x, y))
            f.write(struct.pack("<I", len(data)))
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
        count = struct.unpack("<H", f.read(2))[0]
        for _ in range(count):
            x, y = struct.unpack("bb", f.read(2))
            size = struct.unpack("<I", f.read(4))[0]
            data = f.read(size)
            if x == lx and y == ly:
                return data

    return None

#endregion

#region delete

def delete_save(slot):
    shutil.rmtree(_save_root(slot), ignore_errors=True)

#endregion
