from __future__ import annotations

import collections
from typing import TYPE_CHECKING

import core.MQTTClient as mqtt_manager
from core.BaseFunctionBlock import BaseFunctionBlock, EXTERNAL_EVENT_ID
from core.connections.Connection import ConnectionPoint
from core.datatypes.IEC_INT import IEC_DINT
from core.datatypes.IEC_STRING import IEC_STRING
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class MQTT_SUBSCRIBE(BaseFunctionBlock):

    FBINTERFACE = FBInterface(
        ei_names=("INIT", "TERM"),
        eo_names=("INITO", "IND", "ERROR"),
        di_names=("BROKER_HOST", "BROKER_PORT", "TOPIC"),
        di_types=(IEC_STRING, IEC_DINT, IEC_STRING),
        do_names=("VALUE", "STATUS"),
        do_types=(IEC_STRING, IEC_STRING),
    )

    _EI_INIT = 0
    _EI_TERM = 1
    _EO_INITO = 0
    _EO_IND = 1
    _EO_ERROR = 2
    _DI_BROKER_HOST = 0
    _DI_BROKER_PORT = 1
    _DI_TOPIC = 2
    _DO_VALUE = 0
    _DO_STATUS = 1

    def __init__(self, instance_name: str) -> None:
        self._manager: mqtt_manager.MQTTClientManager | None = None
        self._ecet: EventChainExecutionThread | None = None
        self._pending_messages: collections.deque[str] = collections.deque()
        self._mqtt_callback = self._on_mqtt_message
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if ei_id == self._EI_INIT:
            host = self._di_vars[self._DI_BROKER_HOST].value
            port = int(self._di_vars[self._DI_BROKER_PORT].value)
            topic = self._di_vars[self._DI_TOPIC].value
            try:
                self._ecet = ecet
                self._manager = mqtt_manager.get_client(host, port)
                self._manager.subscribe(topic, self._mqtt_callback)
                self._do_vars[self._DO_STATUS].value = ""
                self.send_output_event(self._EO_INITO, ecet)
            except Exception as exc:
                self._do_vars[self._DO_STATUS].value = str(exc)
                self.send_output_event(self._EO_ERROR, ecet)

        elif ei_id == self._EI_TERM:
            if self._manager is not None:
                topic = self._di_vars[self._DI_TOPIC].value
                self._manager.unsubscribe(topic, self._mqtt_callback)
                self._manager = None
            self._ecet = None

        elif ei_id == EXTERNAL_EVENT_ID:
            if self._pending_messages:
                payload = self._pending_messages.popleft()
                self._do_vars[self._DO_VALUE].value = payload
                self._do_vars[self._DO_STATUS].value = ""
                self.send_output_event(self._EO_IND, ecet)

    def _on_mqtt_message(self, payload: str) -> None:
        self._pending_messages.append(payload)
        if self._ecet is not None:
            self._ecet.start_event_chain(ConnectionPoint(self, EXTERNAL_EVENT_ID))

    def set_initial_values(self) -> None:
        self._di_vars[self._DI_BROKER_HOST].value = "localhost"
        self._di_vars[self._DI_BROKER_PORT].value = 1883
        self._di_vars[self._DI_TOPIC].value = ""
        self._do_vars[self._DO_VALUE].value = ""
        self._do_vars[self._DO_STATUS].value = ""
