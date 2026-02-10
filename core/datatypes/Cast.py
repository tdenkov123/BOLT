from __future__ import annotations

from core.datatypes.IEC_ANY import DataTypeIDEnum

_IMPLICIT_WIDENING: dict[DataTypeIDEnum, set[DataTypeIDEnum]] = {
    DataTypeIDEnum.SINT: {DataTypeIDEnum.INT, DataTypeIDEnum.DINT, DataTypeIDEnum.LINT,
                       DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.INT:  {DataTypeIDEnum.DINT, DataTypeIDEnum.LINT,
                       DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.DINT: {DataTypeIDEnum.LINT, DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.LINT: {DataTypeIDEnum.LREAL},

    DataTypeIDEnum.USINT: {DataTypeIDEnum.UINT, DataTypeIDEnum.UDINT, DataTypeIDEnum.ULINT,
                        DataTypeIDEnum.INT, DataTypeIDEnum.DINT, DataTypeIDEnum.LINT,
                        DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.UINT:  {DataTypeIDEnum.UDINT, DataTypeIDEnum.ULINT,
                        DataTypeIDEnum.DINT, DataTypeIDEnum.LINT,
                        DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.UDINT: {DataTypeIDEnum.ULINT, DataTypeIDEnum.LINT,
                        DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
    DataTypeIDEnum.ULINT: {DataTypeIDEnum.LREAL},

    DataTypeIDEnum.REAL: {DataTypeIDEnum.LREAL},

    DataTypeIDEnum.BOOL: {DataTypeIDEnum.SINT, DataTypeIDEnum.INT, DataTypeIDEnum.DINT,
                       DataTypeIDEnum.LINT, DataTypeIDEnum.USINT, DataTypeIDEnum.UINT,
                       DataTypeIDEnum.UDINT, DataTypeIDEnum.ULINT,
                       DataTypeIDEnum.REAL, DataTypeIDEnum.LREAL},
}


def can_connect(src_id: DataTypeIDEnum, dst_id: DataTypeIDEnum) -> bool:
    if src_id == dst_id:
        return True
    if src_id == DataTypeIDEnum.ANY or dst_id == DataTypeIDEnum.ANY:
        return True
    return dst_id in _IMPLICIT_WIDENING.get(src_id, set())
