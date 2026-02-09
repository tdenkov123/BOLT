from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_STRING


class IEC_STRING(IEC_ANY_STRING):
    """Single-byte string"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.STRING

    def _default(self) -> str:
        return ""

    def _coerce(self, value) -> str:
        return str(value)


class IEC_WSTRING(IEC_ANY_STRING):
    """Wide string"""
    
    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.WSTRING

    def _default(self) -> str:
        return ""

    def _coerce(self, value) -> str:
        return str(value)
