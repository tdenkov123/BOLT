from __future__ import annotations

from typing import TYPE_CHECKING

from core.datatypes.IEC_INT import IEC_LINT
from core.datatypes.IEC_REAL import IEC_LREAL
from core.datatypes.IEC_ANY import IEC_ANY_NUM
from core.BaseFunctionBlock import BaseFunctionBlock
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class ADD_2(BaseFunctionBlock):
    
    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        di_names=("IN1", "IN2"),
        di_types=(IEC_ANY_NUM, IEC_ANY_NUM),
        do_names=("OUT",),
        do_types=(IEC_LREAL,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DI_IN1 = 0
    _DI_IN2 = 1
    _DO_OUT = 0

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_REQ:
            in1 = self._di_vars[self._DI_IN1].value
            in2 = self._di_vars[self._DI_IN2].value
            self._do_vars[self._DO_OUT].value = in1 + in2
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        self._di_vars[self._DI_IN1].value = 0
        self._di_vars[self._DI_IN2].value = 0
        self._do_vars[self._DO_OUT].value = 0
