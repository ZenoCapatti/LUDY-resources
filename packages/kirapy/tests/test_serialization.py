from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace
from typing import cast

import pytest
import yaml
from symbolica import E, Expression, S

import kirapy.serialization as serialization
from kirapy.errors import KiraConfigurationError
from kirapy.models import IntegralFamily, KinematicInvariant, KiraProject
from kirapy.serialization import (
    _MomentumAdapter,
    _alias_digest,
    _alias_wire_name,
    serialize_project,
)
from topo1_oracle import TARGET_INDICES


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

    assert momentum.expression == atom
    assert momentum.representation is not None
    assert adapter._momenta[0].expression == atom


def test_topo1_serialization_matches_kira_schema(topo1_project: KiraProject) -> None:
    files = serialize_project(topo1_project)

    assert set(files) == {
        "config/integralfamilies.yaml",
        "config/kinematics.yaml",
        "jobs.yaml",
        "preferred_masters",
        "targets",
    }
    aliases = {record.original: record for record in files._alias_records}
    family_alias = aliases[S(topo1_project.family.name)]
    q1 = topo1_project.family.loop_momenta[0]
    p1, p2 = topo1_project.kinematics.incoming_momenta
    m2 = topo1_project.kinematics.kinematic_invariants[0].expression
    ipp1p2 = topo1_project.kinematics.kinematic_invariants[1].expression

    assert set(files.symbol_aliases.values()) == set(aliases)
    assert family_alias.wire_name.startswith("kp_f_")
    assert len(family_alias.wire_name) == len("kp_f_") + 64
    assert family_alias.wire.get_symbol_data("kirapy::original") == S("topo1")
    assert "kirapy::alias" in family_alias.wire.get_tags()
    assert yaml.safe_load(files["config/integralfamilies.yaml"]) == {
        "integralfamilies": [
            {
                "name": family_alias.wire_name,
                "loop_momenta": [aliases[q1].wire_name],
                "top_level_sectors": ["b111"],
                "propagators": [
                    [aliases[q1].wire_name, aliases[m2].wire_name],
                    [f"{aliases[q1].wire_name}-{aliases[p1].wire_name}", "0"],
                    [f"{aliases[q1].wire_name}-{aliases[p2].wire_name}", "0"],
                ],
            }
        ]
    }
    assert yaml.safe_load(files["config/kinematics.yaml"]) == {
        "kinematics": {
            "incoming_momenta": [aliases[p1].wire_name, aliases[p2].wire_name],
            "outgoing_momenta": [],
            "kinematic_invariants": [
                [aliases[m2].wire_name, 2],
                [aliases[ipp1p2].wire_name, 2],
            ],
            "scalarproduct_rules": [
                [[aliases[p1].wire_name, aliases[p1].wire_name], "0"],
                [[aliases[p2].wire_name, aliases[p2].wire_name], "0"],
                [
                    [aliases[p1].wire_name, aliases[p2].wire_name],
                    aliases[ipp1p2].wire_name,
                ],
            ],
            "symbol_to_replace_by_one": aliases[m2].wire_name,
        }
    }
    assert yaml.safe_load(files["jobs.yaml"]) == {
        "jobs": [
            {
                "reduce_sectors": {
                    "reduce": [{"sectors": ["b111"], "r": 9, "s": 4, "d": 2}],
                    "select_integrals": {
                        "select_mandatory_list": [
                            [family_alias.wire_name, "targets"]
                        ]
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
                    "target": [[family_alias.wire_name, "targets"]],
                    "reconstruct_mass": True,
                }
            },
        ]
    }
    assert files["targets"].splitlines() == [
        f"{family_alias.wire_name}[{','.join(map(str, indices))}]"
        for indices in TARGET_INDICES
    ]
    assert files["preferred_masters"].splitlines() == [
        f"{family_alias.wire_name}[1,1,1]",
        f"{family_alias.wire_name}[0,1,1]",
        f"{family_alias.wire_name}[1,0,0]",
    ]


def test_scalar_wire_aliases_fit_fermats_identifier_bound(
    topo1_project: KiraProject,
) -> None:
    files = serialize_project(topo1_project)
    invariants = [
        alias for alias in files._alias_records if alias.kind == "invariant"
    ]

    assert invariants
    assert all(len(alias.digest) == 64 for alias in invariants)
    assert all(
        alias.wire.get_symbol_data("kirapy::digest") == alias.digest
        for alias in invariants
    )
    assert all(len(alias.wire_name) <= 10 for alias in invariants)
    assert all(alias.wire_name[0].islower() for alias in invariants)
    assert all(alias.wire_name.islower() for alias in invariants)
    assert all(
        alias.wire_name == _alias_wire_name("invariant", alias.digest)
        for alias in invariants
    )


def test_scalar_wire_alias_collisions_are_rejected_against_full_digests(
    topo1_project: KiraProject,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, second = (S("fermat_collision_first"), S("fermat_collision_second"))
    first_digest = "0" * 64
    second_digest = f"{serialization._FERMAT_ALIAS_MODULUS:064x}"
    assert first_digest != second_digest
    assert _alias_wire_name("invariant", first_digest) == _alias_wire_name(
        "invariant", second_digest
    )
    real_alias_digest = _alias_digest

    def colliding_digest(kind: str, original: Expression) -> str:
        if kind == "invariant" and original == first:
            return first_digest
        if kind == "invariant" and original == second:
            return second_digest
        return real_alias_digest(kind, original)

    monkeypatch.setattr(serialization, "_alias_digest", colliding_digest)
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=(
            KinematicInvariant(first, 2),
            KinematicInvariant(second, 2),
        ),
        scalar_products=(),
        symbol_to_replace_by_one=None,
    )

    with pytest.raises(KiraConfigurationError, match="wire-name collision"):
        serialize_project(replace(topo1_project, kinematics=kinematics))


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


def test_project_requires_at_least_one_target(topo1_project: KiraProject) -> None:
    with pytest.raises(KiraConfigurationError, match="[Aa]t least one target"):
        serialize_project(replace(topo1_project, targets=()))


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


def test_rejects_a_namespaced_head_with_the_same_family_basename(
    topo1_project: KiraProject,
) -> None:
    other = S("other::topo1")(1, 1, 1)

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


@pytest.mark.skipif(
    not os.environ.get("SYMBOLICA_LICENSE"),
    reason="subprocess Symbolica tests require a multi-core license",
)
def test_alias_digest_is_stable_across_symbol_registration_orders() -> None:
    script = """
from symbolica import E, S
from kirapy.serialization import _alias_digest
for name in {names!r}:
    S(name)
print(_alias_digest("invariant", E("x^2+y")))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src"
    first = subprocess.run(
        [sys.executable, "-c", script.format(names=["junk_a", "junk_b"])],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    second = subprocess.run(
        [sys.executable, "-c", script.format(names=["junk_b", "junk_c", "junk_a"])],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert first == second == _alias_digest("invariant", E("x^2+y"))


@pytest.mark.skipif(
    not os.environ.get("SYMBOLICA_LICENSE"),
    reason="subprocess Symbolica tests require a multi-core license",
)
def test_scalar_text_is_stable_across_symbol_registration_orders() -> None:
    script = """
from symbolica import S
from kirapy.serialization import _scalar
for name in {names!r}:
    S(name)
x, y, z = S("scalar_order_x", "scalar_order_y", "scalar_order_z")
print(_scalar((z / x - x * y) / 2, context="test scalar"))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = "src"
    outputs = {
        subprocess.run(
            [sys.executable, "-c", script.format(names=names)],
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        for names in (
            ["scalar_order_x", "scalar_order_y", "scalar_order_z"],
            ["scalar_order_z", "scalar_order_y", "scalar_order_x"],
        )
    }

    assert outputs == {
        "1/2*(-scalar_order_x*scalar_order_y+scalar_order_z/scalar_order_x)"
    }


def test_scalar_text_parenthesizes_a_nonatomic_exponent() -> None:
    base = S("scalar_power_base")
    dimension = S("scalar_power_dimension")

    assert serialization._scalar(
        base ** (dimension - 2),
        context="test scalar power",
    ) == "scalar_power_base^(-2+scalar_power_dimension)"
    assert serialization._scalar(
        base ** (dimension / 2),
        context="test scalar power",
    ) == "scalar_power_base^(1/2*scalar_power_dimension)"


def test_native_expressions_cannot_use_the_wire_prefix(
    topo1_project: KiraProject,
) -> None:
    reserved = S("kp_native_source")
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=(KinematicInvariant(reserved, 2),),
        scalar_products=(),
        symbol_to_replace_by_one=None,
    )

    with pytest.raises(KiraConfigurationError, match="reserved Kira wire names"):
        serialize_project(replace(topo1_project, kinematics=kinematics))


def test_preexisting_plain_wire_symbol_is_rejected(
    topo1_project: KiraProject,
) -> None:
    original = S("alias_conflict_native")
    digest = _alias_digest("invariant", original)
    S(_alias_wire_name("invariant", digest))
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=(KinematicInvariant(original, 2),),
        scalar_products=(),
        symbol_to_replace_by_one=None,
    )

    with pytest.raises(KiraConfigurationError, match="incompatible metadata"):
        serialize_project(replace(topo1_project, kinematics=kinematics))


def test_preexisting_alias_with_a_custom_wire_printer_is_rejected(
    topo1_project: KiraProject,
) -> None:
    original = S("alias_custom_print_native")
    digest = _alias_digest("invariant", original)
    wire_name = _alias_wire_name("invariant", digest)

    def misleading_printer(_expression, **_options):
        return "not_the_wire_name"

    S(
        wire_name,
        tags=["kirapy::alias"],
        data={
            "kirapy::original": original,
            "kirapy::kind": "invariant",
            "kirapy::digest": digest,
        },
        print=misleading_printer,
    )
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=(KinematicInvariant(original, 2),),
        scalar_products=(),
        symbol_to_replace_by_one=None,
    )

    with pytest.raises(KiraConfigurationError, match="does not render as its wire name"):
        serialize_project(replace(topo1_project, kinematics=kinematics))


def test_scalar_serialization_rejects_undeclared_function_heads(
    topo1_project: KiraProject,
) -> None:
    invariant = S("scalar_function_invariant")
    unsupported = S("scalar_function_head")(invariant)
    family = replace(
        topo1_project.family,
        propagators=(
            replace(topo1_project.family.propagators[0], mass_squared=unsupported),
            *topo1_project.family.propagators[1:],
        ),
    )
    kinematics = replace(
        topo1_project.kinematics,
        kinematic_invariants=(KinematicInvariant(invariant, 2),),
        scalar_products=(),
        symbol_to_replace_by_one=None,
    )

    with pytest.raises(KiraConfigurationError, match="unsupported scalar function"):
        serialize_project(
            replace(topo1_project, family=family, kinematics=kinematics)
        )


def test_custom_dimension_does_not_capture_an_unrelated_native_d(
    topo1_project: KiraProject,
) -> None:
    epsilon = S("dimension_capture_epsilon")
    family = replace(
        topo1_project.family,
        propagators=(
            replace(topo1_project.family.propagators[0], mass_squared=S("d")),
            *topo1_project.family.propagators[1:],
        ),
    )

    with pytest.raises(KiraConfigurationError, match="reserved d symbol"):
        serialize_project(
            replace(
                topo1_project,
                family=family,
                dimension=4 - 2 * epsilon,
            )
        )


def test_custom_dimension_cannot_itself_contain_the_reserved_d(
    topo1_project: KiraProject,
) -> None:
    with pytest.raises(KiraConfigurationError, match="custom project dimension"):
        serialize_project(replace(topo1_project, dimension=4 - 2 * S("d")))
