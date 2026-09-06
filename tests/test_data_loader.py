import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.data_loader import normalize


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, -1.0),
        (3, 0.0),
        (5, 1.0),
    ],
)
def test_normalize_maps_rating_scale_to_signed_range(value: int, expected: float) -> None:
    assert normalize(value) == expected
