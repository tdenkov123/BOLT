from __future__ import annotations

from typing import Iterable

from core.FBContainer import FBContainer
from core.EventBroker import EventBroker


class BaseResource:
    def __init__(self, name: str) -> None:
        self._name = name
        self._container = FBContainer()
        self._broker = EventBroker(self._container)

    @property
    def name(self) -> str:
        return self._name

    @property
    def container(self) -> FBContainer:
        return self._container

    def add_fb(self, fb_instance) -> None:
        self._container.add_fb(fb_instance)

    def connect(self, src_fb: str, src_event: str, dst_fb: str, dst_event: str = "REQ") -> None:
        self._broker.add_connection(src_fb, src_event, dst_fb, dst_event)

    def enqueue_event(self, fb_name: str, payload: Iterable | None = None, event: str = "REQ") -> None:
        self._broker.enqueue(fb_name, event, payload or [])

    def drain_events(self) -> None:
        self._broker.process_all()

