from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type

@dataclass
class FBInterface:
    ei_names: tuple[str, ...] = ()
    eo_names: tuple[str, ...] = ()
    di_names: tuple[str, ...] = ()
    di_types: tuple[Type, ...] = ()
    do_names: tuple[str, ...] = ()
    do_types: tuple[Type, ...] = ()

    def get_ei_id(self, name: str) -> int | None:
        try:
            return self.ei_names.index(name)
        except ValueError:
            return None

    def get_eo_id(self, name: str) -> int | None:
        try:
            return self.eo_names.index(name)
        except ValueError:
            return None

    def get_di_id(self, name: str) -> int | None:
        try:
            return self.di_names.index(name)
        except ValueError:
            return None

    def get_do_id(self, name: str) -> int | None:
        try:
            return self.do_names.index(name)
        except ValueError:
            return None


    @property
    def num_eis(self) -> int:
        return len(self.ei_names)

    @property
    def num_eos(self) -> int:
        return len(self.eo_names)

    @property
    def num_dis(self) -> int:
        return len(self.di_names)

    @property
    def num_dos(self) -> int:
        return len(self.do_names)
