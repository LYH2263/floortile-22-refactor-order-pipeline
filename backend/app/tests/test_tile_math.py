import pytest

from app.engines.tile_math import (
    layout_preview,
    order_count_with_waste,
    raw_count_by_area,
    round_to_full_boxes,
)


def test_raw_stage_guest_dining():
    r = raw_count_by_area(6.0, 4.5, 0.6, 0.6)
    assert r["area_m2"] == 27.0
    assert r["piece_m2"] == 0.36
    assert r["raw_count"] == 75


def test_waste_stage_guest_dining():
    raw = raw_count_by_area(6.0, 4.5, 0.6, 0.6)["raw_count"]
    r = order_count_with_waste(raw, 8.0)
    assert r["waste_pct"] == 8.0
    assert r["order_count"] == 81


def test_box_stage_rounds_up():
    r = round_to_full_boxes(81, 10)
    assert r["pieces_per_box"] == 10
    assert r["box_count"] == 9
    assert r["box_rounded_count"] == 90


def test_box_stage_exact_fit():
    r = round_to_full_boxes(80, 10)
    assert r["box_count"] == 8
    assert r["box_rounded_count"] == 80


def test_raw_stage_rejects_zero_tile():
    with pytest.raises(ValueError):
        raw_count_by_area(6.0, 4.5, 0.0, 0.6)


def test_box_stage_rejects_bad_box():
    with pytest.raises(ValueError):
        round_to_full_boxes(81, 0)


def test_layout_preview_guest_dining():
    lp = layout_preview(6.0, 4.5, 0.6, 0.6)
    assert lp["cols"] == 10
    assert lp["rows"] == 8
    assert lp["grid_count"] == 80


def test_layout_preview_small_room():
    lp = layout_preview(2.5, 2.0, 0.6, 0.6)
    assert lp["cols"] == 5
    assert lp["rows"] == 4
    assert lp["grid_count"] == 20


def test_zero_waste():
    raw = raw_count_by_area(3.0, 3.0, 1.0, 1.0)["raw_count"]
    assert raw == 9
    assert order_count_with_waste(raw, 0.0)["order_count"] == 9
