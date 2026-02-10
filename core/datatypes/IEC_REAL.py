from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum, IEC_ANY_REAL
from core.datatypes.IEC_Literals import parse_iec_real_literal

import struct


class IEC_REAL(IEC_ANY_REAL):
    """"Float 32bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.REAL

    def _default(self) -> float:
        return 0.0

    def _coerce(self, value) -> float:
        if isinstance(value, str):
            f = parse_iec_real_literal(value)
        else:
            f = float(value)
        return struct.unpack('f', struct.pack('f', f))[0]


class IEC_LREAL(IEC_ANY_REAL):
    """"Float 64bit"""

    @classmethod
    def type_id(cls) -> DataTypeIDEnum:
        return DataTypeIDEnum.LREAL

    def _default(self) -> float:
        return 0.0

    def _coerce(self, value) -> float:
        if isinstance(value, str):
            return parse_iec_real_literal(value)
        return float(value)
