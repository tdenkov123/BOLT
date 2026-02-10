from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Optional

from core.connections.Connection import ConnectionPoint
from core.datatypes.IEC_TIME import IEC_TIME
from core.BaseFunctionBlock import BaseFunctionBlock, EXTERNAL_EVENT_ID
from core.interface_spec import SFBInterfaceSpec

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class E_CYCLE(BaseFunctionBlock):

    FBINTERFACE = SFBInterfaceSpec(
        ei_names=("START", "STOP"),
        eo_names=("EO",),
        di_names=("DT",),
        di_types=(IEC_TIME,),
    )

    _EI_START = 0
    _EI_STOP = 1
    _EO_EO = 0
    _DI_DT = 0

    def __init__(self, instance_name: str) -> None:
        self._timer: Optional[threading.Timer] = None
        self._active = False
        self._ecet: Optional[EventChainExecutionThread] = None
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_START:
            self._stop_timer()
            self._ecet = ecet
            self._active = True
            self._schedule_next()
        elif ei_id == self._EI_STOP:
            self._stop_timer()
        elif ei_id == EXTERNAL_EVENT_ID:
            self.send_output_event(self._EO_EO, ecet)

    def _schedule_next(self) -> None:
        dt_ms = self._di_vars[self._DI_DT].value
        dt_seconds = max(dt_ms / 1000.0, 0.001)
        self._timer = threading.Timer(dt_seconds, self._on_timer)
        self._timer.daemon = True
        self._timer.start()

    def _on_timer(self) -> None:
        if self._active and self._ecet is not None:
            self._ecet.start_event_chain(
                ConnectionPoint(self, EXTERNAL_EVENT_ID)
            )
        if self._active:
            self._schedule_next()

    def _stop_timer(self) -> None:
        self._active = False
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def set_initial_values(self) -> None:
        self._di_vars[self._DI_DT].value = 1000
