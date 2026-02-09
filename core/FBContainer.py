from __future__ import annotations

from typing import Dict

from core.BaseFb import BaseFB


class FBContainer:
    def __init__(self):
        self._blocks: Dict[str, BaseFB] = {}

    def add_fb(self, fb: BaseFB) -> None:
        if fb.name in self._blocks:
            raise ValueError(f"FB '{fb.name}' already exists in resource container.")
        self._blocks[fb.name] = fb

    def get_fb(self, name: str) -> BaseFB:
        try:
            return self._blocks[name]
        except KeyError as exc:
            raise ValueError(f"FB '{name}' not found in resource container.") from exc

    @property
    def blocks(self) -> Dict[str, BaseFB]:
        return self._blocks

