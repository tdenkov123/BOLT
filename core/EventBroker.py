from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Tuple

from core.FBContainer import FBContainer


@dataclass
class _QueuedEvent:
	target_fb: str
	event: str
	payload: Tuple


class EventBroker:
	def __init__(self, container: FBContainer):
		self._container = container
		self._connections: Dict[tuple[str, str], List[tuple[str, str]]] = {}
		self._queue: Deque[_QueuedEvent] = deque()

	def add_connection(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str) -> None:
		key = (src_fb, src_event)
		self._connections.setdefault(key, []).append((dst_fb, dst_event))

	def enqueue(self, target_fb: str, event: str, payload: Iterable) -> None:
		self._queue.append(_QueuedEvent(target_fb=target_fb, event=event, payload=tuple(payload)))

	def process_all(self) -> None:
		while self._queue:
			queued = self._queue.popleft()
			fb = self._container.get_fb(queued.target_fb)
			result = fb.execute(*queued.payload)
			self._propagate(queued.target_fb, fb.getEventOutputs(), result)

	def _propagate(self, src_fb: str, output_events: Iterable[str], result) -> None:
		for out_event in output_events:
			targets = self._connections.get((src_fb, out_event), [])
			for dst_fb, dst_event in targets:
				self.enqueue(dst_fb, dst_event, [result])
