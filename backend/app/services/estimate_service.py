from fastapi import HTTPException

from app.engines import tile_math
from app.repositories import history, rooms, settings_repo, tiles


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    save: bool,
    note: str,
    box_size: int | None = None,
):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    calc = calculate_order(
        room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste, box_size
    )

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        **calc,
    }


def calculate_order(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
    box_size: int | None = None,
) -> dict:
    """Chain raw -> waste -> optional box rounding; external keys unchanged."""
    try:
        raw = tile_math.raw_count_by_area(room_l, room_w, tile_l, tile_w)
        order = tile_math.apply_waste(raw, waste_pct)
        order = tile_math.round_up_to_boxes(order, box_size)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "area_m2": round(tile_math.room_area_m2(room_l, room_w), 3),
        "piece_m2": round(tile_math.piece_area_m2(tile_l, tile_w), 4),
        "raw_count": raw,
        "waste_pct": float(waste_pct),
        "order_count": order,
        "layout": tile_math.layout_preview(room_l, room_w, tile_l, tile_w),
    }
