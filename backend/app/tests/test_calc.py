import pytest
from fastapi import HTTPException

from app.services.estimate_service import calculate_order


def test_corridor_strip_chain():
    r = calculate_order(8.0, 1.2, 0.8, 0.8, 8.0)
    assert r["raw_count"] == 15
    assert r["order_count"] == 17


def test_guest_room_seed_default():
    # 种子默认链路：客餐厅 6.0x4.5 + 600x600 + 损耗 8% -> raw=75, order=81
    r = calculate_order(6.0, 4.5, 0.6, 0.6, 8.0)
    assert r["area_m2"] == 27.0
    assert r["piece_m2"] == 0.36
    assert r["raw_count"] == 75
    assert r["waste_pct"] == 8.0
    assert r["order_count"] == 81
    assert r["layout"]["cols"] == 10
    assert r["layout"]["rows"] == 8
    assert r["layout"]["grid_count"] == 80


def test_box_rounding_through_chain():
    r = calculate_order(6.0, 4.5, 0.6, 0.6, 8.0, box_size=20)
    assert r["raw_count"] == 75
    assert r["order_count"] == 100  # 81 片进位到 5 箱 x 20


def test_invalid_dimensions_rejected():
    with pytest.raises(HTTPException) as exc:
        calculate_order(6.0, 4.5, 0.0, 0.6, 8.0)
    assert exc.value.status_code == 422
