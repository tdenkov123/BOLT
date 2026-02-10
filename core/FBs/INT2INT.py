from __future__ import annotations

from typing import TYPE_CHECKING

from core.datatypes.IEC_ANY import IEC_ANY
from core.datatypes.IEC_INT import IEC_INT
from core.BaseFunctionBlock import BaseFunctionBlock
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class INT2INT(BaseFunctionBlock):

    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        di_names=("IN",),
        di_types=(IEC_ANY,),
        do_names=("OUT",),
        do_types=(IEC_INT,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DI_IN = 0
    _DO_OUT = 0

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_REQ:
            val = self._di_vars[self._DI_IN].value
            try:
                self._do_vars[self._DO_OUT].value = int(val) if val is not None else 0
            except (ValueError, TypeError, OverflowError):
                self._do_vars[self._DO_OUT].value = 0
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        self._do_vars[self._DO_OUT].value = 0
