from abc import abstractmethod

from libnxctrl.wrapper import Button

from splatplost.common import BrushSize, CommandList


class KeyBinding:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def draw(self, brush_size: BrushSize) -> CommandList:
        pass

    @abstractmethod
    def erase(self, brush_size: BrushSize) -> CommandList:
        pass

    @staticmethod
    @abstractmethod
    def clear() -> CommandList:
        pass


class Splatoon2KeyBinding(KeyBinding):
    brush_binding = {
        BrushSize.SMALL:  BrushSize.MEDIUM,
        BrushSize.MEDIUM: BrushSize.LARGE,
        BrushSize.LARGE:  BrushSize.SMALL,
        }

    def __init__(self):
        self.brush_size = BrushSize.SMALL
        self.isBrush = True

    def _progress_brush(self):
        if self.isBrush:
            self.isBrush = False
        else:
            self.isBrush = True
            self.brush_size = self.brush_binding[self.brush_size]

    def draw(self, brush_size: BrushSize) -> CommandList:
        commands: CommandList = []
        while self.brush_size != brush_size or not self.isBrush:
            self._progress_brush()
            commands += [Button.SHOULDER_R]

        commands += [Button.A]
        return commands

    def erase(self, brush_size: BrushSize) -> CommandList:
        commands: CommandList = []
        while self.brush_size != brush_size or self.isBrush:
            self._progress_brush()
            commands += [Button.SHOULDER_R]

        commands += [Button.A]
        return commands

    @staticmethod
    @abstractmethod
    def clear() -> CommandList:
        return [Button.MINUS]


class Splatoon3KeyBinding(KeyBinding):
    brush_binding = {
        BrushSize.SMALL:  BrushSize.MEDIUM,
        BrushSize.MEDIUM: BrushSize.LARGE,
        BrushSize.LARGE:  BrushSize.SMALL,
        }

    def __init__(self):
        self.brush_size = BrushSize.SMALL

    def _progress_brush(self):
        self.brush_size = self.brush_binding[self.brush_size]

    def draw(self, brush_size: BrushSize) -> CommandList:
        commands: CommandList = []
        while self.brush_size != brush_size:
            self._progress_brush()
            commands += [Button.SHOULDER_R]

        commands += [Button.A]
        return commands

    def erase(self, brush_size: BrushSize) -> CommandList:
        commands: CommandList = []
        while self.brush_size != brush_size:
            self._progress_brush()
            commands += [Button.SHOULDER_R]

        commands += [Button.B]
        return commands

    @staticmethod
    @abstractmethod
    def clear() -> CommandList:
        return [Button.L_STICK_PRESS]