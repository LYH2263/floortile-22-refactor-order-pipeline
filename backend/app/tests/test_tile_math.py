import pytest

from app.engines.tile_math import (
    apply_waste,
    layout_preview,
    raw_count_by_area,
    round_up_to_boxes,
)


def test_raw_stage_guest_room():
    # 面积法单独一截：6.0 x 4.5 房、0.6 x 0.6 砖 -> raw=75
    assert raw_count_by_area(6.0, 4.5, 0.6, 0.6) == 75


def test_waste_stage_guest_room():
    # 损耗截单独核对：raw=75 套 8% -> order=81
    assert apply_waste(75, 8.0) == 81


def test_waste_stage_zero_pct():
    assert apply_waste(9, 0.0) == 9


def test_box_stage_optional():
    assert round_up_to_boxes(81, None) == 81  # 不启用，原样返回
    assert round_up_to_boxes(81, 1) == 81  # 每箱 1 片，等价不启用
    assert round_up_to_boxes(81, 10) == 90  # 81 片进位到 9 箱
    assert round_up_to_boxes(80, 10) == 80  # 正好整箱不再加


def test_box_stage_invalid_size():
    with pytest.raises(ValueError):
        round_up_to_boxes(81, 0)


def test_raw_stage_invalid_dimensions():
    with pytest.raises(ValueError):
        raw_count_by_area(6.0, 4.5, 0.0, 0.6)  # 零面积砖
    with pytest.raises(ValueError):
        raw_count_by_area(6.0, -0.5, 0.6, 0.6)  # 负宽


def test_layout_preview_small_room():
    lp = layout_preview(2.5, 2.0, 0.6, 0.6)
    assert lp["cols"] == 5
    assert lp["rows"] == 4
    assert lp["grid_count"] == 20
