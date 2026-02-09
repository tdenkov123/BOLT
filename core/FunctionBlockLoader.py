import importlib
from typing import Dict, Iterable, List, Type

from core.BaseFunctionBlock import BaseFunctionBlock


class FunctionBlockLoader:
    def __init__(self) -> None:
        pass

    def loadFBList(self, fbArray: List[str]) -> Dict[str, Type[BaseFunctionBlock]]:
        loaded_blocks: Dict[str, Type[BaseFunctionBlock]] = {}
        for fb_ref in fbArray:
            module_path, explicit_class = self._split_ref(fb_ref)
            try:
                module = importlib.import_module(module_path)
            except ModuleNotFoundError as exc:
                raise ImportError(
                    f"Module '{module_path}' could not be imported for '{fb_ref}'."
                ) from exc

            fb_classes = self._collect_classes(module, explicit_class)
            if not fb_classes:
                target = explicit_class or "BaseFunctionBlock subclass"
                raise ImportError(
                    f"No {target} found in module '{module_path}'."
                )

            for name, cls in fb_classes.items():
                loaded_blocks[name] = cls

        return loaded_blocks

    def _split_ref(self, fb_ref: str) -> tuple[str, str | None]:
        if ":" in fb_ref:
            module_path, class_name = fb_ref.rsplit(":", 1)
            return module_path, class_name
        return fb_ref, None

    def _collect_classes(self, module, explicit_class: str | None) -> Dict[str, Type[BaseFunctionBlock]]:
        def is_fb(candidate: object) -> bool:
            return isinstance(candidate, type) and issubclass(candidate, BaseFunctionBlock) and candidate is not BaseFunctionBlock

        if explicit_class:
            try:
                fb_class = getattr(module, explicit_class)
            except AttributeError as exc:
                raise ImportError(
                    f"Expected class '{explicit_class}' inside module '{module.__name__}'."
                ) from exc
            if not is_fb(fb_class):
                raise ImportError(
                    f"'{explicit_class}' in module '{module.__name__}' is not a BaseFunctionBlock subclass."
                )
            return {explicit_class: fb_class}

        discovered: Dict[str, Type[BaseFunctionBlock]] = {}
        for attr_name in dir(module):
            attr_val = getattr(module, attr_name)
            if is_fb(attr_val):
                discovered[attr_name] = attr_val
        return discovered
