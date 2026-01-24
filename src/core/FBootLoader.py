import importlib
from typing import Dict, List, Type

from core.BaseFb import BaseFB


class FBootLoader:
    def __init__(self) -> None:
        pass

    def loadFBList(self, fbArray: List[str]) -> Dict[str, Type[BaseFB]]:
        loaded_blocks: Dict[str, Type[BaseFB]] = {}
        for fb_name in fbArray:
            class_name = fb_name.split(".")[-1]
            try:
                module = importlib.import_module(fb_name)
            except ModuleNotFoundError as exc:
                raise ImportError(
                    f"Function block '{class_name}' not found in module '{fb_name}'."
                ) from exc

            try:
                fb_class = getattr(module, class_name)
            except AttributeError as exc:
                raise ImportError(
                    f"Expected class '{class_name}' inside module '{fb_name}'."
                ) from exc

            loaded_blocks[class_name] = fb_class

        return loaded_blocks