from __future__ import annotations

from enum import IntEnum
from typing import Any


class DataTypeIDEnum(IntEnum):
    ANY = 0
    BOOL = 1
    SINT = 2
    INT = 3
    DINT = 4
    LINT = 5
    USINT = 6
    UINT = 7
    UDINT = 8
    ULINT = 9
    REAL = 10
    LREAL = 11
    STRING = 12
    WSTRING = 13
    TIME = 14
    DATE = 15


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
