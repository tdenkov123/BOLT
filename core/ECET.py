from __future__ import annotations

import threading
from collections import deque
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.BaseFunctionBlock import BaseFunctionBlock

from core.connections.Connection import ConnectionPoint


class EventChainExecutionThread:
    def __init__(self) -> None:
        self._internal_queue: deque[ConnectionPoint] = deque()
        self._external_queue: deque[ConnectionPoint] = deque()
        self._external_lock = threading.Lock()
        self._wake_event = threading.Event()
        self._alive = False
        self._thread: threading.Thread | None = None
        self._processing_events = False

    def start(self) -> None:
        if self._alive:
            return
        self._alive = True
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="ECET"
        )
        self._thread.start()

    def stop(self) -> None:
        self._alive = False
        self._wake_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._thread = None

    def start_event_chain(self, event_entry: ConnectionPoint) -> None:
        with self._external_lock:
            self._external_queue.append(event_entry)
        self._processing_events = True
        self._wake_event.set()

    def add_event_entry(self, event_entry: ConnectionPoint) -> None:
        self._internal_queue.append(event_entry)

    @property
    def is_processing_events(self) -> bool:
        return self._processing_events

    def _run(self) -> None:
        while self._alive:
            if self._external_event_occurred():
                self._transfer_external_events()

            if self._internal_queue:
                event = self._internal_queue.popleft()
                try:
                    event.fb.receive_input_event(event.port_id, self)
                except Exception:
                    print(f"Exception in FB '{event.fb.instance_name}' (event port {event.port_id})")
            else:
                self._processing_events = False
                self._wake_event.clear()
                if self._external_event_occurred():
                    return
                self._wake_event.wait()
                self._processing_events = True

    def _external_event_occurred(self) -> bool:
        return len(self._external_queue) > 0

    def _transfer_external_events(self) -> None:
        with self._external_lock:
            while self._external_queue:
                self.add_event_entry(self._external_queue.popleft())
