import json
from typing import Type

import numpy as np
from libnxctrl.wrapper import Button, NXWrapper
from scipy.spatial.distance import cityblock as manhattan_distance

from splatplost.common import BrushSize, CommandList, Coordinate
from splatplost.generate_route import generate_dense_visit
from splatplost.keybindings import KeyBinding, Splatoon2KeyBinding, Splatoon3KeyBinding
from splatplost.version import __version__


def reset_cursor_position(end_point, start_point, press_time) -> tuple[CommandList, Coordinate]:
    """
    Reset the cursor to the nearest reset corner point.

    :param end_point: The current position of the cursor.
    :param start_point: The target position of the cursor.
    :param press_time: The time to hold the button.
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

    return [(direction_map[d], press_time) for d in point_location[distance_min]], point[distance_min]


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


def plot_block(entry_point: Coordinate, route: list[Coordinate], position: Coordinate, keyBinding: KeyBinding,
               cursor_reset: bool, cursor_reset_time: int) -> tuple[CommandList, Coordinate]:
    """
    Plot a block.

    :param entry_point: The entry point of the block.
    :param route: The route, of plotting dots, of the block.
    :param position: The current position of the cursor.
    :param keyBinding: The key binding.
    :param cursor_reset: Whether to reset the cursor.
    :param cursor_reset_time: The time to hold the button to reset the cursor.
    :return: The command list and the new position of the cursor.
    """
    # Goto entry point
    if cursor_reset:
        command_list, position = reset_cursor_position(position, entry_point, cursor_reset_time)
    else:
        command_list = []
    for coordinate in route:
        command_list += march(position, coordinate)
        command_list += keyBinding.draw(BrushSize.SMALL)
        position = coordinate
    return command_list, position


def get_range(
        block_index: int, horizontal_divider: int = 3, vertical_divider: int = 8) -> tuple[Coordinate, Coordinate]:
    """
    Calculate the range of the block.

    :param block_index: The index of the block.
    :param horizontal_divider: The number of horizontal dividers.
    :param vertical_divider: The number of vertical dividers.
    :return: The range of the block.
    """
    index_on_width_direction = block_index % vertical_divider
    index_on_height_direction = block_index // vertical_divider
    return (
               index_on_height_direction * 120 // horizontal_divider,
               index_on_width_direction * 320 // vertical_divider
               ), (
               (index_on_height_direction + 1) * 120 // horizontal_divider,
               (index_on_width_direction + 1) * 320 // vertical_divider,
               )


def get_loc_from_index(width: int, height: int, horizontal_divider: int, vertical_divider: int) -> int:
    """
    Calculate the index of the block.

    :param width: The x coordinate of the block.
    :param height: The y coordinate of the block.
    :param horizontal_divider: The number of horizontal dividers.
    :param vertical_divider: The number of vertical dividers.
    :return: The index of the block.
    """
    block_size = (120 // horizontal_divider, 320 // vertical_divider)
    return (width // block_size[0]) + (height // block_size[1]) * vertical_divider


def erase_block(block_index: int, position: Coordinate, horizontal_divider: int, vertical_divider: int,
                key_binding: KeyBinding, cursor_reset: bool, cursor_reset_time: int) -> tuple[CommandList, Coordinate]:
    """
    Erase a block.

    :param block_index: The index of the block.
    :param position: Current position of the cursor.
    :param horizontal_divider: The number of horizontal dividers.
    :param vertical_divider: The number of vertical dividers.
    :param key_binding: The key binding.
    :param cursor_reset: Whether to reset the cursor.
    :param cursor_reset_time: The time to reset the cursor.
    :return: The command list and the new position of the cursor.
    """
    # Goto entry point
    start_point, end_point = get_range(block_index, horizontal_divider=horizontal_divider,
                                       vertical_divider=vertical_divider
                                       )
    plot_size = ((end_point[0] - start_point[0]), (end_point[1] - start_point[1]))
    block = np.ones(plot_size)
    coords_list: list[Coordinate] = [(t[0], t[1]) for t in generate_dense_visit(block, 1, np.array(start_point))]

    # Goto entry point
    if cursor_reset:
        command_list, position = reset_cursor_position(position, start_point, cursor_reset_time)
    else:
        command_list = []

    for coordinate in coords_list:
        command_list += march(position, coordinate)
        command_list += key_binding.erase(BrushSize.SMALL)
        position = coordinate

    return command_list, position


def partial_erase(order_file: str, backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100,
                  stable_mode: bool = False, clear_drawing: bool = False, splatoon3: bool = False,
                  plot_blocks: list[int] = None) -> None:
    """
    Clean blocks.

    :param order_file: The order file in JSON format.
    :param backend: The backend to use.
    :param delay_ms: The delay between each press down.
    :param press_duration_ms: The duration of each press down.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    :param splatoon3: Whether to use Splatoon 3 mode.
    :param plot_blocks: The blocks to plot.
    """
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

    key_binding = Splatoon3KeyBinding() if splatoon3 else Splatoon2KeyBinding()

    partial_erase_with_conn(connection=connection, key_binding=key_binding,
                            horizontal_divider=content["divide_schedule"]["horizontal_divider"],
                            vertical_divider=content["divide_schedule"]["vertical_divider"], cursor_reset=True,
                            cursor_reset_time=10000, stable_mode=stable_mode, clear_drawing=clear_drawing,
                            plot_blocks=plot_blocks
                            )

    connection.disconnect()


def partial_erase_with_conn(connection: NXWrapper, key_binding: KeyBinding, horizontal_divider: int,
                            vertical_divider: int, cursor_reset, cursor_reset_time, stable_mode: bool = False,
                            clear_drawing: bool = False, plot_blocks: list[int] = None) -> None:
    """
    Clean blocks.

    :param connection: The connection to the Switch.
    :param key_binding: The key binding.
    :param horizontal_divider: The number of horizontal dividers.
    :param vertical_divider: The number of vertical dividers.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    :param plot_blocks: The blocks to plot.
    """

    # Goto (0,0) point
    command_list, current_position = reset_cursor_position((0, 0), (0, 0), cursor_reset_time)
    # Press clear button
    if clear_drawing:
        command_list += key_binding.clear()
        # If clear button is pressed, we don't need to continue to erasing.
        execute_command_list(command_list, connection, stable_mode=stable_mode)
        return

    # Execute
    execute_command_list(command_list, connection, stable_mode=stable_mode)

    for index in plot_blocks:
        command_list, current_position = erase_block(block_index=index, position=current_position,
                                                     horizontal_divider=horizontal_divider,
                                                     vertical_divider=vertical_divider, key_binding=key_binding,
                                                     cursor_reset=cursor_reset, cursor_reset_time=cursor_reset_time
                                                     )
        execute_command_list(command_list, connection, stable_mode=stable_mode)


def partial_plot_with_conn(connection: NXWrapper, blocks, key_binding: KeyBinding, cursor_reset, cursor_reset_time,
                           stable_mode: bool = False, clear_drawing: bool = False,
                           plot_blocks: list[int] = None) -> None:
    """
    Plot blocks.

    :param connection: The connection to the Switch.
    :param blocks: The blocks scheme.
    :param key_binding: The key binding.
    :param cursor_reset: whether to reset the cursor between each block.
    :param cursor_reset_time: The time to reset the cursor.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    :param plot_blocks: The blocks to plot.
    """
    # Goto (0,0) point
    command_list, current_position = reset_cursor_position((0, 0), (0, 0), cursor_reset_time)
    # Press clear button
    if clear_drawing:
        command_list += key_binding.clear()
    # Execute
    execute_command_list(command_list, connection, stable_mode=stable_mode)

    # Start plotting

    for block_name, block in blocks:
        if int(block_name) not in plot_blocks:
            continue
        command_list, current_position = plot_block(entry_point=parse_coordinate(block["entry_point"]),
                                                    route=[parse_coordinate(coord) for coord in block["visit_route"]],
                                                    position=current_position, keyBinding=key_binding,
                                                    cursor_reset=cursor_reset, cursor_reset_time=10000
                                                    )
        execute_command_list(command_list, connection, stable_mode=stable_mode)


def partial_plot(order_file: str, backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100,
                 stable_mode: bool = False, clear_drawing: bool = False, splatoon3: bool = False,
                 plot_blocks: list[int] = None) -> None:
    """
    Plot blocks.

    :param order_file: The order file in JSON format.
    :param backend: The backend to use.
    :param delay_ms: The delay between each press down.
    :param press_duration_ms: The duration of each press down.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    :param splatoon3: Whether to use Splatoon 3 mode.
    :param plot_blocks: The blocks to plot.
    """
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

    partial_plot_with_conn(connection=connection, blocks=content["blocks"].items(),
                           key_binding=Splatoon3KeyBinding() if splatoon3 else Splatoon2KeyBinding(),
                           cursor_reset=False, cursor_reset_time=10000, stable_mode=stable_mode,
                           clear_drawing=clear_drawing, plot_blocks=plot_blocks
                           )
    connection.disconnect()


def plot(order_file: str, backend: Type[NXWrapper], delay_ms: int = 100, press_duration_ms: int = 100,
         stable_mode: bool = False, clear_drawing: bool = True, splatoon3: bool = False) -> None:
    """
    Plot the order file.

    :param order_file: The order file in JSON format.
    :param backend: The backend to use.
    :param delay_ms: The delay between each press down.
    :param press_duration_ms: The duration of each press down.
    :param stable_mode: Whether to use stable mode.
    :param clear_drawing: Whether to clear the plot before plotting.
    :param splatoon3: Whether to use Splatoon 3 mode.
    """
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

    plot_blocks = [int(i) for i in content["blocks"].keys()]

    partial_plot(order_file, backend, delay_ms, press_duration_ms, stable_mode, clear_drawing, splatoon3, plot_blocks)
