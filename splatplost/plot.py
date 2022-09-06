import json
from typing import Type

import numpy as np
from libnxctrl.wrapper import Button, NXWrapper
from scipy.spatial.distance import cityblock as manhattan_distance

from splatplost.version import __version__

# Type aliases
Command = tuple[Button, int] | Button
CommandList = list[Command]
Coordinate = tuple[int, int]


def reset_cursor_position(end_point, start_point) -> tuple[CommandList, Coordinate]:
    """
    Reset the cursor to the nearest point.

    :param end_point: The current position of the cursor.
    :param start_point: The target position of the cursor.
    :return: The command list and the new position of the cursor.
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


def march(from_point: Coordinate, to_point: Coordinate) -> CommandList:
    """
    March from one point to another.

    :param from_point: The starting point.
    :param to_point: The ending point.
    :return: The command list.
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


def parse_coordinate(coord: str) -> Coordinate:
    """
    Parse and validate the coordinate string (shaped as `123,456`) to tuple.

    :param coord: The coordinate string.
    :return: The coordinate tuple.
    """
    t = coord.split(',')
    if len(t) != 2:
        raise ValueError("Invalid coordinate string: {}".format(coord))
    if not (0 <= int(t[0]) <= 119 and 0 <= int(t[1]) <= 319):
        raise ValueError("Invalid coordinate string: {}".format(coord))
    return int(t[0]), int(t[1])


def execute_command_list(command_list: CommandList, connection: NXWrapper,
                         stable_mode: bool = False) -> None:
    """
    Execute the command list.

    :param command_list: The command list to execute.
    :param connection: The connection to the switch.
    :param stable_mode: Whether to use stable mode.
    """
    if stable_mode:
        connection.series_press(command_list)
    else:
        for command in command_list:
            if isinstance(command, tuple):
                connection.button_hold(command[0], command[1])
            else:
                connection.button_press(command)


def plot_block(entry_point: Coordinate, route: list[Coordinate], position: Coordinate) -> tuple[
    CommandList, Coordinate]:
    """
    Plot a block.

    :param entry_point: The entry point of the block.
    :param route: The route, of plotting dots, of the block.
    :param position: The current position of the cursor.
    :return: The command list and the new position of the cursor.
    """
    # Goto entry point
    command_list, position = reset_cursor_position(position, entry_point)
    for coordinate in route:
        command_list += march(position, coordinate)
        command_list += [Button.A]
        position = coordinate
    return command_list, position


def plot(order_file: str, backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100,
         stable_mode: bool = False, clear_drawing: bool = True) -> None:
    """
    Plot the order file.

    :param order_file: The order file in JSON format.
    :param backend: The backend to use.
    :param delay_ms: The delay between each press down.
    :param press_duration_ms: The duration of each press down.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    """

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

    command_list: CommandList = []
    # Goto (0,0) point
    command_list += reset_cursor_position((0, 0), (0, 0))
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
        command_list, current_position = plot_block(
                entry_point=parse_coordinate(block["entry_point"]),
                route=[parse_coordinate(coord) for coord in block["visit_route"]],
                position=current_position
                )
        # TODO: ask for confirmation
        execute_command_list(command_list, connection, stable_mode=stable_mode)

    connection.disconnect()
