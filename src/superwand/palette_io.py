"""
Read and write palettes: hex lists, JSON, TOML, GIMP .gpl, Adobe .ase and CSS
custom properties.
"""

from __future__ import annotations

import json
import re
import struct
import sys
from collections.abc import Sequence
from os import PathLike
from pathlib import Path

from .color import RGB, parse_color, parse_palette, rgb_to_hex

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

FORMATS = ("hex", "json", "css", "gpl", "ase")
READ_EXTENSIONS = (".hex", ".txt", ".json", ".toml", ".gpl", ".ase", ".css")
_EXT_TO_FORMAT = {
    ".hex": "hex",
    ".txt": "hex",
    ".json": "json",
    ".css": "css",
    ".gpl": "gpl",
    ".ase": "ase",
}

StrPath = str | PathLike[str]


def load_palette(path: StrPath) -> tuple[str, list[RGB]]:
    """Returns (name, colors) from a palette file; the name defaults to the file stem."""
    path = Path(path)
    ext = path.suffix.lower()
    name = path.stem
    if ext == ".ase":
        found_name, colors = _read_ase(path.read_bytes())
        return found_name or name, colors

    text = path.read_text(encoding="utf-8")
    if ext == ".json":
        data = json.loads(text)
        if isinstance(data, dict):
            name = data.get("name", name)
            data = data.get("colors", [])
        return name, parse_palette(data)
    if ext == ".toml":
        data = tomllib.loads(text)
        return data.get("name", name), parse_palette(data.get("colors", []))
    if ext == ".gpl":
        return _read_gpl(text, name)
    if ext == ".css":
        values = re.findall(r"--[\w-]+\s*:\s*([^;}]+)", text)
        return name, [parse_color(v) for v in values]
    return name, _read_hex(text)


def _read_hex(text: str) -> list[RGB]:
    colors: list[RGB] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith((";", "//")) or re.match(r"#(\s|$)", line):
            continue
        colors.extend(parse_palette(line))
    if not colors:
        raise ValueError("Palette file has no colors")
    return colors


def _read_gpl(text: str, name: str) -> tuple[str, list[RGB]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "GIMP Palette":
        raise ValueError("Not a GIMP palette (missing 'GIMP Palette' header)")
    colors: list[RGB] = []
    for line in lines[1:]:
        line = line.strip()
        if line.startswith("Name:"):
            name = line[5:].strip() or name
        elif line and not line.startswith(("#", "Columns:")):
            r, g, b = line.split()[:3]
            colors.append(parse_color((int(r), int(g), int(b))))
    return name, colors


def _read_ase(data: bytes) -> tuple[str | None, list[RGB]]:
    if data[:4] != b"ASEF":
        raise ValueError("Not an Adobe Swatch Exchange file")
    (count,) = struct.unpack(">I", data[8:12])
    pos, group, colors = 12, None, []
    for _ in range(count):
        kind, length = struct.unpack(">HI", data[pos : pos + 6])
        body = data[pos + 6 : pos + 6 + length]
        pos += 6 + length
        if kind not in (0x0001, 0xC001):
            continue
        (n,) = struct.unpack(">H", body[:2])
        label = body[2 : 2 + 2 * n].decode("utf-16-be").rstrip("\0")
        if kind == 0xC001:
            group = group or label
            continue
        rest = body[2 + 2 * n :]
        model = rest[:4]
        if model == b"RGB ":
            vals = struct.unpack(">3f", rest[4:16])
        elif model == b"Gray":
            (v,) = struct.unpack(">f", rest[4:8])
            vals = (v, v, v)
        elif model == b"CMYK":
            c, m, y, k = struct.unpack(">4f", rest[4:20])
            vals = ((1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k))
        else:
            raise ValueError(f"Unsupported ASE color model {model!r}")
        colors.append(parse_color(tuple(round(v * 255) for v in vals)))
    return group, colors


def dumps_palette(
    colors: Sequence[Sequence[int]], fmt: str = "hex", name: str = "superwand"
) -> str | bytes:
    """Serializes colors as `fmt` (one of FORMATS); .ase is returned as bytes."""
    hexes = [rgb_to_hex(c) for c in colors]
    if fmt == "hex":
        return "\n".join(hexes) + "\n"
    if fmt == "json":
        return json.dumps({"name": name, "colors": hexes}, indent=2) + "\n"
    if fmt == "css":
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "color"
        body = "".join(f"  --{slug}-{i}: {h};\n" for i, h in enumerate(hexes, 1))
        return ":root {\n" + body + "}\n"
    if fmt == "gpl":
        rows = "".join(
            f"{c[0]:3d} {c[1]:3d} {c[2]:3d}\t{h}\n" for c, h in zip(colors, hexes, strict=True)
        )
        return f"GIMP Palette\nName: {name}\nColumns: {min(len(hexes), 8)}\n#\n{rows}"
    if fmt == "ase":
        return _write_ase(colors, name)
    raise ValueError(f"Unknown palette format {fmt!r}; choose from {', '.join(FORMATS)}")


def _ase_name(label: str) -> bytes:
    encoded = (label + "\0").encode("utf-16-be")
    return struct.pack(">H", len(encoded) // 2) + encoded


def _write_ase(colors: Sequence[Sequence[int]], name: str) -> bytes:
    blocks = []
    group = _ase_name(name)
    blocks.append(struct.pack(">HI", 0xC001, len(group)) + group)
    for c in colors:
        body = (
            _ase_name(rgb_to_hex(c))
            + b"RGB "
            + struct.pack(">3f", *(v / 255 for v in c[:3]))
            + struct.pack(">H", 2)  # normal (not global/spot) color
        )
        blocks.append(struct.pack(">HI", 0x0001, len(body)) + body)
    blocks.append(struct.pack(">HI", 0xC002, 0))
    return b"ASEF" + struct.pack(">HHI", 1, 0, len(blocks)) + b"".join(blocks)


def save_palette(
    colors: Sequence[Sequence[int]], path: StrPath, fmt: str | None = None, name: str | None = None
) -> Path:
    """Writes colors to `path`; the format defaults to the file extension."""
    path = Path(path)
    fmt = fmt or _EXT_TO_FORMAT.get(path.suffix.lower(), "hex")
    data = dumps_palette(colors, fmt, name or path.stem)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")
    return path
