from random import randint

import numpy as np
from libnxctrl.wrapper import Button, NXWrapper


class PseudoS2Wrapper(NXWrapper):
    def __init__(self, press_duration_ms: int = 50, delay_ms: int = 120):
        super().__init__(press_duration_ms=press_duration_ms, delay_ms=delay_ms)
        self.result = np.ones((120, 320))
        self.current_cursor: tuple[int, int] = (randint(0, 119), randint(0, 319))
        self.move_speed = 800  # TODO: to be confirm

    def connect(self):
        pass

    def button_hold(self, button_name: Button, duration_ms: int):
        if button_name == Button.MINUS:
            self.result = np.ones((120, 320))
        elif button_name == Button.DPAD_UP:
            if duration_ms < 200:
                self.current_cursor = (
                    max(0, self.current_cursor[0] - 1),
                    self.current_cursor[1],
                    )
            else:
                self.current_cursor = (
                    max(0, self.current_cursor[0] - int(duration_ms * self.move_speed)),
                    self.current_cursor[1],
                    )
        elif button_name == Button.DPAD_DOWN:
            if duration_ms < 200:
                self.current_cursor = (
                    min(119, self.current_cursor[0] + 1),
                    self.current_cursor[1],
                    )
            else:
                self.current_cursor = (
                    min(119, self.current_cursor[0] + int(duration_ms * self.move_speed)),
                    self.current_cursor[1],
                    )
        elif button_name == Button.DPAD_LEFT:
            if duration_ms < 200:
                self.current_cursor = (
                    self.current_cursor[0],
                    max(0, self.current_cursor[1] - 1),
                    )
            else:
                self.current_cursor = (
                    self.current_cursor[0],
                    max(0, self.current_cursor[1] - int(duration_ms * self.move_speed)),
                    )
        elif button_name == Button.DPAD_RIGHT:
            if duration_ms < 200:
                self.current_cursor = (
                    self.current_cursor[0],
                    min(319, self.current_cursor[1] + 1),
                    )
            else:
                self.current_cursor = (
                    self.current_cursor[0],
                    min(319, self.current_cursor[1] + int(duration_ms * self.move_speed)),
                    )
        elif button_name == Button.A:
            self.result[self.current_cursor] = 0

    def disconnect(self):
        pass

    def get_result(self):
        return self.result


class PseudoS3Wrapper(NXWrapper):
    def __init__(self, press_duration_ms: int = 50, delay_ms: int = 120):
        super().__init__(press_duration_ms=press_duration_ms, delay_ms=delay_ms)
        self.result = np.ones((120, 320))
        self.current_cursor: tuple[int, int] = (randint(0, 119), randint(0, 319))
        self.move_speed = 800  # TODO: to be confirm

    def connect(self):
        pass

    def button_hold(self, button_name: Button, duration_ms: int):
        if button_name == Button.L_STICK_PRESS:
            self.result = np.ones((120, 320))
        elif button_name == Button.DPAD_UP:
            if duration_ms < 200:
                self.current_cursor = (
                    max(0, self.current_cursor[0] - 1),
                    self.current_cursor[1],
                    )
            else:
                self.current_cursor = (
                    max(0, self.current_cursor[0] - int(duration_ms * self.move_speed)),
                    self.current_cursor[1],
                    )
        elif button_name == Button.DPAD_DOWN:
            if duration_ms < 200:
                self.current_cursor = (
                    min(119, self.current_cursor[0] + 1),
                    self.current_cursor[1],
                    )
            else:
                self.current_cursor = (
                    min(119, self.current_cursor[0] + int(duration_ms * self.move_speed)),
                    self.current_cursor[1],
                    )
        elif button_name == Button.DPAD_LEFT:
            if duration_ms < 200:
                self.current_cursor = (
                    self.current_cursor[0],
                    max(0, self.current_cursor[1] - 1),
                    )
            else:
                self.current_cursor = (
                    self.current_cursor[0],
                    max(0, self.current_cursor[1] - int(duration_ms * self.move_speed)),
                    )
        elif button_name == Button.DPAD_RIGHT:
            if duration_ms < 200:
                self.current_cursor = (
                    self.current_cursor[0],
                    min(319, self.current_cursor[1] + 1),
                    )
            else:
                self.current_cursor = (
                    self.current_cursor[0],
                    min(319, self.current_cursor[1] + int(duration_ms * self.move_speed)),
                    )
        elif button_name == Button.A:
            self.result[self.current_cursor] = 0

    def disconnect(self):
        pass

    def get_result(self):
        return self.result
