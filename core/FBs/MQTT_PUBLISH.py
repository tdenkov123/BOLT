from __future__ import annotations

from typing import TYPE_CHECKING

import core.MQTTClient as mqtt_manager
from core.BaseFunctionBlock import BaseFunctionBlock
from core.datatypes.IEC_INT import IEC_DINT
from core.datatypes.IEC_STRING import IEC_STRING
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class MQTT_PUBLISH(BaseFunctionBlock):

    FBINTERFACE = FBInterface(
        ei_names=("INIT", "SEND", "TERM"),
        eo_names=("INITO", "CNF", "ERROR"),
        di_names=("BROKER_HOST", "BROKER_PORT", "TOPIC", "VALUE"),
        di_types=(IEC_STRING, IEC_DINT, IEC_STRING, IEC_STRING),
        do_names=("STATUS",),
        do_types=(IEC_STRING,),
    )

    _EI_INIT = 0
    _EI_SEND = 1
    _EI_TERM = 2
    _EO_INITO = 0
    _EO_CNF = 1
    _EO_ERROR = 2
    _DI_BROKER_HOST = 0
    _DI_BROKER_PORT = 1
    _DI_TOPIC = 2
    _DI_VALUE = 3
    _DO_STATUS = 0

    def __init__(self, instance_name: str) -> None:
        self._manager: mqtt_manager.MQTTClientManager | None = None
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_INIT:
            host = self._di_vars[self._DI_BROKER_HOST].value
            port = int(self._di_vars[self._DI_BROKER_PORT].value)
            try:
                self._manager = mqtt_manager.get_client(host, port)
                self._do_vars[self._DO_STATUS].value = ""
                self.send_output_event(self._EO_INITO, ecet)
            except Exception as exc:
                self._do_vars[self._DO_STATUS].value = str(exc)
                self.send_output_event(self._EO_ERROR, ecet)

        elif ei_id == self._EI_SEND:
            if self._manager is None:
                self._do_vars[self._DO_STATUS].value = ("Not connected — trigger INIT first")
                self.send_output_event(self._EO_ERROR, ecet)
                return
            topic = self._di_vars[self._DI_TOPIC].value
            value = self._di_vars[self._DI_VALUE].value
            try:
                self._manager.publish(topic, value)
                self._do_vars[self._DO_STATUS].value = ""
                self.send_output_event(self._EO_CNF, ecet)
            except Exception as exc:
                self._do_vars[self._DO_STATUS].value = str(exc)
                self.send_output_event(self._EO_ERROR, ecet)

        elif ei_id == self._EI_TERM:
            self._manager = None

    def set_initial_values(self) -> None:
        self._di_vars[self._DI_BROKER_HOST].value = "localhost"
        self._di_vars[self._DI_BROKER_PORT].value = 1883
        self._di_vars[self._DI_TOPIC].value = ""
        self._di_vars[self._DI_VALUE].value = ""
        self._do_vars[self._DO_STATUS].value = ""
