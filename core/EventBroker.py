from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List

from core.FBContainer import FBContainer


@dataclass
class _QueuedEvent:
    target_fb: str
    event: str
    payload: Dict[str, Any]


class EventBroker:
    def __init__(self, container: FBContainer):
        self._container = container
        self._event_connections: Dict[tuple[str, str], List[tuple[str, str]]] = {}
        self._data_connections: Dict[tuple[str, str], List[tuple[str, str]]] = {}
        self._queue: asyncio.Queue[_QueuedEvent] = asyncio.Queue()

    def add_event_connection(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str) -> None:
        key = (src_fb, src_event)
        self._event_connections.setdefault(key, []).append((dst_fb, dst_event))

    def add_data_connection(self, src_fb: str, src_data: str, dst_fb: str, dst_data: str) -> None:
        key = (src_fb, src_data)
        self._data_connections.setdefault(key, []).append((dst_fb, dst_data))

    async def enqueue(self, target_fb: str, event: str, payload: Dict[str, Any] | None = None) -> None:
        await self._queue.put(_QueuedEvent(target_fb=target_fb, event=event, payload=payload or {}))

    async def process_all(self) -> None:
        while not self._queue.empty():
            queued = await self._queue.get()
            fb = self._container.get_fb(queued.target_fb)

            for key, val in queued.payload.items():
                fb.set_input(key, val)

            outputs = fb.execute()
            self._propagate_data(queued.target_fb, outputs)
            await self._propagate_events(queued.target_fb, fb.getEventOutputs())
            self._queue.task_done()

    def _propagate_data(self, src_fb: str, outputs: Dict[str, Any]) -> None:
        for out_name, out_val in outputs.items():
            targets = self._data_connections.get((src_fb, out_name), [])
            for dst_fb, dst_input in targets:
                target_block = self._container.get_fb(dst_fb)
                target_block.set_input(dst_input, out_val)

    async def _propagate_events(self, src_fb: str, output_events: Iterable[str]) -> None:
        for out_event in output_events:
            targets = self._event_connections.get((src_fb, out_event), [])
            for dst_fb, dst_event in targets:
                await self.enqueue(dst_fb, dst_event)
