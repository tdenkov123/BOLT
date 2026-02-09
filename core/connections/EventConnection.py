from __future__ import annotations
from typing import TYPE_CHECKING, List
from core.connections.Connection import ConnectionPoint

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread
    from core.BaseFunctionBlock import BaseFunctionBlock


class EventConnection:
    def __init__(self, src_fb: BaseFunctionBlock, src_port_id: int) -> None:
        self._source = ConnectionPoint(src_fb, src_port_id)
        self._destinations: List[ConnectionPoint] = []

    def add_destination(self, dst_fb: BaseFunctionBlock, dst_ei_id: int) -> None:
        dest = ConnectionPoint(dst_fb, dst_ei_id)
        if dest in self._destinations:
            raise ValueError(
                f"Destination already connected: {dst_fb.instance_name}:{dst_ei_id}"
            )
        self._destinations.append(dest)

    def remove_destination(self, dst_fb: BaseFunctionBlock, dst_ei_id: int) -> None:
        dest = ConnectionPoint(dst_fb, dst_ei_id)
        self._destinations.remove(dest)

    def trigger_event(self, ecet: EventChainExecutionThread) -> None:
        for dest in self._destinations:
            ecet.add_event_entry(dest)

    @property
    def is_connected(self) -> bool:
        return len(self._destinations) > 0

    @property
    def destinations(self) -> List[ConnectionPoint]:
        return self._destinations
