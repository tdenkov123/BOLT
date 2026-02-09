from __future__ import annotations

from typing import Dict

from core.BaseFunctionBlock import BaseFunctionBlock


class FBContainer:
    def __init__(self):
        self._blocks: Dict[str, BaseFunctionBlock] = {}

    def add_fb(self, fb: BaseFunctionBlock) -> None:
        if fb._name in self._blocks:
            raise ValueError(f"FB '{fb._name}' already exists in resource container.")
        self._blocks[fb._name] = fb

    def get_fb(self, name: str) -> BaseFunctionBlock:
        try:
            return self._blocks[name]
        except KeyError as exc:
            raise ValueError(f"FB '{name}' not found in resource container.") from exc

    @property
    def blocks(self) -> Dict[str, BaseFunctionBlock]:
        return self._blocks

