from __future__ import annotations

from pathlib import Path

import pytest
from symbolica import E, S

from kirapy.errors import IncompleteReductionError, KiraParseError
from kirapy.parser import parse_kira2math, parse_masters
from kirapy.result import ReductionResult


KIRA2MATH_SAMPLE = """\
{
(* Kira emits leading plus signs and splits rules over lines. *)
topo1[0,1,0] ->
 + 0
,
topo1[1,1,0] ->
 + topo1[1,0,0]*(1/m2)
,
topo1[1,1,-1] ->
 + topo1[1,0,0]*((-4*ipp1p2+(d)*m2)/((d)*m2))
}
"""


def _assert_exact_equal(actual, expected: str) -> None:
    delta = (actual - E(expected)).together().cancel()
    assert delta == E("0")


def test_parse_realistic_multiline_kira2math() -> None:
    rules = parse_kira2math(KIRA2MATH_SAMPLE, family_name="topo1", arity=3)

    assert len(rules) == 3
    _assert_exact_equal(rules[E("topo1(0,1,0)")], "0")
    _assert_exact_equal(rules[E("topo1(1,1,0)")], "topo1(1,0,0)/m2")
    _assert_exact_equal(
        rules[E("topo1(1,1,-1)")],
        "topo1(1,0,0)*(d*m2-4*ipp1p2)/(d*m2)",
    )


def test_parse_keeps_commas_inside_integrals_and_functions() -> None:
    rules = parse_kira2math(
        "{topo1[1,0,0] -> f[a,b]*(topo1[0,1,1]+g[x,y])}",
        family_name="topo1",
        arity=3,
    )

    assert tuple(rules) == (E("topo1(1,0,0)"),)
    assert rules[E("topo1(1,0,0)")] == E("f(a,b)*(topo1(0,1,1)+g(x,y))")


@pytest.mark.parametrize(
    "text,match",
    (
        ("topo1[1,0,0] -> 0", "must be a Mathematica list"),
        ("{topo1[1,0,0]}", "Missing top-level arrow"),
        ("{topo1[1,0,0] -> 0 -> 1}", "Multiple top-level arrows"),
        ("{topo1[1,0,0] -> (1}", "Unbalanced delimiters"),
        ("{topo1[1,0,0] -> 0 (*", "Unterminated Mathematica comment"),
    ),
)
def test_rejects_malformed_kira2math(text: str, match: str) -> None:
    with pytest.raises(KiraParseError, match=match):
        parse_kira2math(text, family_name="topo1", arity=3)


@pytest.mark.parametrize(
    "left",
    (
        "other[1,0,0]",
        "other`topo1[1,0,0]",
        "topo1[1,0]",
        "topo1[x,0,0]",
        "topo1[1/2,0,0]",
    ),
)
def test_rejects_invalid_rule_left_hand_side(left: str) -> None:
    with pytest.raises(KiraParseError):
        parse_kira2math(f"{{{left} -> 0}}", family_name="topo1", arity=3)


def test_rejects_conflicting_duplicate_rules() -> None:
    with pytest.raises(KiraParseError, match="Conflicting duplicate"):
        parse_kira2math(
            "{topo1[1,0,0] -> 0, topo1[1,0,0] -> 1}",
            family_name="topo1",
            arity=3,
        )


def test_parse_masters_strips_comments_and_deduplicates() -> None:
    masters = parse_masters(
        """
        topo1[0,1,1] # 6
        topo1[1,0,0] # 1
        topo1[1,1,1] # 7
        topo1[0,1,1] # duplicate
        """,
        family_name="topo1",
        arity=3,
    )

    assert masters == (
        E("topo1(0,1,1)"),
        E("topo1(1,0,0)"),
        E("topo1(1,1,1)"),
    )


@pytest.mark.parametrize(
    "master",
    (
        "other[1,0,0]",
        "other`topo1[1,0,0]",
        "topo1[1,0]",
        "topo1[x,0,0]",
    ),
)
def test_rejects_invalid_master(master: str) -> None:
    with pytest.raises(KiraParseError):
        parse_masters(master, family_name="topo1", arity=3)


def test_result_synthesizes_master_identities_and_applies_rules(tmp_path: Path) -> None:
    target = E("topo1(1,1,0)")
    master = E("topo1(1,0,0)")
    result = ReductionResult(
        family_name="topo1",
        arity=3,
        requested_targets=(target, master),
        rules={target: master / S("m2")},
        masters=(master,),
        workdir=tmp_path,
    )

    assert result.complete
    assert result.rules[master] == master
    assert result.apply(2 * target + master) == 2 * master / S("m2") + master


def test_result_reports_missing_and_unresolved_integrals(tmp_path: Path) -> None:
    target = E("topo1(1,1,0)")
    unresolved = E("topo1(0,1,1)")
    missing = E("topo1(-1,1,1)")
    result = ReductionResult(
        family_name="topo1",
        arity=3,
        requested_targets=(target, missing),
        rules={target: unresolved},
        masters=(),
        workdir=tmp_path,
    )

    assert not result.complete
    assert result.missing_targets == (missing,)
    assert result.unresolved_integrals == (unresolved,)
    with pytest.raises(IncompleteReductionError) as caught:
        result.require_complete()
    assert caught.value.missing_targets == (missing,)
    assert caught.value.unresolved_integrals == (unresolved,)


def test_result_does_not_treat_a_namespaced_basename_as_its_family(
    tmp_path: Path,
) -> None:
    target = E("topo1(1,1,1)")
    foreign = S("other::topo1")(0, 1, 1)
    result = ReductionResult(
        family_name="topo1",
        arity=3,
        requested_targets=(target,),
        rules={target: foreign},
        masters=(),
        workdir=tmp_path,
    )

    assert result.complete
    assert result.unresolved_integrals == ()
    assert result.apply(foreign) == foreign


def test_apply_rejects_unknown_integrals_by_default(tmp_path: Path) -> None:
    known = E("topo1(1,0,0)")
    unknown = E("topo1(2,0,0)")
    result = ReductionResult(
        family_name="topo1",
        arity=3,
        requested_targets=(known,),
        rules={},
        masters=(known,),
        workdir=tmp_path,
    )

    with pytest.raises(IncompleteReductionError, match="absent"):
        result.apply(known + unknown)
    assert result.apply(known + unknown, allow_incomplete=True) == known + unknown
