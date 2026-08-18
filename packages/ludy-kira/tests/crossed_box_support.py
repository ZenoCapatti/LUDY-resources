"""Shared exact FIRE evidence and Kira projects for DY topologies 22 through 31."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from types import MappingProxyType

from symbolica import E, Expression, S

from ludy_kira.models import (
    IntegralFamily,
    KinematicInvariant,
    Kinematics,
    KiraProject,
    Propagator,
    ReductionBounds,
    ScalarProductRule,
)
from ludy_kira.parser import parse_kira2math_file

Index = tuple[int, int, int]

TARGET_INDICES: tuple[Index, ...] = tuple(
    (first, second, third)
    for first in (1, 0, -1)
    for second in (1, 0, -1)
    for third in (1, 0, -1)
)


def _source_hashes(
    topology_id: int,
    fire_input: str,
    to_reduce: str,
    table: str,
    decoded_rules: str,
    converted_rules: str,
) -> Mapping[str, str]:
    family_name = f"topo{topology_id}"
    return MappingProxyType(
        {
            "FIREinput.m": fire_input,
            "ToReduce.m": to_reduce,
            f"{family_name}.tables": table,
            "decoded-rules.m": decoded_rules,
            f"{family_name}.rules.m": converted_rules,
        }
    )


@dataclass(frozen=True, slots=True)
class CrossedBoxSpec:
    topology_id: int
    propagator_indices: tuple[int, int, int]
    master_indices: tuple[Index, ...]
    expected_zero_count: int
    expected_nontrivial_count: int
    source_sha256: Mapping[str, str]

    def __post_init__(self) -> None:
        if self.topology_id not in range(22, 32):
            raise ValueError("crossed-box topology ID must be in 22..31")
        if self.propagator_indices not in (
            (1, 2, 3),
            (1, 2, 4),
            (1, 3, 4),
            (2, 3, 4),
        ):
            raise ValueError("unexpected crossed-box propagator subset")
        if (
            len(self.master_indices)
            + self.expected_zero_count
            + self.expected_nontrivial_count
            != len(TARGET_INDICES)
        ):
            raise ValueError("masters, zeros, and nontrivial reductions must partition targets")

    @property
    def family_name(self) -> str:
        return f"topo{self.topology_id}"

    @property
    def fixture_root(self) -> Path:
        return Path(__file__).parent / "fixtures" / f"fire_{self.family_name}"

    @property
    def has_internal_mass(self) -> bool:
        return 3 in self.propagator_indices

    @property
    def kinematics_group(self) -> int:
        return (self.topology_id - 20) // 4


CROSSED_BOX_SPECS: tuple[CrossedBoxSpec, ...] = (
    CrossedBoxSpec(
        topology_id=22,
        propagator_indices=(1, 3, 4),
        master_indices=((0, 1, 0), (1, 1, 0)),
        expected_zero_count=18,
        expected_nontrivial_count=7,
        source_sha256=_source_hashes(
            22,
            "1d7dd9a70da4aa13e40eb827660f580ad3ad97df6c05680d6376af0bb4515d7e",
            "137d63ea35cc96f9b8c32c949467018e961c7e71db62456e4aaa37d9815bbc9b",
            "16f01d7cbe16055f8faa1b5bc73b47812475e9a24f67576edee7b9b7d34a7d8a",
            "fc73f4e6bef0cfc900b6abdb8672a4f0f94a17a4b8e8496cf987c6c1c4808ea1",
            "d2c6b181cb3892e2215a3b694cf79d9e5a0752415cc62dd732811260b03ac799",
        ),
    ),
    CrossedBoxSpec(
        topology_id=23,
        propagator_indices=(2, 3, 4),
        master_indices=((0, 1, 0), (1, 0, 1), (1, 1, 1)),
        expected_zero_count=16,
        expected_nontrivial_count=8,
        source_sha256=_source_hashes(
            23,
            "c292a19d7069c413be46f72b6ad70fefb7040376cc944dabfb8e18ed98a823eb",
            "aedcebb796f68ac54cef91e5165da908356f6656153be71d5c7f893b763b86ef",
            "8388442e8919f760f6165c0dd6f0b05ae086e8b16f7671b25ecba50b7f633077",
            "311dedd2f5ad5339d9c4c54d92f79574653ec6511e23efdecfd5b2fd51e5f62b",
            "b69fcc669f7bd692903566bd3bf543ba595bd7256debbd16d58fafad91fc5647",
        ),
    ),
    CrossedBoxSpec(
        topology_id=24,
        propagator_indices=(1, 2, 3),
        master_indices=((0, 0, 1), (0, 1, 1), (1, 0, 1)),
        expected_zero_count=18,
        expected_nontrivial_count=6,
        source_sha256=_source_hashes(
            24,
            "c80498f9eb78646452af758fbfee2f224ec9e36b016dea4ae3e96edd507f13f0",
            "594948af599333dd6fefc93dcdfeac9691bc6bca60362e8fe9b358d8a188a52a",
            "e4529faa1e9908b0ecc858532b057490f96ffb80c65f1071f8a9d6be7760ac43",
            "4e7da6cc05ea8855c4a4aa48d1a11afcb52017a69756130570ec24afba419247",
            "94bcf5ff8fefec521ed852bae86797ac8f6048ad301ffbed0291ed58c688485f",
        ),
    ),
    CrossedBoxSpec(
        topology_id=25,
        propagator_indices=(1, 2, 4),
        master_indices=((0, 1, 1), (1, 0, 1)),
        expected_zero_count=22,
        expected_nontrivial_count=3,
        source_sha256=_source_hashes(
            25,
            "5ff7d0985c053b9e1583247209034e266774ea7d34dab705b23ee8b48ee19d19",
            "833187caa630ec5d91dd76402ee8c6b38219d0fdabd2091fc427c7d34c4f0b6c",
            "5f903e52024e996881f5c594e2ff417cb03b78e76212aabadcc723c1e54568e2",
            "0f904cd01b32ad608e86e81cc5c5f2d0ca680cc5327bb4a1e2f96a55c7a7e5f3",
            "47a36bd2628278118a7aaaaf8b5829f7edbcdc2c6ea9b7fdb999919756eec3d7",
        ),
    ),
    CrossedBoxSpec(
        topology_id=26,
        propagator_indices=(1, 3, 4),
        master_indices=((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        expected_zero_count=16,
        expected_nontrivial_count=7,
        source_sha256=_source_hashes(
            26,
            "2d9223ced53595047e70dd3e06ca81d6851f17454e4546a2bb2dd5cd216e2025",
            "bb750c981e70ad96bb67188415d812fbca4d1257cb4b8f7bdc341b13fc493a89",
            "890dcfbefb71188755bcd5e816c7aa5fc7128da022c040f6a0de39f5b55ffd72",
            "070289c3166da4aee8f61a7b665ca459d77772efe76e0ec34229803bc9c20edd",
            "a673963193812cdeae8b7007b6b22f14205391572031935c0c1bb1697d6b3a45",
        ),
    ),
    CrossedBoxSpec(
        topology_id=27,
        propagator_indices=(2, 3, 4),
        master_indices=((0, 1, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        expected_zero_count=16,
        expected_nontrivial_count=7,
        source_sha256=_source_hashes(
            27,
            "63a33102c6bdc3d7360d936d2ca347011c0b8df68aa57ff66f508b6334a1b85d",
            "fa073dbd911f9ed39edd2843c7cd817669630a911c6fb2112a70925cd85e0807",
            "82383a3975cb50a5f93adb7dbb7d092bc26602dd9a8864b8e9346d8f496f7c3c",
            "fcaa0d83fb458d4b6efd6f0cf2d563ed56d75f273f8f8d6e2f3269679971777e",
            "1a91a0ccbcd691c387243f97a996fbf9dc2f18c201c037beaf2474a1a4af9fad",
        ),
    ),
    CrossedBoxSpec(
        topology_id=28,
        propagator_indices=(1, 2, 3),
        master_indices=((0, 0, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1)),
        expected_zero_count=16,
        expected_nontrivial_count=7,
        source_sha256=_source_hashes(
            28,
            "c9fd85fdf72cb6cc56e9a3826f96bfac01d2a02f7d9163d239b6e13ea6e896d0",
            "424354ca0d7d2f3b529c27a3aab932c71bad937cdfbcfa68601cb94b11b7bc1f",
            "6161e434db236f9134a04646b1f1175bc8febfe1008c023dcccb58145b3a4fea",
            "a1a81d82d2cab205f81f94961702fa13af5c537d9750b51a9a7655e4b357b28e",
            "fa4cfba273ad4b8a5cb5e65e95f99a2ea0be97cc8e6e2acc7cc4808f9ef5ba4b",
        ),
    ),
    CrossedBoxSpec(
        topology_id=29,
        propagator_indices=(1, 2, 4),
        master_indices=((0, 1, 1), (1, 1, 0)),
        expected_zero_count=22,
        expected_nontrivial_count=3,
        source_sha256=_source_hashes(
            29,
            "ba3348f8ea0336cbeae3d847d14e5d68680b2c6a6d6d75482db7ed113f6204dc",
            "9968f071f1c074fc1ed6e6d7eb49289a34a03891d78e789dace34a5c44bcf50c",
            "02b38c9b7d18f4577c2ad544fcaca1738fef8afd165386cbb94ed56f3c011de1",
            "de6e1c4683b31f62da78442322983ac926f3dc59d47d02596fbc96ce0e4b424d",
            "69bb6d48aa70e502e983456439f60a2421d9feeaa0f300c1449b8e0c43fbb119",
        ),
    ),
    CrossedBoxSpec(
        topology_id=30,
        propagator_indices=(1, 3, 4),
        master_indices=((0, 1, 0), (0, 1, 1), (1, 1, 0)),
        expected_zero_count=18,
        expected_nontrivial_count=6,
        source_sha256=_source_hashes(
            30,
            "14f3aef6276764c45d565494303f1943be3f1cf4c24f3b13ad8faba581e9862c",
            "446d4573966cd7f3502cf957de3821a6f385b23c92dc19fbf84a5712106a2415",
            "18e2546605e673e51f96f4375b212ea3e960b1257a0198f1361e1721b4ed27fc",
            "47d46870fc9d32bd5d47e292990a41c67987957f7d444eb703cdb1876873a4bb",
            "ac5992bece8c4047c43433f7f7b438fae80e227590f688fcd0347d59d614e265",
        ),
    ),
    CrossedBoxSpec(
        topology_id=31,
        propagator_indices=(2, 3, 4),
        master_indices=((0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)),
        expected_zero_count=16,
        expected_nontrivial_count=7,
        source_sha256=_source_hashes(
            31,
            "02fae93a5a5b768f9528a5b2c6ec738f6509310a6dbcc055d73cc957c6d8a91d",
            "d95d7e90b5b7322774f3cebb5f5478ec786c7de3d56ed2b27f0f113c4c5d52b5",
            "92db1ca64114f8cbabed180ec4400d5f5776eabd96b5e5c60304340acaad0b24",
            "115825595a5f2a1ef1f10d068324b15244dfadd92a3f570d9a745910ddd7c19d",
            "7b2d51f82ba33fe22383fc789e7656d96a0e77d4cf80b94d0e84d301acdf9cef",
        ),
    ),
)

CROSSED_BOX_SPECS_BY_ID: Mapping[int, CrossedBoxSpec] = MappingProxyType(
    {spec.topology_id: spec for spec in CROSSED_BOX_SPECS}
)


def symbolica_integral(spec: CrossedBoxSpec, indices: Index) -> str:
    return f"{spec.family_name}({','.join(map(str, indices))})"


@cache
def load_fire_rules(topology_id: int) -> Mapping[Expression, Expression]:
    spec = CROSSED_BOX_SPECS_BY_ID[topology_id]
    rules = parse_kira2math_file(
        spec.fixture_root / f"{spec.family_name}.rules.m",
        family_name=spec.family_name,
        arity=3,
    )
    for indices in spec.master_indices:
        master = E(symbolica_integral(spec, indices))
        rules.setdefault(master, master)
    return MappingProxyType(rules)


@cache
def expected_rhs(topology_id: int) -> Mapping[Index, Expression]:
    spec = CROSSED_BOX_SPECS_BY_ID[topology_id]
    rules = load_fire_rules(topology_id)
    return MappingProxyType(
        {
            indices: rules[E(symbolica_integral(spec, indices))]
            for indices in TARGET_INDICES
        }
    )


@cache
def zero_indices(topology_id: int) -> frozenset[Index]:
    return frozenset(
        indices
        for indices, right in expected_rhs(topology_id).items()
        if right == E("0")
    )


@cache
def nontrivial_indices(topology_id: int) -> frozenset[Index]:
    spec = CROSSED_BOX_SPECS_BY_ID[topology_id]
    return frozenset(TARGET_INDICES) - frozenset(spec.master_indices) - zero_indices(
        topology_id
    )


def build_project(spec: CrossedBoxSpec) -> KiraProject:
    q1, p1, p2, msq, ipp1p1, ipp1p2, ipp2p2 = S(
        "q1", "p1", "p2", "msq", "ipp1p1", "ipp1p2", "ipp2p2"
    )
    all_propagators = (
        Propagator(q1),
        Propagator(q1 - p1),
        Propagator(q1 - p1 - p2, msq),
        Propagator(q1 - p2),
    )
    family = IntegralFamily(
        name=spec.family_name,
        loop_momenta=(q1,),
        propagators=tuple(
            all_propagators[index - 1] for index in spec.propagator_indices
        ),
        top_level_sectors=(7,),
    )

    invariants: list[KinematicInvariant] = []
    if spec.has_internal_mass:
        invariants.append(KinematicInvariant(msq, 2))
    if spec.kinematics_group == 2:
        invariants.append(KinematicInvariant(ipp1p1, 2))
    invariants.append(KinematicInvariant(ipp1p2, 2))
    if spec.kinematics_group == 1:
        invariants.append(KinematicInvariant(ipp2p2, 2))

    kinematics = Kinematics(
        incoming_momenta=(p1, p2),
        kinematic_invariants=tuple(invariants),
        scalar_products=(
            ScalarProductRule(
                p1,
                p1,
                ipp1p1 if spec.kinematics_group == 2 else 0,
            ),
            ScalarProductRule(
                p2,
                p2,
                ipp2p2 if spec.kinematics_group == 1 else 0,
            ),
            ScalarProductRule(p1, p2, ipp1p2),
        ),
        symbol_to_replace_by_one=msq if spec.has_internal_mass else None,
    )
    return KiraProject(
        family=family,
        kinematics=kinematics,
        targets=tuple(family(*indices) for indices in TARGET_INDICES),
        bounds=ReductionBounds(sectors=(7,), r=9, s=4, d=2),
        preferred_masters=tuple(
            family(*indices) for indices in spec.master_indices
        ),
        check_masters=True,
        reconstruct_mass=spec.has_internal_mass,
    )


__all__ = [
    "CROSSED_BOX_SPECS",
    "CROSSED_BOX_SPECS_BY_ID",
    "TARGET_INDICES",
    "CrossedBoxSpec",
    "Index",
    "build_project",
    "expected_rhs",
    "load_fire_rules",
    "nontrivial_indices",
    "symbolica_integral",
    "zero_indices",
]
