from __future__ import annotations

from typing import Dict

from core.BaseResource import BaseResource


class BaseDevice:
    def __init__(self, device_name: str):
        self.device_name = device_name
        self._resources: Dict[str, BaseResource] = {}

    def add_resource(self, resource: BaseResource) -> None:
        if resource.name in self._resources:
            raise ValueError(f"Resource '{resource.name}' already exists on device '{self.device_name}'.")
        self._resources[resource.name] = resource

    @property
    def resources(self) -> Dict[str, BaseResource]:
        return self._resources

    async def start(self) -> None:
        for resource in self._resources.values():
            await resource.start()

    async def stop(self) -> None:
        for resource in self._resources.values():
            await resource.stop()

    async def trigger_event(self, resource_name: str, fb_name: str, payload=None, event: str = "REQ") -> None:
        resource = self._get_resource(resource_name)
        await resource.enqueue_event(fb_name, payload, event)

    def _get_resource(self, resource_name: str) -> BaseResource:
        try:
            return self._resources[resource_name]
        except KeyError as exc:
            raise ValueError(f"Resource '{resource_name}' not found on device '{self.device_name}'.") from exc
