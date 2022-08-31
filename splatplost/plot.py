from time import sleep
from typing import Type

import tqdm
from libnxctrl.wrapper import Button, NXWrapper


def reset(connection: NXWrapper, direction=None):
    direction_map = {
        'up':    Button.DPAD_UP,
        'down':  Button.DPAD_DOWN,
        'left':  Button.DPAD_LEFT,
        'right': Button.DPAD_RIGHT,
        }
    if direction is None:
        direction = ['left', 'up']
    for d in direction:
        connection.button_hold(direction_map[d], duration_ms=5000)


def plot(order_list: list[str], backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100):
    connection = backend(press_duration_ms=press_duration_ms)
    print("Open the pairing menu on switch.")
    connection.connect()

    t = "Placeholder"
    while t.strip() != "":
        t = input("Press <enter> to draw, or some words ending "
                  "with <enter> to press the A on the pairing menu."
                  )
        connection.button_press(Button.A)

    # Goto (0,0) point
    reset(connection, ['left', 'up'])

    # Clear
    connection.button_press(Button.MINUS)
    sleep(0.5)

    for order in tqdm.tqdm(order_list):
        order = order.strip()
        reset_map = {
            'lu': lambda: reset(connection, ['left', 'up']),
            'ru': lambda: reset(connection, ['right', 'up']),
            'ld': lambda: reset(connection, ['left', 'down']),
            'rd': lambda: reset(connection, ['right', 'down']),
            }
        button_map = {
            "up":    Button.DPAD_UP,
            "down":  Button.DPAD_DOWN,
            "left":  Button.DPAD_LEFT,
            "right": Button.DPAD_RIGHT,
            "a":     Button.A,
            "b":     Button.B,
            "x":     Button.X,
            "y":     Button.Y,
            }
        if order in reset_map:
            reset_map[order]()
        elif order in button_map:
            connection.button_press(button_map[order])
        sleep(delay_ms / 1000)

    connection.disconnect()
