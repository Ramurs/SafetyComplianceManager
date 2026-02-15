from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Control:
    id: str
    title: str
    description: str = ""
    category: str = ""


@dataclass
class ComplianceFramework(ABC):
    name: str
    version: str
    description: str
    controls: list[Control] = field(default_factory=list)

    @abstractmethod
    def get_controls(self) -> list[Control]:
        ...

    def get_controls_by_category(self, category: str) -> list[Control]:
        return [c for c in self.get_controls() if c.category == category]

    def get_categories(self) -> list[str]:
        return sorted(set(c.category for c in self.get_controls() if c.category))
