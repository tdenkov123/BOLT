import importlib
from typing import Dict, List, Type

from core.BaseFb import BaseFB


class FBootLoader:
    def __init__(self, fb_package: str = "core.FBs") -> None:
        self._fbArray: List[str] = []
        self._fb_package = fb_package

    def getFBList(self, fbArray: List[str]) -> None:
        self._fbArray = fbArray

    def loadFBList(self) -> Dict[str, Type[BaseFB]]:
        loaded_blocks: Dict[str, Type[BaseFB]] = {}
        for fb_name in self._fbArray:
            module_name = fb_name.split(".")[0]
            try:
                module = importlib.import_module(f"{self._fb_package}.{module_name}")
            except ModuleNotFoundError as exc:
                raise ImportError(
                    f"Function block '{module_name}' not found in package '{self._fb_package}'."
                ) from exc

            try:
                fb_class = getattr(module, module_name)
            except AttributeError as exc:
                raise ImportError(
                    f"Expected class '{module_name}' inside module '{module_name}'."
                ) from exc

            loaded_blocks[module_name] = fb_class

        return loaded_blocks