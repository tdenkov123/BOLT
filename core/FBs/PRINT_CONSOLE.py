from __future__ import annotations
from typing import TYPE_CHECKING

from core.datatypes.IEC_ANY import IEC_ANY
from core.BaseFunctionBlock import BaseFunctionBlock
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class PRINT_CONSOLE(BaseFunctionBlock):

    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        di_names=("IN",),
        di_types=(IEC_ANY,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DI_IN = 0

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_REQ:
            print(self._di_vars[self._DI_IN].value)
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        pass
