"""Piece-count chain: area method -> waste -> optional box rounding.

Each stage is independently callable; the service layer chains them
and shapes the external JSON. Grid layout preview stays alongside.
"""

from app.engines.helpers import ceil_units


def raw_count_by_area(room_l: float, room_w: float, tile_l: float, tile_w: float) -> int:
    """Stage 1 — area method: ceil(room_area / tile_piece_area)."""
    area = room_area_m2(room_l, room_w)
    piece = piece_area_m2(tile_l, tile_w)
    if piece <= 0 or area < 0:
        raise ValueError("invalid dimensions")
    return ceil_units(area / piece)


def apply_waste(raw_count: int, waste_pct: float) -> int:
    """Stage 2 — waste allowance: ceil(raw * (1 + waste_pct/100))."""
    raw = int(raw_count)
    if raw < 0:
        raise ValueError("invalid raw count")
    return ceil_units(raw * (1 + float(waste_pct) / 100.0))


def round_up_to_boxes(count: int, box_size: int | None) -> int:
    """Stage 3 (optional) — round up to whole boxes; box_size=None skips."""
    count = int(count)
    if box_size is None:
        return count
    box = int(box_size)
    if box <= 0:
        raise ValueError("invalid box size")
    boxes = -(-count // box)  # integer ceil division
    return boxes * box


def room_area_m2(room_l: float, room_w: float) -> float:
    return float(room_l) * float(room_w)


def piece_area_m2(tile_l: float, tile_w: float) -> float:
    return float(tile_l) * float(tile_w)


def layout_preview(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Grid count if tiles are laid on a full rectangular lattice (may exceed area method)."""
    cols = ceil_units(float(room_l) / float(tile_l))
    rows = ceil_units(float(room_w) / float(tile_w))
    grid_count = cols * rows
    return {
        "cols": cols,
        "rows": rows,
        "grid_count": grid_count,
    }
