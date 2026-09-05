"""Narrow AST gate for obvious forbidden capabilities in production source.

This check intentionally scans only ``src/`` Python files. It detects direct,
obvious execution, mutation, process-control, and network-probing API usage.
It does not attempt to prove arbitrary runtime behavior, inspect user files,
or replace code review and the behavioral tests.
"""

import ast
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"

FORBIDDEN_IMPORTS = {
    "subprocess",
    "commands",
    "pty",
}
FORBIDDEN_CALLS = {
    "eval",
    "exec",
}
FORBIDDEN_ATTRIBUTE_CALLS = {
    "terminate",
    "kill",
    "send_signal",
    "rmtree",
    "unlink",
    "remove",
    "rmdir",
    "mkdir",
    "makedirs",
    "write_text",
    "write_bytes",
    "rename",
    "replace",
    "move",
    "copy",
    "copy2",
    "create_connection",
    "connect_ex",
}
FORBIDDEN_MODULE_CALLS = {
    ("os", "system"),
    ("os", "popen"),
    ("os", "kill"),
    ("os", "remove"),
    ("os", "unlink"),
    ("os", "rmdir"),
    ("os", "startfile"),
    ("os", "spawnv"),
    ("os", "spawnve"),
    ("os", "spawnvp"),
    ("os", "spawnvpe"),
    ("shutil", "rmtree"),
    ("shutil", "move"),
    ("shutil", "copy"),
    ("shutil", "copy2"),
    ("subprocess", "run"),
    ("subprocess", "Popen"),
    ("subprocess", "call"),
    ("subprocess", "check_call"),
    ("subprocess", "check_output"),
    ("socket", "create_connection"),
    ("socket", "connect_ex"),
    ("socket", "connect"),
}


def _qualified_name(node: ast.Call) -> tuple[str, str] | None:
    if not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, ast.Name):
        return None
    return node.func.value.id, node.func.attr


def scan_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    violations.append(f"{path}:{node.lineno}: forbidden import {alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] in FORBIDDEN_IMPORTS:
            violations.append(f"{path}:{node.lineno}: forbidden import {node.module}")
        elif isinstance(node, ast.Call):
            qualified = _qualified_name(node)
            if qualified in FORBIDDEN_MODULE_CALLS:
                violations.append(f"{path}:{node.lineno}: forbidden call {qualified[0]}.{qualified[1]}()")
            elif isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
                violations.append(f"{path}:{node.lineno}: forbidden call {node.func.id}()")
            elif isinstance(node.func, ast.Attribute) and node.func.attr in FORBIDDEN_ATTRIBUTE_CALLS:
                violations.append(f"{path}:{node.lineno}: forbidden call *.{node.func.attr}()")
    return violations


def main() -> None:
    violations = [violation for path in sorted(SOURCE_ROOT.rglob("*.py")) for violation in scan_file(path)]
    if violations:
        raise SystemExit("Forbidden capability gate failed:\n" + "\n".join(violations))
    print("Forbidden capability gate passed: no prohibited direct APIs found in src/")


if __name__ == "__main__":
    main()
