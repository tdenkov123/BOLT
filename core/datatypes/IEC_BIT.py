from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_BIT
from core.datatypes.IEC_Literals import parse_iec_bool_literal, parse_iec_int_literal


def _coerce_any_bit(value, byte_len: int, type_name: str) -> bytes:
    if isinstance(value, IEC_ANY_BIT):
        value = value.value

    if isinstance(value, (bytes, bytearray)):
        b = bytes(value)
        if len(b) != byte_len:
            raise OverflowError(f"Value length {len(b)} invalid for {type_name}")
        return b

    if isinstance(value, str):
        try:
            value = parse_iec_int_literal(value)
        except ValueError as exc:
            raise ValueError(f"Invalid integer literal for {type_name}") from exc

    if isinstance(value, int):
        max_value = (1 << (byte_len * 8)) - 1
        if not (0 <= value <= max_value):
            raise OverflowError(f"Value {value} out of range for {type_name}")
        return value.to_bytes(byte_len, "little", signed=False)

    raise TypeError(f"Unsupported value type for {type_name}")


class IEC_BOOL(IEC_ANY_BIT):
    """Boolean value"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.BOOL

    def _default(self) -> bool:
        return False

    def _coerce(self, value) -> bool:
        if isinstance(value, str):
            return parse_iec_bool_literal(value)
        return bool(value)


class IEC_BYTE(IEC_ANY_BIT):
    """Bit string of length 8bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.BYTE

    def _default(self) -> bytes:
        return b"\x00"

    def _coerce(self, value) -> bytes:
        return _coerce_any_bit(value, 1, self.type_name())


class IEC_WORD(IEC_ANY_BIT):
    """Bit string of length 16bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.WORD

    def _default(self) -> bytes:
        return b"\x00\x00"

    def _coerce(self, value) -> bytes:
        return _coerce_any_bit(value, 2, self.type_name())


class IEC_DWORD(IEC_ANY_BIT):
    """Bit string of length 32bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.DWORD

    def _default(self) -> bytes:
        return b"\x00\x00\x00\x00"

    def _coerce(self, value) -> bytes:
        return _coerce_any_bit(value, 4, self.type_name())


class IEC_LWORD(IEC_ANY_BIT):
    """Bit string of length 64bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.LWORD

    def _default(self) -> bytes:
        return b"\x00\x00\x00\x00\x00\x00\x00\x00"

    def _coerce(self, value) -> bytes:
        return _coerce_any_bit(value, 8, self.type_name())
