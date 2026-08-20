from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from topo7_oracle import (
    EXPECTED_RHS,
    FIRE_SOURCE_SHA256,
    MASTER_INDICES,
    NONZERO_REDUCED_INDICES,
    PREFERRED_MASTERS,
    TARGET_INDICES,
    ZERO_INDICES,
)


def test_fire_topo7_oracle_is_a_total_partition() -> None:
    assert len(TARGET_INDICES) == 64
    assert len(MASTER_INDICES) == 2
    assert len(ZERO_INDICES) == 57
    assert len(NONZERO_REDUCED_INDICES) == 5
    assert set(EXPECTED_RHS) == set(TARGET_INDICES)
    assert MASTER_INDICES.isdisjoint(ZERO_INDICES)
    assert NONZERO_REDUCED_INDICES.isdisjoint(ZERO_INDICES)
    assert PREFERRED_MASTERS == (
        "topo7[0,1,1]",
        "topo7[1,1,0]",
    )


@pytest.mark.parametrize(("filename", "expected"), FIRE_SOURCE_SHA256.items())
def test_fire_topo7_oracle_provenance(filename: str, expected: str) -> None:
    """Detect silent drift in the self-contained copies of the FIRE sources."""

    fixture_root = Path(__file__).parent / "fixtures" / "fire_topo7"
    source = fixture_root / filename
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual == expected
