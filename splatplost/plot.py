import json
from typing import Type, Union

import numpy as np
from libnxctrl.wrapper import Button, NXWrapper
from scipy.spatial.distance import cityblock as manhattan_distance

from splatplost.version import __version__


def reset_from_loc(end_point, start_point) -> tuple[list[tuple[Button, int]], tuple[int, int]]:
    """
    Reset the cursor to the nearest point.
    """
    direction_map = {
        'up':    Button.DPAD_UP,
        'down':  Button.DPAD_DOWN,
        'left':  Button.DPAD_LEFT,
        'right': Button.DPAD_RIGHT,
        }
    distance_min = np.array([manhattan_distance(end_point, (0, 0)) + manhattan_distance(start_point, (0, 0)),
                             manhattan_distance(end_point, (119, 0)) + manhattan_distance(start_point, (119, 0)),
                             manhattan_distance(end_point, (0, 319)) + manhattan_distance(start_point, (0, 319)),
                             manhattan_distance(end_point, (119, 319)) + manhattan_distance(start_point, (119, 319))]
                            ).argmin()

    point_location = [("left", "up"), ("left", "down"), ("right", "up"), ("right", "down")]

    point = [(0, 0), (119, 0), (0, 319), (119, 319)]

    return [(direction_map[d], 8000) for d in point_location[distance_min]], point[distance_min]


def march(from_point: tuple[int, int], to_point: tuple[int, int]) -> list[tuple[Button, int]]:
    """
    March from one point to another.
    """
    direction_map = {
        'up':    Button.DPAD_UP,
        'down':  Button.DPAD_DOWN,
        'left':  Button.DPAD_LEFT,
        'right': Button.DPAD_RIGHT,
        }
    output_q = []
    ver = to_point[0] - from_point[0]
    hor = to_point[1] - from_point[1]
    if ver > 0:
        output_q += [direction_map['down']] * ver
    else:
        output_q += [direction_map['up']] * (-ver)
    if hor > 0:
        output_q += [direction_map['right']] * hor
    else:
        output_q += [direction_map['left']] * (-hor)
    return output_q


def parse_coord(coord: str) -> tuple[int, int]:
    """
    Parse the coordinate string to tuple.
    """
    t = coord.split(',')
    if len(t) != 2:
        raise ValueError("Invalid coordinate string: {}".format(coord))
    return int(t[0]), int(t[1])


def execute_command_list(command_list: list[Union[Button, tuple[Button, int]]], connection: NXWrapper,
                         stable_mode: bool = False) -> None:
    """
    Execute the command list.
    """
    if stable_mode:
        connection.series_press(command_list)
    else:
        for command in command_list:
            if isinstance(command, tuple):
                connection.button_hold(command[0], command[1])
            else:
                connection.button_press(command)


def plot_block(block, block_name, current_position):
    print("Plotting block {}".format(block_name))
    command_list: list[Union[Button, tuple[Button, int]]] = []
    entry_point = parse_coord(block["entry_point"])
    # Goto entry point
    command_list_new, current_position = reset_from_loc(current_position, entry_point)
    command_list += command_list_new
    for item in block["visit_route"]:
        coordinate = parse_coord(item)
        command_list += march(current_position, coordinate)
        command_list += [Button.A]
        current_position = coordinate
    return command_list, current_position


def plot(order_file: str, backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100,
         stable_mode: bool = False, clear_drawing: bool = True) -> None:

    # Connect to the Switch
    connection = backend(press_duration_ms=press_duration_ms, delay_ms=delay_ms)
    print("Open the pairing menu on switch.")
    connection.connect()

    # Enter the drawing mode
    t = "Placeholder"
    while t.strip() != "":
        t = input("Press <enter> to draw, or some words ending "
                  "with <enter> to press the A on the pairing menu."
                  )
        if t.strip() == "":
            break
        connection.button_press(Button.A)

    command_list: list[Union[Button, tuple[Button, int]]] = []
    # Goto (0,0) point
    command_list += reset_from_loc((0, 0), (0, 0))
    # Press clear button
    if clear_drawing:
        command_list += [Button.MINUS]

    # Execute
    execute_command_list(command_list, connection, stable_mode=stable_mode)

    # Start plotting
    with open(order_file, 'r') as f:
        try:
            content = json.load(f)
        except json.JSONDecodeError:
            print("Error: Generated plan file uses version ~= 0.1.0, "
                  "but current version is {}. Please regenerate plan file.".format(__version__)
                  )
            return

    if content["splatplost_version"] != __version__:
        print("Error: Generated plan file uses version {}, ""but current version is {}. "
              "Please regenerate plan file.".format(content["splatplost_version"], __version__)
              )
        return

    print("Total print blocks: {}".format(len(content["blocks"])))

    current_position = (0, 0)

    for block_name, block in content["blocks"].items():
        command_list, current_position = plot_block(block, block_name, current_position)
        # TODO: ask for confirmation
        execute_command_list(command_list, connection, stable_mode=stable_mode)

    connection.disconnect()
