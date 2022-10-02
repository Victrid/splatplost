import enum
from typing import Union

from libnxctrl.wrapper import Button

Command = Union[tuple[Button, int], Button]
CommandList = list[Command]
Coordinate = tuple[int, int]


class BrushSize(enum.Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
