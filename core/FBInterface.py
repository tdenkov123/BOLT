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

    