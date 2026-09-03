from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from topo1_oracle import (
    EXPECTED_RHS,
    FIRE_SOURCE_SHA256,
    MASTER_INDICES,
    PREFERRED_MASTERS,
    TARGET_INDICES,
    ZERO_INDICES,
)


def test_fire_oracle_is_a_total_partition() -> None:
    nonzero_reduced = set(TARGET_INDICES) - MASTER_INDICES - ZERO_INDICES

    assert len(TARGET_INDICES) == 27
    assert len(MASTER_INDICES) == 3
    assert len(ZERO_INDICES) == 16
    assert len(nonzero_reduced) == 8
    assert set(EXPECTED_RHS) == set(TARGET_INDICES)
    assert MASTER_INDICES.isdisjoint(ZERO_INDICES)
    assert PREFERRED_MASTERS == (
        "topo1[1,1,1]",
        "topo1[0,1,1]",
        "topo1[1,0,0]",
    )


@pytest.mark.parametrize(("filename", "expected"), FIRE_SOURCE_SHA256.items())
def test_fire_oracle_provenance(filename: str, expected: str) -> None:
    """Detect silent drift in the self-contained copies of the FIRE sources."""

    fixture_root = Path(__file__).parent / "fixtures" / "fire_topo1"
    source = fixture_root / filename
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    assert actual == expected
