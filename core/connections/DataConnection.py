from __future__ import annotations
from typing import TYPE_CHECKING, Type, Any

if TYPE_CHECKING:
    from core.BaseFunctionBlock import BaseFunctionBlock


class DataConnection:
    def __init__(self, src_fb: BaseFunctionBlock, src_port_id: int, value: Any) -> None:
        self._src_fb = src_fb
        self._src_port_id = src_port_id
        self._value: Any = value.clone()

    def write_data(self, value: Any) -> None:
        self._value.set_value(value)

    def read_data(self, target: Any) -> None:
        target.set_value(self._value)

    @property
    def value(self) -> Any:
        return self._value

