import sys

import numpy as np
from PIL import Image
from scipy.spatial.distance import cityblock as manhattan_distance
from skimage import measure
from tsp_solver.greedy_numpy import solve_tsp as tsp_solver_greedy

from .tsp_solver_dp import solve_tsp_dynamic_programming as tsp_solver_dp


class ResetPosition:
    def __init__(self, left: bool, up: bool):
        self.left = left
        self.up = up

    def get_command(self):
        if self.left:
            return "lu" if self.up else "ld"
        else:
            return "ru" if self.up else "rd"

    def get_position(self):
        if self.left:
            return (0, 0) if self.up else (119, 0)
        else:
            return (0, 319) if self.up else (119, 319)


def is_coordinate_valid(x: int, y: int) -> bool:
    return 0 <= x < 120 and 0 <= y < 320


def find_nearest_reset_position(point: np.ndarray) -> ResetPosition:
    t = np.array([manhattan_distance(point, (0, 0)),
                  manhattan_distance(point, (119, 0)),
                  manhattan_distance(point, (0, 319)),
                  manhattan_distance(point, (119, 319))]
                 ).argmin()

    return ResetPosition(t % 2 == 0, t // 2 == 0)


def goto_next_point(current_point, next_point, draw=True):
    def march(a, b):
        output_q = []
        ver = b[0] - a[0]
        hor = b[1] - a[1]
        if ver > 0:
            output_q += ["down"] * ver
        else:
            output_q += ["up"] * (-ver)
        if hor > 0:
            output_q += ["right"] * hor
        else:
            output_q += ["left"] * (-hor)
        return output_q

    return march(current_point, next_point) + ["a"] if draw else march(current_point, next_point)


def generate_order_file(seq, filename):
    current = (0, 0)
    command_list = []
    for item in seq:
        if isinstance(item, ResetPosition):
            command_list += [item.get_command()]
            current = item.get_position()
        else:
            command_list += goto_next_point(current, item)
            current = item
        pass
    with open(filename, "w+") as f:
        f.write("\n".join(command_list))


def load_images(input_file_name: str) -> np.ndarray:
    im = Image.open(input_file_name)
    if not (im.size[0] == 320 and im.size[1] == 120):
        print("ERROR: Image must be 320px by 120px!")
        sys.exit()
    im = im.convert("1")
    image = np.array(im.getdata()).reshape(120, 320) / 255
    image = 1 - image.astype(int)
    return image


def divide_image(image: np.ndarray):
    # Divide the image into 24 parts to prevent errors in drawing
    image_patch_size = 40
    image_list = []
    for i in range(0, 120, image_patch_size):
        for j in range(0, 320, image_patch_size):
            image_list.append(((i, j), image[i:i + image_patch_size, j:j + image_patch_size],))
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
    visit_list = []
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


def get_entry_exit_point_min_distance(entry_exit_point: list[tuple[np.ndarray, np.ndarray]], greedy: int = 3) -> list[
    int]:
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


def generate_block_visit(image_block: np.ndarray, image_offset: np.ndarray) -> list[np.ndarray]:
    """
    Generate a list of points that dense label is visited
    """
    label, label_count = get_label(image_block)
    if label_count == 0:
        return []
    internal_routes = [generate_dense_visit(label, label_idx, image_offset) for label_idx in
                       range(1, label_count + 1)]
    offset_entry_exit_point = [(t[0], t[-1]) for t in internal_routes]
    arrangement = get_entry_exit_point_min_distance(offset_entry_exit_point, greedy=16)
    visit_list = []
    for i in arrangement:
        visit_list += internal_routes[i]
    return visit_list


def summarize_difficulties(image, output):
    original_difficulty = 2 * np.sum(image) + np.sum(image == 0)
    with open(output, "r") as f:
        current_difficulty = len(f.readlines())
    print("Original difficulty: {}, Current difficulty: {}, reduced: {}".format(
            original_difficulty,
            current_difficulty,
            (original_difficulty - current_difficulty) / original_difficulty * 100
            )
            )
