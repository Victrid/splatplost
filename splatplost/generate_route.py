import json
import sys
from typing import NamedTuple, Union

import numpy as np
from PIL import Image
from scipy.spatial.distance import cityblock as manhattan_distance
from skimage import measure
from tsp_solver.greedy_numpy import solve_tsp as tsp_solver_greedy

from .tsp_solver_dp import solve_tsp_dynamic_programming as tsp_solver_dp


class BlockVisit(NamedTuple):
    empty: bool
    entry_point: Union[np.ndarray | tuple[int, int]]
    exit_point: Union[np.ndarray | tuple[int, int]]
    visit_route: list[np.ndarray]


def is_coordinate_valid(x: int, y: int) -> bool:
    return 0 <= x < 120 and 0 <= y < 320


def load_images(input_file_name: str) -> np.ndarray:
    im = Image.open(input_file_name)
    if not (im.size[0] == 320 and im.size[1] == 120):
        print("ERROR: Image must be 320px by 120px!")
        sys.exit()
    im = im.convert("1")
    image = np.array(im.getdata()).reshape(120, 320) / 255
    return 1 - image.astype(int)


def divide_image(image: np.ndarray, horizontal_divider: int = 8, vertical_divider: int = 3) -> list[
    tuple[tuple[int, int], np.ndarray]]:
    # Divide the image into parts to prevent errors in drawing
    image_list = []
    # Check if divider is valid
    if 320 % horizontal_divider != 0:
        raise ValueError("Horizontal divider must be a divisor of 320")
    if 120 % vertical_divider != 0:
        raise ValueError("Vertical divider must be a divisor of 120")
    for i in range(0, 120, 120 // vertical_divider):
        for j in range(0, 320, 320 // horizontal_divider):
            image_list.append(((i, j), image[i:i + 120 // vertical_divider, j:j + 320 // horizontal_divider],))
    return image_list


def get_label(image: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Get connected components of the image and return the label
    """
    label = measure.label(image, connectivity=1, background=0)
    label_count = np.max(label)
    return label, label_count


def generate_dense_visit(labeled_image: np.ndarray, label_selector: int, image_offset: np.ndarray) -> list[np.ndarray]:
    """
    Generate a list of points that dense label is visited
    """
    to_be_visited = (labeled_image == label_selector)
    current_row = np.argwhere(to_be_visited)[0][0]
    go_right = True
    visit_list: list[np.ndarray] = []
    current_list = []
    for item in np.argwhere(to_be_visited):
        if item[0] == current_row:
            current_list.append(item + image_offset)
        else:
            visit_list += current_list if go_right else reversed(current_list)
            current_row = item[0]
            go_right = not go_right
            current_list = [item + image_offset]
    visit_list += current_list if go_right else reversed(current_list)
    return visit_list


def get_entry_exit_point_min_distance(entry_exit_point: list[tuple[np.ndarray, np.ndarray]],
                                      greedy: int = 3) -> list[int]:
    """
    For each drawing block, having an entry point and an exit point. Find the minimum distance to travel through
    all drawing blocks, from one's exit point to another one's entry point.
    """
    distance_matrix = np.zeros((len(entry_exit_point), len(entry_exit_point)))
    for i in range(len(entry_exit_point)):
        for j in range(len(entry_exit_point)):
            if i == j or j == 0:
                continue
            distance_matrix[i][j] = manhattan_distance(entry_exit_point[i][1], entry_exit_point[j][0])
    if greedy != -1:
        permutation = tsp_solver_greedy(distance_matrix, optim_steps=greedy, endpoints=(0, None))
    else:
        permutation, _ = tsp_solver_dp(distance_matrix)
    return permutation


def generate_block_visit(image_block: np.ndarray, image_offset: np.ndarray) -> BlockVisit:
    """
    Generate a list of points that dense label is visited
    """
    label, label_count = get_label(image_block)
    if label_count == 0:
        return BlockVisit(empty=True, visit_route=[], entry_point=(-1, -1), exit_point=(-1, -1))
    internal_routes = [generate_dense_visit(label, label_idx, image_offset) for label_idx in
                       range(1, label_count + 1)]
    offset_entry_exit_point = [(t[0], t[-1]) for t in internal_routes]
    arrangement = get_entry_exit_point_min_distance(offset_entry_exit_point, greedy=16)
    visit_list = []
    for i in arrangement:
        visit_list += internal_routes[i]

    if len(visit_list) > 0:
        return BlockVisit(empty=False, visit_route=visit_list, entry_point=visit_list[0], exit_point=visit_list[-1])
    else:
        return BlockVisit(empty=True, visit_route=[], entry_point=(-1, -1), exit_point=(-1, -1))


def generate_route_file(input_file: str, output: str, horizontal_divider: int = 8, vertical_divider: int = 3) -> None:
    from splatplost.version import __version__
    image = load_images(input_file)
    divided_image = divide_image(image, horizontal_divider=horizontal_divider, vertical_divider=vertical_divider)
    visit_list: list[tuple[tuple[int, int], int, BlockVisit]] = []
    for block_idx, item in enumerate(divided_image):
        block_visit = generate_block_visit(item[1], np.array(item[0]))
        if block_visit.empty:
            continue
        visit_list.append((item[0], block_idx, block_visit))

    output_dict = {
        "splatplost_version": __version__,
        "divide_schedule":    {
            "horizontal_divider": horizontal_divider,
            "vertical_divider":   vertical_divider
            }
        }
    blocks = dict()
    for index, block_idx, visit in visit_list:
        blocks["{}".format(block_idx)] = {
            "entry_point": "{},{}".format(visit.entry_point[0], visit.entry_point[1]),
            "exit_point":  "{},{}".format(visit.exit_point[0], visit.exit_point[1]),
            "visit_route": ["{},{}".format(s[0], s[1]) for s in visit.visit_route]
            }
    output_dict["blocks"] = blocks

    with open(output, "w") as f:
        json.dump(output_dict, f, indent=4)
