import enum

from libnxctrl.wrapper import Button

Command = tuple[Button, int] | Button
CommandList = list[Command]
Coordinate = tuple[int, int]


class BrushSize(enum.Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
