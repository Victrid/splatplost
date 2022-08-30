#!env python

import argparse
import sys
from typing import Union

import numpy as np
import tqdm
from PIL import Image
from skimage import measure

from tsp_solver import solve_tsp_dynamic_programming


class ResetPosition:
    def __init__(self, left: bool, up: bool):
        self.left = left
        self.up = up

    def get_command(self):
        if self.left:
            if self.up:
                return "lu"
            else:
                return "ld"
        else:
            if self.up:
                return "ru"
            else:
                return "rd"

    def get_position(self):
        if self.left:
            if self.up:
                return 0, 0
            else:
                return 119, 0
        else:
            if self.up:
                return 0, 319
            else:
                return 119, 319


def is_coordinate_valid(x, y):
    return 0 <= x < 120 and 0 <= y < 320


def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]


def get_reset(point):
    ad = []
    ad.append(point_distance(point, (119, 319)))
    ad.append(point_distance(point, (119, 0)))
    ad.append(point_distance(point, (0, 319)))
    ad.append(point_distance(point, (0, 0)))
    t = argmin(ad)
    return ResetPosition(t % 2, t // 2)


def point_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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


def get_entry_exit_point_min_distance(entry_exit_point: list[tuple[np.ndarray, np.ndarray]]) -> list[int]:
    distance_matrix = np.zeros((len(entry_exit_point), len(entry_exit_point)))
    for i in range(len(entry_exit_point)):
        for j in range(len(entry_exit_point)):
            if i == j or j == 0:
                continue
            distance_matrix[i][j] = point_distance(entry_exit_point[i][1], entry_exit_point[j][0])
    permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
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
    arrangement = get_entry_exit_point_min_distance(offset_entry_exit_point)
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


def main(input, output):
    image = load_images(input)
    divided_image = divide_image(image)
    visit_list: list[Union[ResetPosition, np.ndarray]] = []
    for item in tqdm.tqdm(divided_image, desc="Blocks to be visited"):
        visit_list += generate_block_visit(item[1], np.array(item[0]))
        if len(visit_list) == 0 or isinstance(visit_list[-1], ResetPosition):
            continue
        visit_list.append(get_reset(visit_list[-1]))
    generate_order_file(visit_list, output)
    summarize_difficulties(image, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Generate instructions for plotting.'
            )
    parser.add_argument("-o", "--output", required=True,
                        dest="output", help="Specify output instruct filename."
                        )
    parser.add_argument("-i", "--input", required=True,
                        dest="input", help="Specify input picture."
                        )
    args = parser.parse_args()
    main(args.input, args.output)
