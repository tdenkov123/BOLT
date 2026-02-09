from typing import Callable, Awaitable, Dict, Any

from abc import ABC, abstractmethod

class BaseFunctionBlock(ABC):
    def __init__(self, name: str):
        self.name = name
        self._inputs = {}
        self._outputs = {}
        self._emit_callback: Callable[[str, str, Dict[str, Any] | None], Awaitable[None]] | None = None

    def set_input(self, name: str, value):
        self._inputs[name] = value

    def get_output(self, name: str):
        return self._outputs.get(name)

    def set_emit_callback(self, callback: Callable[[str, str, Dict[str, Any] | None], Awaitable[None]]) -> None:
        self._emit_callback = callback

    async def _emit_event(self, event: str, payload: Dict[str, Any] | None = None) -> None:
        if self._emit_callback:
            await self._emit_callback(self.name, event, payload)

    async def execute(self, event: str):
        raise NotImplementedError("Subclasses should implement this method.")