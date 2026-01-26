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
        self._runner: asyncio.Task | None = None

    def add_event_connection(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str) -> None:
        key = (src_fb, src_event)
        self._event_connections.setdefault(key, []).append((dst_fb, dst_event))

    def add_data_connection(self, src_fb: str, src_output: str, dst_fb: str, dst_input: str) -> None:
        key = (src_fb, src_output)
        self._data_connections.setdefault(key, []).append((dst_fb, dst_input))

    async def enqueue(self, target_fb: str, event: str, payload: Dict[str, Any] | None = None) -> None:
        await self._queue.put(_QueuedEvent(target_fb=target_fb, event=event, payload=payload or {}))

    async def start(self) -> None:
        if self._runner is None or self._runner.done():
            self._runner = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._runner and not self._runner.done():
            self._runner.cancel()
            try:
                await self._runner
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        while True:
            queued = await self._queue.get()
            await self._handle_event(queued)

    async def _handle_event(self, queued: _QueuedEvent) -> None:
        fb = self._container.get_fb(queued.target_fb)

        for key, val in queued.payload.items():
            fb.set_input(key, val)

        outputs, out_events = await fb.execute(queued.event)
        await self._propagate(outputs, queued.target_fb, out_events)

    async def _propagate(self, outputs: Dict[str, Any], src_fb: str, output_events: Iterable[str]) -> None:
        for out_name, out_val in outputs.items():
            for dst_fb, dst_input in self._data_connections.get((src_fb, out_name), []):
                target_block = self._container.get_fb(dst_fb)
                target_block.set_input(dst_input, out_val)

        for out_event in output_events:
            for dst_fb, dst_event in self._event_connections.get((src_fb, out_event), []):
                await self.enqueue(dst_fb, dst_event)
