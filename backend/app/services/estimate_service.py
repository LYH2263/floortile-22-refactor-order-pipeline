from fastapi import HTTPException

from app.engines.tile_math import (
    layout_preview,
    order_count_with_waste,
    raw_count_by_area,
    round_to_full_boxes,
)
from app.repositories import history, rooms, settings_repo, tiles


def run_estimate(
    room_id: int,
    tile_id: int,
    waste_pct: float | None,
    save: bool,
    note: str,
    pieces_per_box: int | None = None,
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

    try:
        calc = raw_count_by_area(room["length"], room["width"], tile["tile_l"], tile["tile_w"])
        calc.update(order_count_with_waste(calc["raw_count"], waste))
        if pieces_per_box is not None:
            calc.update(round_to_full_boxes(calc["order_count"], pieces_per_box))
    except ValueError as exc:
        raise HTTPException(422, str(exc))

    calc["layout"] = layout_preview(room["length"], room["width"], tile["tile_l"], tile["tile_w"])

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
