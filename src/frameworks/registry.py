from __future__ import annotations

from pathlib import Path

import yaml

from src.frameworks.base import ComplianceFramework, Control


class YAMLFramework(ComplianceFramework):
    def get_controls(self) -> list[Control]:
        return self.controls


def load_framework_from_yaml(path: Path) -> ComplianceFramework:
    with open(path) as f:
        data = yaml.safe_load(f)
    controls = [
        Control(
            id=c["id"],
            title=c["title"],
            description=c.get("description", ""),
            category=c.get("category", ""),
        )
        for c in data.get("controls", [])
    ]
    return YAMLFramework(
        name=data["name"],
        version=data.get("version", "1.0"),
        description=data.get("description", ""),
        controls=controls,
    )


def discover_frameworks(frameworks_dir: Path) -> dict[str, ComplianceFramework]:
    registry = {}
    for yaml_file in sorted(frameworks_dir.glob("*.yaml")):
        fw = load_framework_from_yaml(yaml_file)
        registry[fw.name] = fw
    return registry
