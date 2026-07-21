#!/usr/bin/env python3
"""Build the canonical OpenAPI JSON file served by Mintlify."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = [
    ROOT / "openapi" / "openapi-deals.yaml",
    ROOT / "openapi" / "openapi-companies.yaml",
    ROOT / "openapi" / "openapi-investors.yaml",
    ROOT / "openapi" / "openapi-people.yaml",
    ROOT / "openapi" / "openapi-alerts.yaml",
    ROOT / "openapi" / "openapi-other.yaml",
]
OUTPUT_FILES = [
    ROOT / "openapi.json",
    ROOT / "api-reference" / "openapi.json",
]


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_prefix(path: Path) -> str:
    stem = path.stem.removeprefix("openapi-")
    return "".join(part.capitalize() for part in stem.replace("_", "-").split("-"))


def replace_schema_refs(value: Any, rename_map: dict[str, str]) -> Any:
    if isinstance(value, dict):
        updated = {}
        for key, child in value.items():
            if key == "$ref" and isinstance(child, str):
                prefix = "#/components/schemas/"
                if child.startswith(prefix):
                    name = child.removeprefix(prefix)
                    child = prefix + rename_map.get(name, name)
            updated[key] = replace_schema_refs(child, rename_map)
        return updated
    if isinstance(value, list):
        return [replace_schema_refs(child, rename_map) for child in value]
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open() as file:
        return yaml.safe_load(file)


def main() -> None:
    combined: dict[str, Any] = {
        "openapi": "3.0.3",
        "info": {
            "title": "Fundable API",
            "description": (
                "Canonical OpenAPI specification for the Fundable API. "
                "This file bundles the Deals, Companies, Investors, People, "
                "Alerts, Location, and Industry endpoints."
            ),
            "version": "2.0.0",
            "contact": {
                "name": "Fundable API Support",
                "url": "mailto:jacob@tryfundable.ai",
            },
            "license": {
                "name": "Proprietary",
                "url": "https://www.tryfundable.ai/terms/privacy/",
            },
        },
        "servers": [
            {
                "url": "https://www.tryfundable.ai/api/v1",
                "description": "Production server",
            }
        ],
        "security": [{"bearerAuth": []}],
        "paths": {},
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "API Key",
                    "description": "API key provided as a Bearer token",
                }
            },
            "schemas": {},
        },
        "tags": [],
        "x-sourceSpecs": [f"/openapi/{path.name}" for path in SOURCE_FILES],
    }

    schema_hashes: dict[str, str] = {}
    tag_names: set[str] = set()

    for path in SOURCE_FILES:
        spec = load_yaml(path)
        rename_map: dict[str, str] = {}
        prefix = source_prefix(path)
        pending_schemas: list[tuple[str, dict[str, Any], str]] = []

        for name, schema in spec.get("components", {}).get("schemas", {}).items():
            schema_copy = copy.deepcopy(schema)
            schema_digest = digest(schema_copy)
            if name not in combined["components"]["schemas"]:
                target_name = name
            elif schema_hashes[name] == schema_digest:
                target_name = name
            else:
                target_name = f"{prefix}{name}"
                counter = 2
                while target_name in combined["components"]["schemas"]:
                    target_name = f"{prefix}{name}{counter}"
                    counter += 1

            rename_map[name] = target_name
            pending_schemas.append((target_name, schema_copy, schema_digest))

        for target_name, schema_copy, schema_digest in pending_schemas:
            if target_name not in combined["components"]["schemas"]:
                combined["components"]["schemas"][target_name] = replace_schema_refs(
                    schema_copy, rename_map
                )
                schema_hashes[target_name] = schema_digest

        for route, path_item in spec.get("paths", {}).items():
            if route in combined["paths"]:
                raise ValueError(f"Duplicate path in source specs: {route}")
            combined["paths"][route] = replace_schema_refs(copy.deepcopy(path_item), rename_map)

        for tag in spec.get("tags", []):
            name = tag.get("name")
            if name and name not in tag_names:
                combined["tags"].append(copy.deepcopy(tag))
                tag_names.add(name)

    contents = json.dumps(combined, indent=2) + "\n"
    for output_file in OUTPUT_FILES:
        output_file.write_text(contents)
        print(f"Wrote {output_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
