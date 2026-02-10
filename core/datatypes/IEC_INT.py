from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_INT
from core.datatypes.IEC_Literals import parse_iec_int_literal


class IEC_SINT(IEC_ANY_INT):
    """Signed 8bit int"""
    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.SINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (-128 <= v <= 127):
            raise OverflowError(f"Value {v} out of range for IEC_SINT")
        return v


class IEC_INT(IEC_ANY_INT):
    """Signed 16bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.INT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (-32768 <= v <= 32767):
            raise OverflowError(f"Value {v} out of range for IEC_INT")
        return v


class IEC_DINT(IEC_ANY_INT):
    """Signed 32bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.DINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (-2147483648 <= v <= 2147483647):
            raise OverflowError(f"Value {v} out of range for IEC_DINT")
        return v


class IEC_LINT(IEC_ANY_INT):
    """Signed 64bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.LINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (-9223372036854775808 <= v <= 9223372036854775807):
            raise OverflowError(f"Value {v} out of range for IEC_LINT")
        return v


class IEC_USINT(IEC_ANY_INT):
    """Unsigned 8bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.USINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (0 <= v <= 255):
            raise OverflowError(f"Value {v} out of range for IEC_USINT")
        return v


class IEC_UINT(IEC_ANY_INT):
    """Unsigned 16bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.UINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (0 <= v <= 65535):
            raise OverflowError(f"Value {v} out of range for IEC_UINT")
        return v


class IEC_UDINT(IEC_ANY_INT):
    """Unsigned 32bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.UDINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (0 <= v <= 4294967295):
            raise OverflowError(f"Value {v} out of range for IEC_UDINT")
        return v


class IEC_ULINT(IEC_ANY_INT):
    """Unsigned 64bit int"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.ULINT

    def _default(self) -> int:
        return 0

    def _coerce(self, value) -> int:
        if isinstance(value, str):
            v = parse_iec_int_literal(value)
        else:
            v = int(value)
        if not (0 <= v <= 18446744073709551615):
            raise OverflowError(f"Value {v} out of range for IEC_ULINT")
        return v
