from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from core.BaseFunctionBlock import BaseFunctionBlock



@dataclass
class ConnectionPoint:
    fb: BaseFunctionBlock
    port_id: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConnectionPoint):
            return NotImplemented
        return self.fb is other.fb and self.port_id == other.port_id

    def __hash__(self) -> int:
        return hash((id(self.fb), self.port_id))
