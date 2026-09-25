import os
import tempfile

# Isolate the sqlite DB before app.config is imported (Docker sets DATA_DIR=/data).
os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="floortile-test-")

import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history
from app.services import estimate_service

seed.init_db()


def test_guest_dining_seed_defaults():
    r = estimate_service.run_estimate(1, 1, None, False, "")
    assert r["area_m2"] == 27.0
    assert r["raw_count"] == 75
    assert r["waste_pct"] == 8.0
    assert r["order_count"] == 81
    assert r["layout"]["grid_count"] == 80
    assert "box_count" not in r


def test_box_rounding_optional():
    r = estimate_service.run_estimate(1, 1, None, False, "", pieces_per_box=10)
    assert r["order_count"] == 81
    assert r["box_count"] == 9
    assert r["box_rounded_count"] == 90


def test_save_persists_run():
    r = estimate_service.run_estimate(1, 1, None, True, "pytest")
    assert r["run_id"] is not None
    saved = history.get_run(r["run_id"])
    assert saved["result"]["raw_count"] == 75
    assert saved["result"]["order_count"] == 81


def test_dirty_room_rejected():
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(3, 1, None, False, "")


def test_zero_area_tile_rejected():
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 3, None, False, "")
