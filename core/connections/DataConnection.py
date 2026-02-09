from __future__ import annotations
from typing import TYPE_CHECKING
from core.datatypes.iec_any import IEC_ANY

if TYPE_CHECKING:
    from core.BaseFunctionBlock import BaseFunctionBlock


class DataConnection:
    def __init__(self, src_fb: BaseFunctionBlock, src_port_id: int, value: IEC_ANY) -> None:
        self._src_fb = src_fb
        self._src_port_id = src_port_id
        self._value: IEC_ANY = value.clone()

    def write_data(self, value: IEC_ANY) -> None:
        self._value.set_value(value)

    def read_data(self, target: IEC_ANY) -> None:
        target.set_value(self._value)

    @property
    def value(self) -> IEC_ANY:
        return self._value

