"""Piece-count chain: area method -> waste allowance -> optional whole-box rounding.

Each stage is a pure function that can be called on its own; the estimate
service chains them and attaches the grid layout preview.
"""

from app.engines.helpers import ceil_units


def raw_count_by_area(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Stage 1 — area method: net piece count from room and tile areas."""
    area = float(room_l) * float(room_w)
    piece = float(tile_l) * float(tile_w)
    if piece <= 0 or area < 0:
        raise ValueError("invalid dimensions")
    return {
        "area_m2": round(area, 3),
        "piece_m2": round(piece, 4),
        "raw_count": ceil_units(area / piece),
    }


def order_count_with_waste(raw_count: int, waste_pct: float) -> dict:
    """Stage 2 — waste allowance on top of the net count."""
    if raw_count < 0:
        raise ValueError("invalid raw count")
    waste = float(waste_pct)
    return {
        "waste_pct": waste,
        "order_count": ceil_units(int(raw_count) * (1 + waste / 100.0)),
    }


def round_to_full_boxes(count: int, pieces_per_box: int) -> dict:
    """Stage 3 — optional: round a piece count up to whole boxes."""
    if pieces_per_box <= 0:
        raise ValueError("invalid box size")
    boxes = ceil_units(int(count) / int(pieces_per_box))
    return {
        "pieces_per_box": int(pieces_per_box),
        "box_count": boxes,
        "box_rounded_count": boxes * int(pieces_per_box),
    }


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
