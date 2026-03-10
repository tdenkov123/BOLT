from __future__ import annotations

from typing import Dict

from core.connections.Connection import ConnectionPoint
from core.connections.DataConnection import DataConnection
from core.ECET import EventChainExecutionThread
from core.FBStates import FBStates, ManagerCommandType
from core.BaseFunctionBlock import BaseFunctionBlock
from core.FBInterface import FBInterface


class BaseResource(BaseFunctionBlock):
    FBINTERFACE = FBInterface()

    def __init__(self, instance_name: str) -> None:
        super().__init__(instance_name)
        self._ecet = EventChainExecutionThread()
        self._fbs: Dict[str, BaseFunctionBlock] = {}

    def create_fb(self, fb: BaseFunctionBlock) -> None:
        if fb.instance_name in self._fbs:
            raise ValueError(
                f"FB '{fb.instance_name}' already exists in "
                f"resource '{self._instance_name}'"
            )
        self._fbs[fb.instance_name] = fb

    def get_fb(self, name: str) -> BaseFunctionBlock:
        try:
            return self._fbs[name]
        except KeyError:
            raise ValueError(
                f"FB '{name}' not found in resource '{self._instance_name}'"
            )

    def connect_event(
        self,
        src_fb_name: str,
        src_eo_name: str,
        dst_fb_name: str,
        dst_ei_name: str,
    ) -> None:
        src_fb = self.get_fb(src_fb_name)
        dst_fb = self.get_fb(dst_fb_name)

        eo_id = src_fb.FBINTERFACE.get_eo_id(src_eo_name)
        ei_id = dst_fb.FBINTERFACE.get_ei_id(dst_ei_name)

        if eo_id is None:
            raise ValueError(
                f"No event output '{src_eo_name}' on FB '{src_fb_name}'"
            )
        if ei_id is None:
            raise ValueError(
                f"No event input '{dst_ei_name}' on FB '{dst_fb_name}'"
            )

        src_fb._eo_connections[eo_id].add_destination(dst_fb, ei_id)

    def connect_data(
        self,
        src_fb_name: str,
        src_do_name: str,
        dst_fb_name: str,
        dst_di_name: str,
    ) -> None:
        src_fb = self.get_fb(src_fb_name)
        dst_fb = self.get_fb(dst_fb_name)

        do_id = src_fb.FBINTERFACE.get_do_id(src_do_name)
        di_id = dst_fb.FBINTERFACE.get_di_id(dst_di_name)

        if do_id is None:
            raise ValueError(
                f"No data output '{src_do_name}' on FB '{src_fb_name}'"
            )
        if di_id is None:
            raise ValueError(
                f"No data input '{dst_di_name}' on FB '{dst_fb_name}'"
            )

        src_type = src_fb.FBINTERFACE.do_types[do_id]
        dst_type = dst_fb.FBINTERFACE.di_types[di_id]
        if not DataConnection.can_be_connected(src_type, dst_type):
            raise TypeError(
                f"Cannot connect {src_type.type_name()} output "
                f"'{src_do_name}' to {dst_type.type_name()} input "
                f"'{dst_di_name}'"
            )

        data_conn = src_fb._do_connections[do_id]
        dst_fb.connect_di(di_id, data_conn)

    def set_data(self, fb_name: str, di_name: str, value) -> None:
        fb = self.get_fb(fb_name)
        di_id = fb.FBINTERFACE.get_di_id(di_name)
        if di_id is None:
            raise ValueError(
                f"No data input '{di_name}' on FB '{fb_name}'"
            )
        fb._di_vars[di_id].value = value

    def start(self) -> None:
        self._ecet.change_execution_state(ManagerCommandType.START)
        for fb in self._fbs.values():
            fb.change_execution_state(ManagerCommandType.START)
        self.change_execution_state(ManagerCommandType.START)

    def stop(self) -> None:
        for fb in self._fbs.values():
            fb.change_execution_state(ManagerCommandType.STOP)
        self.change_execution_state(ManagerCommandType.STOP)
        self._ecet.change_execution_state(ManagerCommandType.STOP)

    def trigger_event(
        self, fb_name: str, event_name: str = "REQ"
    ) -> None:
        fb = self.get_fb(fb_name)
        ei_id = fb.FBINTERFACE.get_ei_id(event_name)
        if ei_id is None:
            from core.BaseFunctionBlock import EXTERNAL_EVENT_ID
            ei_id = EXTERNAL_EVENT_ID
        self._ecet.start_event_chain(ConnectionPoint(fb, ei_id))

    @property
    def ecet(self) -> EventChainExecutionThread:
        return self._ecet

    def execute_event(self, ei_id, ecet):
        pass

    def set_initial_values(self):
        pass
