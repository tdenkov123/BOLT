from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_MAGNITUDE
from core.datatypes.IEC_Literals import parse_iec_time_literal


class IEC_TIME(IEC_ANY_MAGNITUDE):
    """Time duration in milliseconds"""
    
    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.TIME

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            return parse_iec_time_literal(value)
        return int(value)
