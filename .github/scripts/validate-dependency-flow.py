#!/usr/bin/env python3
"""
Dependency Flow Validator

Validates that imports comply with the layered architecture dependency rules:
- API can depend on Service, Domain, Repository, Core
- Service can depend on Domain, Repository, Core
- Domain can depend on Repository, Core
- Repository can depend on Core
- Core has no dependencies

Usage:
    python scripts/validate-dependency-flow.py
"""

import ast
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Define allowed dependencies for each layer
ALLOWED_DEPENDENCIES = {
    "api": {"service", "domain", "repository", "core"},
    "service": {"domain", "repository", "core"},
    "domain": {"repository", "core"},
    "repository": {"core"},
    "core": set(),  # Core has no dependencies
}

# Layers to check (in order of dependency flow)
LAYERS = ["api", "service", "domain", "repository", "core"]


def get_file_layer(file_path: Path) -> str | None:
    """Determine which layer a file belongs to based on its path."""
    parts = file_path.parts

    # Check if file is in backend directory
    if "backend" not in parts:
        return None

    backend_idx = parts.index("backend")
    if backend_idx + 1 < len(parts):
        layer = parts[backend_idx + 1]
        if layer in LAYERS:
            return layer

    return None


def extract_imports(file_path: Path) -> List[Tuple[int, str]]:
    """Extract import statements from a Python file.

    Returns:
        List of tuples (line_number, import_statement)
    """
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((node.lineno, f"import {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.names:
                    names = ", ".join(alias.name for alias in node.names)
                    imports.append((node.lineno, f"from {module} import {names}"))
                else:
                    imports.append((node.lineno, f"from {module} import *"))

    except SyntaxError as e:
        print(f"Warning: Syntax error in {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)

    return imports


def get_imported_layers(import_stmt: str) -> Set[str]:
    """Extract which layers are imported from an import statement.

    Args:
        import_stmt: Import statement string (e.g., "from domain.integrations import GAClient")

    Returns:
        Set of layer names that are imported
    """
    imported_layers = set()

    # Handle "from X import Y" statements
    if import_stmt.startswith("from "):
        parts = import_stmt.split(" import ", 1)
        if len(parts) == 2:
            module = parts[0].replace("from ", "").strip()
            # Check if it's a local import (starts with one of our layers)
            for layer in LAYERS:
                if module.startswith(layer + ".") or module == layer:
                    imported_layers.add(layer)
                    break

    # Handle "import X" statements
    elif import_stmt.startswith("import "):
        module = import_stmt.replace("import ", "").strip()
        # Handle "import X as Y" or "import X, Y"
        module = module.split(" as ")[0].split(",")[0].strip()
        for layer in LAYERS:
            if module.startswith(layer + ".") or module == layer:
                imported_layers.add(layer)
                break

    return imported_layers


def validate_dependency_flow(backend_root: Path) -> Tuple[List[str], int]:
    """Validate dependency flow for all Python files in backend.

    Returns:
        Tuple of (violations list, total violations count)
    """
    violations = []
    total_violations = 0

    # Walk through all Python files in backend
    for py_file in backend_root.rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in py_file.parts or "test" in py_file.name.lower():
            continue

        file_layer = get_file_layer(py_file)
        if not file_layer:
            continue

        # Get allowed dependencies for this layer (includes same layer)
        allowed = ALLOWED_DEPENDENCIES[file_layer] | {
            file_layer
        }  # Allow same-layer imports

        # Extract imports
        imports = extract_imports(py_file)

        # Check each import
        for line_num, import_stmt in imports:
            imported_layers = get_imported_layers(import_stmt)

            # Check if any imported layer violates the rules
            for imported_layer in imported_layers:
                if imported_layer not in allowed:
                    relative_path = py_file.relative_to(backend_root.parent)
                    violations.append(
                        f"{relative_path}:{line_num}: {file_layer.upper()} layer "
                        f"imports from {imported_layer.upper()} layer "
                        f"(allowed: {', '.join(sorted(allowed)) or 'none'})\n"
                        f"  Import: {import_stmt}"
                    )
                    total_violations += 1

    return violations, total_violations


def main():
    """Main entry point."""
    # Find backend directory (assume script is run from project root or backend directory)
    script_dir = Path(__file__).parent
    project_root = (
        script_dir.parent.parent
    )  # Go up from .cursor/skills/backend-technical-knowledge/assets/scripts

    # Try to find backend directory
    backend_root = project_root / "backend"
    if not backend_root.exists():
        # Maybe we're already in backend?
        backend_root = Path("backend")
        if not backend_root.exists():
            backend_root = Path(".")
            if not (backend_root / "api").exists():
                print("Error: Could not find backend directory", file=sys.stderr)
                sys.exit(1)

    print(f"Validating dependency flow in: {backend_root.absolute()}")
    print("=" * 70)

    violations, total = validate_dependency_flow(backend_root)

    if violations:
        print(f"\n❌ Found {total} dependency flow violation(s):\n")
        for violation in violations:
            print(violation)
            print()
        sys.exit(1)
    else:
        print("\n✅ All imports comply with dependency flow rules!")
        sys.exit(0)


if __name__ == "__main__":
    main()
