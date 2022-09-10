import json
from typing import NamedTuple, Union

import numpy as np
from PIL import Image
from scipy.spatial.distance import cityblock as manhattan_distance
from skimage import measure
from tsp_solver.greedy_numpy import solve_tsp as tsp_solver_greedy


class BlockVisit(NamedTuple):
    """
    A named tuple to store the block visit information.
    """
    empty: bool
    entry_point: Union[np.ndarray | tuple[int, int]]
    exit_point: Union[np.ndarray | tuple[int, int]]
    visit_route: list[np.ndarray]


def is_coordinate_valid(x: int, y: int) -> bool:
    """
    Check if the coordinate is valid

    :param x: The x coordinate
    :param y: The y coordinate
    :return: True if the coordinate is valid, False otherwise
    """
    return 0 <= x < 120 and 0 <= y < 320


def load_images(input_file_name: str) -> np.ndarray:
    """
    Load the image from the input file

    :param input_file_name: The input file name
    :return: The image in binary numpy array, where 1 is black and 0 is white
    """
    im = Image.open(input_file_name)
    if not (im.size[0] == 320 and im.size[1] == 120):
        raise ValueError("Image must be 320px by 120px!")
    im = im.convert("1")
    image = np.array(im.getdata()).reshape(120, 320) / 255
    return 1 - image.astype(int)


def divide_image(image: np.ndarray, vertical_divider: int = 8,
                 horizontal_divider: int = 3) -> list[tuple[tuple[int, int], np.ndarray]]:
    """
    Divide the image into parts to prevent errors in drawing

    :param image: The image to be divided
    :param vertical_divider: The number of horizontal parts
    :param horizontal_divider: The number of vertical parts
    """
    image_list = []
    # Check if divider is valid
    if 320 % vertical_divider != 0:
        raise ValueError("Horizontal divider must be a divisor of 320")
    if 120 % horizontal_divider != 0:
        raise ValueError("Vertical divider must be a divisor of 120")
    for i in range(0, 120, 120 // horizontal_divider):
        for j in range(0, 320, 320 // vertical_divider):
            image_list.append(((i, j), image[i:i + 120 // horizontal_divider, j:j + 320 // vertical_divider],))
    return image_list


def get_label(image: np.ndarray) -> tuple[np.ndarray, int]:
    """
    Get connected components of the image and return the label.

    :param image: The image to be processed
    :return: A tuple of labeled image and the number of labels
    """
    label = measure.label(image, connectivity=1, background=0)
    label_count = np.max(label)
    return label, label_count


def generate_dense_visit(labeled_image: np.ndarray, label_selector: int, image_offset: np.ndarray) -> list[np.ndarray]:
    """
    Generate a list of points that dense label is visited

    :param labeled_image: The labeled image, with background as 0 and connected components as 1, 2, 3, ...
    :param label_selector: The label to be processed
    :param image_offset: The offset to original image of (0,0) of the image block
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

    :param entry_exit_point: A list of tuple, each tuple contains the entry point and exit point of a drawing block
    :param greedy: The number of points to be used in greedy algorithm
    """
    distance_matrix = np.zeros((len(entry_exit_point), len(entry_exit_point)))
    for i in range(len(entry_exit_point)):
        for j in range(len(entry_exit_point)):
            if i == j or j == 0:
                continue
            distance_matrix[i][j] = manhattan_distance(entry_exit_point[i][1], entry_exit_point[j][0])
    permutation = tsp_solver_greedy(distance_matrix, optim_steps=greedy, endpoints=(0, None))
    return permutation


def generate_block_visit(image_block: np.ndarray, image_offset: np.ndarray) -> BlockVisit:
    """
    Generate a list of points that dense label is visited

    :param image_block: The image block to be processed
    :param image_offset: The offset to original image of (0,0) of the image block
    :return: A named tuple of BlockVisit
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
    """
    Generate a route file for the input image

    :param input_file: Input file name
    :param output: Output file name
    :param horizontal_divider: Divide how many blocks horizontally (must be a divisor of 320)
    :param vertical_divider: Divide how many blocks vertically (must be a divisor of 120)
    """
    from splatplost.version import __version__
    image = load_images(input_file)
    divided_image = divide_image(image, vertical_divider=horizontal_divider, horizontal_divider=vertical_divider)
    visit_list: list[tuple[tuple[int, int], int, BlockVisit]] = []
    for block_idx, item in enumerate(divided_image):
        block_visit = generate_block_visit(item[1], np.array(item[0]))
        if block_visit.empty:
            continue
        visit_list.append((item[0], block_idx, block_visit))

    output_dict = {
        "splatplost_version": __version__,
        "divide_schedule":    {
            "vertical_divider": horizontal_divider,
            "horizontal_divider":   vertical_divider
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
        json.dump(output_dict, f, indent=2)
