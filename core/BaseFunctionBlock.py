from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from core.connections.DataConnection import DataConnection
from core.connections.EventConnection import EventConnection
from core.datatypes.IEC_ANY import IEC_ANY
from core.FBStates import FBStates, ManagerCommandType
from core.FBInterface import FBInterface

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread

class BaseFunctionBlock(ABC):
    FBINTERFACE: FBInterface

    def __init__(self, instance_name: str) -> None:
        self._instance_name = instance_name
        self._state = FBStates.IDLE
        spec = self.FBINTERFACE

        self._di_vars: List[IEC_ANY] = [
            di_type() for di_type in spec.di_types
        ]

        self._do_vars: List[IEC_ANY] = [
            do_type() for do_type in spec.do_types
        ]

        self._eo_connections: List[EventConnection] = [
            EventConnection(self, eo_id) for eo_id in range(spec.num_eos)
        ]

        self._do_connections: List[DataConnection] = [
            DataConnection(self, do_id, self._do_vars[do_id])
            for do_id in range(spec.num_dos)
        ]

        self._di_connections: List[Optional[DataConnection]] = [
            None for _ in range(spec.num_dis)
        ]

        self.set_initial_values()

    @property
    def instance_name(self) -> str:
        return self._instance_name

    @property
    def state(self) -> FBStates:
        return self._state


    def receive_input_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        if self._state != FBStates.RUNNING:
            return
        if ei_id < self.FBINTERFACE.num_eis:
            self.read_input_data(ei_id)
        self.execute_event(ei_id, ecet)

    def send_output_event(self, eo_id: int, ecet: EventChainExecutionThread) -> None:
        if eo_id < self.FBINTERFACE.num_eos:
            self.write_output_data(eo_id)
            self._eo_connections[eo_id].trigger_event(ecet)


    @abstractmethod
    def execute_event(self, ei_id: int, ecet: EventChainExecutionThread) -> None:
        ...

    @abstractmethod
    def set_initial_values(self) -> None:
        ...

    def read_input_data(self, ei_id: int) -> None:
        for di_id in range(self.FBINTERFACE.num_dis):
            self._read_data(di_id)

    def write_output_data(self, eo_id: int) -> None:
        for do_id in range(self.FBINTERFACE.num_dos):
            self._write_data(do_id)

    def _read_data(self, di_id: int) -> None:
        conn = self._di_connections[di_id]
        if conn is not None:
            conn.read_data(self._di_vars[di_id])

    def _write_data(self, do_id: int) -> None:
        self._do_connections[do_id].write_data(self._do_vars[do_id])

    def get_eo_connection(self, eo_name: str) -> EventConnection:
        eo_id = self.FBINTERFACE.get_eo_id(eo_name)
        if eo_id is None:
            raise ValueError(
                f"No event output '{eo_name}' on FB '{self._instance_name}'"
            )
        return self._eo_connections[eo_id]

    def get_do_connection(self, do_name: str) -> DataConnection:
        do_id = self.FBINTERFACE.get_do_id(do_name)
        if do_id is None:
            raise ValueError(
                f"No data output '{do_name}' on FB '{self._instance_name}'"
            )
        return self._do_connections[do_id]

    def connect_di(self, di_id: int, data_conn: Optional[DataConnection]) -> bool:
        if di_id >= self.FBINTERFACE.num_dis:
            return False
        self._di_connections[di_id] = data_conn
        return True

    def change_execution_state(self, command: ManagerCommandType) -> None:
        if command == ManagerCommandType.START:
            if self._state in (FBStates.IDLE, FBStates.STOPPED):
                self._state = FBStates.RUNNING
        elif command == ManagerCommandType.STOP:
            if self._state == FBStates.RUNNING:
                self._state = FBStates.STOPPED
        elif command == ManagerCommandType.KILL:
            self._state = FBStates.KILLED
        elif command == ManagerCommandType.RESET:
            if self._state == FBStates.STOPPED:
                self.set_initial_values()
                self._state = FBStates.IDLE
