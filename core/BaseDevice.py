from __future__ import annotations

from typing import Dict

from core.BaseResource import BaseResource


class BaseDevice:
    def __init__(self, device_name: str) -> None:
        self._device_name = device_name
        self._resources: Dict[str, BaseResource] = {}

    def get_resource(self, name: str) -> BaseResource:
        try:
            return self._resources[name]
        except KeyError:
            raise ValueError(f"Resource '{name}' not found on device '{self._device_name}'")
    
    @property
    def device_name(self) -> str:
        return self._device_name

    def add_resource(self, resource: BaseResource) -> None:
        if resource.instance_name in self._resources:
            raise ValueError(
                f"Resource '{resource.instance_name}' already exists "
                f"on device '{self._device_name}'"
            )
        self._resources[resource.instance_name] = resource

    @property
    def resources(self) -> Dict[str, BaseResource]:
        return self._resources

    def start(self) -> None:
        for resource in self._resources.values():
            resource.start()

    def stop(self) -> None:
        for resource in self._resources.values():
            resource.stop()

    def trigger_event(
        self,
        resource_name: str,
        fb_name: str,
        event: str = "REQ",
    ) -> None:
        resource = self.get_resource(resource_name)
        resource.trigger_event(fb_name, event)
