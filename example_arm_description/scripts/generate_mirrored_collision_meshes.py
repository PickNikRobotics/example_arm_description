#!/usr/bin/env python3
"""Generate the mirrored collision meshes used by r6bot_description with mirror:=true.

Reflects each binary STL in meshes/collision across its y-z plane (x -> -x) into meshes/collision/mirrored. Reflection
alone would turn every triangle inside out, so the vertex order of each triangle is reversed to keep the normals
pointing outward; collision padding grows a mesh along those normals.

Usage: python3 generate_mirrored_collision_meshes.py
"""

import pathlib
import struct

HEADER_SIZE = 80
TRIANGLE = struct.Struct("<12fH")


def mirror_binary_stl(source: pathlib.Path, target: pathlib.Path) -> None:
    data = source.read_bytes()
    (count,) = struct.unpack_from("<I", data, HEADER_SIZE)
    if len(data) != HEADER_SIZE + 4 + count * TRIANGLE.size:
        raise ValueError(f"{source} is not a binary STL")
    out = bytearray(data[: HEADER_SIZE + 4])
    for i in range(count):
        values = TRIANGLE.unpack_from(data, HEADER_SIZE + 4 + i * TRIANGLE.size)
        normal, v1, v2, v3, attribute = (
            values[0:3],
            values[3:6],
            values[6:9],
            values[9:12],
            values[12],
        )

        def reflect(v):
            return (-v[0], v[1], v[2])

        out += TRIANGLE.pack(
            *reflect(normal), *reflect(v1), *reflect(v3), *reflect(v2), attribute
        )
    target.write_bytes(bytes(out))


def main() -> None:
    collision_dir = (
        pathlib.Path(__file__).resolve().parent.parent / "meshes" / "collision"
    )
    mirrored_dir = collision_dir / "mirrored"
    mirrored_dir.mkdir(exist_ok=True)
    for source in sorted(collision_dir.glob("*.stl")):
        mirror_binary_stl(source, mirrored_dir / source.name)


if __name__ == "__main__":
    main()
