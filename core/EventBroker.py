from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

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
        self._data_pulls: Dict[tuple[str, str], List[Tuple[str, str, str]]] = {}
        self._data_pushes: Dict[tuple[str, str], List[Tuple[str, str, str]]] = {}
        self._queue: asyncio.Queue[_QueuedEvent] = asyncio.Queue()
        self._tasks: set[asyncio.Task] = set()

    def add_event_connection(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str) -> None:
        key = (src_fb, src_event)
        self._event_connections.setdefault(key, []).append((dst_fb, dst_event))

    def add_data_pull(self, dst_fb: str, dst_event: str, src_fb: str, src_output: str, dst_input: str) -> None:
        key = (dst_fb, dst_event)
        self._data_pulls.setdefault(key, []).append((src_fb, src_output, dst_input))

    def add_data_push(self, src_fb: str, src_event: str, src_output: str, dst_fb: str, dst_input: str) -> None:
        key = (src_fb, src_event)
        self._data_pushes.setdefault(key, []).append((src_output, dst_fb, dst_input))

    async def enqueue(self, target_fb: str, event: str, payload: Dict[str, Any] | None = None) -> None:
        await self._queue.put(_QueuedEvent(target_fb=target_fb, event=event, payload=payload or {}))

    async def process_all(self) -> None:
        while True:
            while not self._queue.empty():
                queued = await self._queue.get()
                task = asyncio.create_task(self._handle_event(queued))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)

            if not self._tasks:
                break

            done, _ = await asyncio.wait(self._tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                self._tasks.discard(t)
                exc = t.exception()
                if exc:
                    raise exc

    async def _handle_event(self, queued: _QueuedEvent) -> None:
        fb = self._container.get_fb(queued.target_fb)

        for src_fb, src_out, dst_input in self._data_pulls.get((queued.target_fb, queued.event), []):
            src_block = self._container.get_fb(src_fb)
            fb.set_input(dst_input, src_block.get_output(src_out))

        for key, val in queued.payload.items():
            fb.set_input(key, val)

        outputs, out_events = await fb.execute(queued.event)
        await self._propagate(outputs, queued.target_fb, out_events)

    async def _propagate(self, outputs: Dict[str, Any], src_fb: str, output_events: Iterable[str]) -> None:
        for out_event in output_events:
            for src_out, dst_fb, dst_input in self._data_pushes.get((src_fb, out_event), []):
                target_block = self._container.get_fb(dst_fb)
                target_block.set_input(dst_input, outputs.get(src_out))

            for dst_fb, dst_event in self._event_connections.get((src_fb, out_event), []):
                await self.enqueue(dst_fb, dst_event)
