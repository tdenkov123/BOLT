from __future__ import annotations

from enum import IntEnum
from typing import Any


class DataTypeIDEnum(IntEnum):
    ANY = 0
    BOOL = 1
    BYTE = 2
    WORD = 3
    DWORD = 4
    LWORD = 5
    SINT = 6
    INT = 7
    DINT = 8
    LINT = 9
    USINT = 10
    UINT = 11
    UDINT = 12
    ULINT = 13
    REAL = 14
    LREAL = 15
    STRING = 16
    WSTRING = 17
    TIME = 18
    DATE = 19


class IEC_ANY:
    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.ANY

    @classmethod
    def type_name(cls) -> str:
        return cls.type_id().name

    def __init__(self, value: Any = None) -> None:
        self._value: Any = self._default() if value is None else self._coerce(value)

    def _default(self) -> Any:
        return None

    def _coerce(self, value: Any) -> Any:
        return value

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        self._value = self._coerce(new_value)

    def set_value(self, other: IEC_ANY) -> None:
        self._value = self._coerce(other._value)

    def clone(self) -> IEC_ANY:
        return self.__class__(self._value)

    def __repr__(self) -> str:
        return f"{self.type_name()}({self._value!r})"


class IEC_ANY_ELEMENTARY(IEC_ANY):
    pass

class IEC_ANY_MAGNITUDE(IEC_ANY_ELEMENTARY):
    pass

class IEC_ANY_NUM(IEC_ANY_MAGNITUDE):
    pass

class IEC_ANY_INT(IEC_ANY_NUM):
    pass

class IEC_ANY_REAL(IEC_ANY_NUM):
    pass

class IEC_ANY_STRING(IEC_ANY_ELEMENTARY):
    pass

class IEC_ANY_BIT(IEC_ANY_ELEMENTARY):
    pass

class IEC_ANY_DATE(IEC_ANY_ELEMENTARY):
    pass
