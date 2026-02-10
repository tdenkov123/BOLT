from __future__ import annotations

from typing import TYPE_CHECKING

from core.BaseFunctionBlock import BaseFunctionBlock, EXTERNAL_EVENT_ID
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class START(BaseFunctionBlock):

    FBINTERFACE = FBInterface(
        eo_names=("START",),
    )

    _EO_START = 0

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == EXTERNAL_EVENT_ID:
            self.send_output_event(self._EO_START, ecet)

    def set_initial_values(self) -> None:
        pass
