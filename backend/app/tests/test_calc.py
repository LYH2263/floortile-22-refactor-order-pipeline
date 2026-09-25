from app.engines.tile_math import order_count_with_waste, raw_count_by_area


def test_corridor_strip():
    raw = raw_count_by_area(8.0, 1.2, 0.8, 0.8)["raw_count"]
    assert raw == 15
    assert order_count_with_waste(raw, 8.0)["order_count"] == 17
