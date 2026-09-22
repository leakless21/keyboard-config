"""
Shared validation helpers and structured parser loaders.

Provides standard failure handling, assertions, and robust JSON/YAML/TOML
loaders for all repository validation scripts.
"""

from __future__ import annotations

import json
import sys
import tomllib
from collections.abc import Container
from pathlib import Path
from typing import Any, NoReturn

try:
    import yaml
except ImportError:
    yaml = None


def fail(msg: str) -> NoReturn:
    """Print failure message and exit with non-zero exit code."""
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def load_json(path: Path) -> Any:
    """Load and parse JSON file."""
    if not path.exists():
        fail(f"JSON file not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"Failed to parse JSON file {path}: {e}")


def load_yaml(path: Path) -> Any:
    """Load and parse YAML file using PyYAML."""
    if yaml is None:
        fail("PyYAML is required for YAML parsing. Run via 'uv run ...' or install via 'uv sync'.")
    if not path.exists():
        fail(f"YAML file not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        fail(f"Failed to parse YAML file {path}: {e}")


def load_toml(path: Path) -> dict[str, Any]:
    """Load and parse TOML file using the standard-library tomllib."""
    if not path.exists():
        fail(f"TOML file not found: {path}")
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        fail(f"Failed to parse TOML file {path}: {e}")


def assert_eq(actual: Any, expected: Any, msg: str | None = None) -> None:
    """Assert actual equals expected."""
    if actual != expected:
        detail = msg or f"Expected {expected!r}, got {actual!r}"
        fail(detail)


def assert_in(item: Any, container: Container, msg: str | None = None) -> None:
    """Assert item is in container."""
    if item not in container:
        detail = msg or f"Expected {item!r} in container"
        fail(detail)


def assert_true(condition: bool, msg: str) -> None:
    """Assert condition is True."""
    if not condition:
        fail(msg)


def is_exactly_true(value: Any) -> bool:
    """Return True only for the boolean ``True``.

    Config validation needs more strictness than plain truthiness: a TOML ``1`` or a
    YAML ``"true"`` string must not satisfy a boolean contract. ``isinstance`` keeps
    that exactness without an identity comparison against a literal.
    """
    return isinstance(value, bool) and value


def is_exactly_false(value: Any) -> bool:
    """Return True only for the boolean ``False`` (rejects 0, None, and "")."""
    return isinstance(value, bool) and not value
