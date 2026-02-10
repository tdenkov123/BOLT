from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_STRING
from core.datatypes.IEC_Literals import parse_iec_string_literal


class IEC_STRING(IEC_ANY_STRING):
    """Single-byte string"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.STRING

    def _default(self) -> str:
        return ""

    def _coerce(self, value) -> str:
        if isinstance(value, str):
            return parse_iec_string_literal(value)
        return str(value)


class IEC_WSTRING(IEC_ANY_STRING):
    """Wide string"""
    
    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.WSTRING

    def _default(self) -> str:
        return ""

    def _coerce(self, value) -> str:
        if isinstance(value, str):
            return parse_iec_string_literal(value)
        return str(value)
