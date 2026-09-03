import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (
    PROJECT_ROOT / "splitting_kernels",
    PROJECT_ROOT / "notebooks",
)


def test_no_forbidden_expression_backends_or_regex_imports() -> None:
    forbidden_roots = {"re", "sympy"}
    for source_root in SOURCE_ROOTS:
        if not source_root.exists():
            continue
        for path in source_root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="ascii"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = {alias.name.split(".")[0] for alias in node.names}
                    assert forbidden_roots.isdisjoint(imported), path
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_root = node.module.split(".")[0]
                    assert imported_root not in forbidden_roots, path
