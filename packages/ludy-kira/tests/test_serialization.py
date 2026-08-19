from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest
import yaml
from symbolica import E, Expression, S

from ludy_kira.errors import KiraConfigurationError
from ludy_kira.models import IntegralFamily, KiraProject
from ludy_kira.serialization import _MomentumAdapter, serialize_project
from topo1_oracle import PREFERRED_MASTERS, TARGET_INDICES, wolfram_integral


def test_momentum_adapter_unwraps_structured_expression_subclasses() -> None:
    inner_by_id: dict[int, Expression] = {}

    class StructuredExpression(Expression):
        def __new__(cls, inner: Expression) -> StructuredExpression:
            value = cast(StructuredExpression, super().__new__(cls))
            inner_by_id[id(value)] = inner
            return value

        def to_expression(self) -> Expression:
            return inner_by_id[id(self)]

        def __iter__(self):
            return iter(())

    representation = S("spenso::wrapped_test_representation")(S("D"))
    atom = S("spenso_python::wrapped_test_p")(7, representation)
    structured = StructuredExpression(atom)

    momentum = _MomentumAdapter._inspect(structured)
    adapter = _MomentumAdapter((structured,))

    assert momentum.expression is structured
    assert momentum.name == "wrapped_test_p7"
    assert momentum.representation is not None
    assert adapter.name(structured) == "wrapped_test_p7"
    assert adapter.linear(structured) == "wrapped_test_p7"


def test_topo1_serialization_matches_kira_schema(topo1_project: KiraProject) -> None:
    files = serialize_project(topo1_project)

    assert set(files) == {
        "config/integralfamilies.yaml",
        "config/kinematics.yaml",
        "jobs.yaml",
        "preferred_masters",
        "targets",
    }
    assert dict(files.invariant_aliases) == {"m2": "m^2"}
    assert yaml.safe_load(files["config/integralfamilies.yaml"]) == {
        "integralfamilies": [
            {
                "name": "topo1",
                "loop_momenta": ["q1"],
                "top_level_sectors": ["b111"],
                "propagators": [
                    ["q1", "m2"],
                    ["-p1+q1", "0"],
                    ["-p2+q1", "0"],
                ],
            }
        ]
    }
    assert yaml.safe_load(files["config/kinematics.yaml"]) == {
        "kinematics": {
            "incoming_momenta": ["p1", "p2"],
            "outgoing_momenta": [],
            "kinematic_invariants": [["m2", 2], ["ipp1p2", 2]],
            "scalarproduct_rules": [
                [["p1", "p1"], "0"],
                [["p2", "p2"], "0"],
                [["p1", "p2"], "ipp1p2"],
            ],
            "symbol_to_replace_by_one": "m2",
        }
    }
    assert yaml.safe_load(files["jobs.yaml"]) == {
        "jobs": [
            {
                "reduce_sectors": {
                    "reduce": [{"sectors": ["b111"], "r": 9, "s": 4, "d": 2}],
                    "select_integrals": {
                        "select_mandatory_list": [["topo1", "targets"]]
                    },
                    "preferred_masters": "preferred_masters",
                    "check_masters": True,
                    "run_initiate": True,
                    "run_triangular": True,
                    "run_back_substitution": True,
                }
            },
            {
                "kira2math": {
                    "target": [["topo1", "targets"]],
                    "reconstruct_mass": True,
                }
            },
        ]
    }
    assert files["targets"].splitlines() == [
        wolfram_integral(indices) for indices in TARGET_INDICES
    ]
    assert files["preferred_masters"].splitlines() == list(PREFERRED_MASTERS)


def test_zero_sectors_belong_to_integralfamilies_not_jobs(topo1_project: KiraProject) -> None:
    family = replace(topo1_project.family, zero_sectors=(1, 2))
    files = serialize_project(replace(topo1_project, family=family))

    family_yaml = yaml.safe_load(files["config/integralfamilies.yaml"])
    jobs_yaml = yaml.safe_load(files["jobs.yaml"])
    assert family_yaml["integralfamilies"][0]["zero_sectors"] == ["b001", "b010"]
    assert "set_zero_sectors" not in jobs_yaml["jobs"][0]["reduce_sectors"]


def test_check_masters_requires_a_preferred_list(topo1_project: KiraProject) -> None:
    project = replace(topo1_project, preferred_masters=())

    with pytest.raises(KiraConfigurationError, match="check_masters requires"):
        serialize_project(project)


@pytest.mark.parametrize("sector", (0, 8, -1))
def test_sector_must_fit_propagator_width(
    topo1_project: KiraProject,
    sector: int,
) -> None:
    bounds = replace(topo1_project.bounds, sectors=(sector,))

    with pytest.raises(KiraConfigurationError, match="does not fit"):
        serialize_project(replace(topo1_project, bounds=bounds))


def test_rejects_a_target_from_another_family(topo1_project: KiraProject) -> None:
    other = S("other")(1, 1, 1)

    with pytest.raises(KiraConfigurationError, match="Expected an integral in family topo1"):
        serialize_project(replace(topo1_project, targets=(other,)))


def test_rejects_wrong_integral_arity(topo1_project: KiraProject) -> None:
    malformed = S("topo1")(1, 1)

    with pytest.raises(KiraConfigurationError, match="3 are required"):
        serialize_project(replace(topo1_project, targets=(malformed,)))


def test_cut_propagators_are_one_based_and_in_range(topo1_project: KiraProject) -> None:
    invalid_family = IntegralFamily(
        name=topo1_project.family.name,
        loop_momenta=topo1_project.family.loop_momenta,
        propagators=topo1_project.family.propagators,
        top_level_sectors=topo1_project.family.top_level_sectors,
        cut_propagators=(0, 4),
    )

    with pytest.raises(KiraConfigurationError, match="cut_propagators"):
        serialize_project(replace(topo1_project, family=invalid_family))
