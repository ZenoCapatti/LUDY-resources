"""Integrity checks for the official DIS ancillary integrands.

The public arXiv files are intentionally not downloaded on import.  They are
large source fixtures, not reduction tables, and callers must opt in to
fetching them.  This module verifies the exact v1 bytes and the documented
association inventory before any downstream parser treats them as evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping
from urllib.request import urlopen


@dataclass(frozen=True, slots=True)
class AncillarySpec:
    """Immutable provenance and inventory for one arXiv source fixture."""

    filename: str
    url: str
    sha256: str
    byte_count: int
    line_count: int
    embeddings: int
    a1_records: int
    a2_records: int

    @property
    def rooted_records(self) -> int:
        return self.a1_records + self.a2_records


ANCILLARY_SPECS: Mapping[str, AncillarySpec] = MappingProxyType(
    {
        "DT": AncillarySpec(
            filename="dataDT.m",
            url="https://arxiv.org/src/2506.16489v1/anc/dataDT.m",
            sha256=(
                "bea50339af20ec52cb52ddd620b3eebad"
                "ba080f8ad6eed18d60312b225e8224b"
            ),
            byte_count=301_518,
            line_count=449,
            embeddings=20,
            a1_records=12,
            a2_records=20,
        ),
        "SE": AncillarySpec(
            filename="dataSE.m",
            url="https://arxiv.org/src/2506.16489v1/anc/dataSE.m",
            sha256=(
                "2cd5e6b0e8337ed1036079f493eca11"
                "e920df18c0c2dcd578908ea66b89f2b60"
            ),
            byte_count=241_701,
            line_count=741,
            embeddings=34,
            a1_records=26,
            a2_records=26,
        ),
    }
)


_KEY_PATTERNS = MappingProxyType(
    {
        "embedding": re.compile(r'^\s*"embedding"\s*->', re.MULTILINE),
        "a1": re.compile(r'^\s*"a1"\s*->', re.MULTILINE),
        "a2": re.compile(r'^\s*"a2"\s*->', re.MULTILINE),
        "cut_content": re.compile(r'^\s*"Cut content"\s*->', re.MULTILINE),
        "denominator": re.compile(r'^\s*"Denominator"\s*->', re.MULTILINE),
        "numerator": re.compile(r'^\s*"Numerator"\s*->', re.MULTILINE),
        "F2": re.compile(r'^\s*"F2"\s*->', re.MULTILINE),
        "FL": re.compile(r'^\s*"FL"\s*->', re.MULTILINE),
        "zero": re.compile(r'^\s*"zero"\s*->', re.MULTILINE),
    }
)


@dataclass(frozen=True, slots=True)
class AncillaryAudit:
    """Exact-byte and structural audit of one ancillary file."""

    spec: AncillarySpec
    actual_sha256: str
    actual_bytes: int
    actual_lines: int
    counts: Mapping[str, int]

    @property
    def failures(self) -> tuple[str, ...]:
        expected_records = self.spec.rooted_records
        expected_counts = {
            "embedding": self.spec.embeddings,
            "a1": self.spec.a1_records,
            "a2": self.spec.a2_records,
            "cut_content": expected_records,
            "denominator": expected_records,
            "numerator": expected_records,
            "F2": expected_records,
            "FL": expected_records,
            "zero": expected_records,
        }
        failures: list[str] = []
        if self.actual_sha256 != self.spec.sha256:
            failures.append("SHA-256 differs from the pinned arXiv v1 source")
        if self.actual_bytes != self.spec.byte_count:
            failures.append("byte count differs from the pinned source")
        if self.actual_lines != self.spec.line_count:
            failures.append("line count differs from the pinned source")
        for key, expected in expected_counts.items():
            actual = self.counts.get(key, 0)
            if actual != expected:
                failures.append(f"{key} count is {actual}, expected {expected}")
        return tuple(failures)

    @property
    def valid(self) -> bool:
        return not self.failures

    def require_valid(self) -> None:
        """Raise with all discrepancies rather than accepting partial data."""

        if self.failures:
            raise ValueError("; ".join(self.failures))


def audit_ancillary_bytes(data: bytes, spec: AncillarySpec) -> AncillaryAudit:
    """Check exact provenance and the documented association inventory."""

    text = data.decode("utf-8")
    counts = MappingProxyType(
        {name: len(pattern.findall(text)) for name, pattern in _KEY_PATTERNS.items()}
    )
    return AncillaryAudit(
        spec=spec,
        actual_sha256=sha256(data).hexdigest(),
        actual_bytes=len(data),
        # Match the source inventory's POSIX ``wc -l`` convention.  Both
        # ancillary files end in a final non-newline line, so ``splitlines``
        # would report one more logical fragment than the pinned count.
        actual_lines=data.count(b"\n"),
        counts=counts,
    )


def audit_ancillary_file(path: str | Path, spec: AncillarySpec) -> AncillaryAudit:
    """Read and audit an explicitly supplied local fixture."""

    return audit_ancillary_bytes(Path(path).read_bytes(), spec)


def fetch_ancillary(
    spec: AncillarySpec,
    destination_directory: str | Path,
    *,
    timeout: float = 60.0,
) -> tuple[Path, AncillaryAudit]:
    """Download one pinned fixture atomically and reject changed bytes.

    This is the only network-writing operation in the DIS source layer.  It is
    never called by an import or notebook evaluation without an explicit user
    action.
    """

    destination = Path(destination_directory) / spec.filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(spec.url, timeout=timeout) as response:  # noqa: S310
        data = response.read()
    audit = audit_ancillary_bytes(data, spec)
    audit.require_valid()
    temporary = destination.with_suffix(destination.suffix + ".download")
    temporary.write_bytes(data)
    temporary.replace(destination)
    return destination, audit


def self_check() -> None:
    """Validate the immutable two-file inventory without network access."""

    assert set(ANCILLARY_SPECS) == {"DT", "SE"}
    assert sum(spec.embeddings for spec in ANCILLARY_SPECS.values()) == 54
    assert sum(spec.rooted_records for spec in ANCILLARY_SPECS.values()) == 84
    assert all(len(spec.sha256) == 64 for spec in ANCILLARY_SPECS.values())


__all__ = [
    "ANCILLARY_SPECS",
    "AncillaryAudit",
    "AncillarySpec",
    "audit_ancillary_bytes",
    "audit_ancillary_file",
    "fetch_ancillary",
    "self_check",
]
