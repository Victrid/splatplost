#!/bin/python

import sys
import os
from PIL import Image
import numpy as np
import tqdm
import argparse


class reset_pos:
    def __init__(self, left: bool, up: bool):
        self.left = left
        self.up = up

    def getposcommand(self):
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

    def getpostuple(self):
        if self.left:
            if self.up:
                return (0, 0)
            else:
                return (119, 0)
        else:
            if self.up:
                return (0, 319)
            else:
                return (119, 319)


def plot_difficulty(a, b):
    return (a != b).sum()


def is_coordinate_valid(x, y):
    return x >= 0 and x < 120 and y >= 0 and y < 320


def find_neighbours(x, y, original_point, visited, distance_threshold):
    neighbours = []
    if is_coordinate_valid(x+1, y) and (x+1, y) not in visited and point_distance(original_point, (x+1, y)) < distance_threshold:
        neighbours.append((x+1, y))
    if is_coordinate_valid(x, y-1) and (x, y-1) not in visited and point_distance(original_point, (x, y-1)) < distance_threshold:
        neighbours.append((x, y-1))
    if is_coordinate_valid(x-1, y) and (x-1, y) not in visited and point_distance(original_point, (x-1, y)) < distance_threshold:
        neighbours.append((x-1, y))
    if is_coordinate_valid(x, y+1) and (x, y+1) not in visited and point_distance(original_point, (x, y+1)) < distance_threshold:
        neighbours.append((x, y+1))
    return neighbours


def argmin(iterable):
    return min(enumerate(iterable), key=lambda x: x[1])[0]


def get_reset(point):
    ad = []
    ad.append(point_distance(point, (119, 319)))
    ad.append(point_distance(point, (119, 0)))
    ad.append(point_distance(point, (0, 319)))
    ad.append(point_distance(point, (0, 0)))
    t = argmin(ad)
    return reset_pos(t % 2, t//2)


def point_distance(a, b):
    return abs(a[0]-b[0])+abs(a[1]-b[1])


def find_next_point(x, y, original_plot, current_plot):
    search_queue = [(x, y)]
    visited = [(x, y)]
    distance_threshold = 500
    search_queue += find_neighbours(x, y, (x, y), visited, distance_threshold)
    visited += find_neighbours(x, y, (x, y), visited, distance_threshold)
    step_bar = tqdm.tqdm(total=320*120, position=1, leave=False)
    candidates = []
    while len(search_queue) > 0:
        point = search_queue[0]
        search_queue.pop(0)
        if original_plot[point[0]][point[1]] == current_plot[point[0]][point[1]]:
            search_queue += find_neighbours(point[0],
                                            point[1], (x, y), visited, distance_threshold)
            visited += find_neighbours(point[0], point[1],
                                       (x, y), visited, distance_threshold)
            step_bar.update(len(visited)-step_bar.n)
        else:
            candidates.append(point)
            if distance_threshold > point_distance(point, (x, y)):
                distance_threshold = point_distance(point, (x, y))
    step_bar.update(step_bar.total-step_bar.n)
    distance_threshold = 500
    final = (-1, -1)
    for t in candidates:
        if point_distance(t, (x, y)) < distance_threshold:
            final = t
    step_bar.close()
    return final


def generate_point_sequence(original_plot, step):

    generated_plot = np.zeros_like(original_plot)
    generated_plot.fill(1)
    generated_plot = generated_plot.astype(int)
    plot_sequence = []
    current_point = (0, 0)
    initial_difficulty = plot_difficulty(generated_plot, original_plot)
    current_difficulty = initial_difficulty
    if(initial_difficulty == 0):
        return plot_sequence
    total_bar = tqdm.tqdm(total=initial_difficulty, position=0)
    step_counter = 0
    while current_difficulty != 0:
        step_counter += 1
        if step_counter % step == 0:
            plot_sequence.append(get_reset(current_point))
            plot_sequence.append(current_point)
            continue
        total_bar.update(1)
        next_point = find_next_point(
            current_point[0], current_point[1], original_plot, generated_plot)
        if next_point[0] == -1:
            raise Exception()
        plot_sequence.append(next_point)
        current_point = next_point
        generated_plot[next_point[0]][next_point[1]
                                      ] = original_plot[next_point[0]][next_point[1]]

        current_difficulty = plot_difficulty(generated_plot, original_plot)
    total_bar.close()
    return plot_sequence


def generate_order_file(seq, filename):
    def march(a, b):
        output_q = []
        ver = b[0]-a[0]
        hor = b[1]-a[1]
        if ver > 0:
            output_q += ["down"]*ver
        else:
            output_q += ["up"]*(-ver)
        if hor > 0:
            output_q += ["right"]*hor
        else:
            output_q += ["left"]*(-hor)
        return output_q
    num = 0
    init = (0, 0)
    with open(filename, "w+") as f:
        for item in seq:
            if type(item) is reset_pos:
                f.write(item.getposcommand()+"\n")
                init = item.getpostuple()
                continue
            q = march(init, item)
            for word in q:
                f.write(word+"\n")
                num += 1
            f.write("a\n")
            num += 1
            init = item
    return num


def main(input, output, steps):
    im = Image.open(input)
    if not (im.size[0] == 320 and im.size[1] == 120):
        print("ERROR: Image must be 320px by 120px!")
        sys.exit()
    im = im.convert("1")
    image = np.array(im.getdata()).reshape(120, 320)/255
    image = image.astype(int)
    original_num = image.sum()+320*120-1
    optimized_num = generate_order_file(
        generate_point_sequence(image, steps), output)
    sys.stderr.write(
        f"Complete. Original difficulty: {original_num}, Optimized difficulty:{optimized_num}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Generate instructions for plotting.')
    parser.add_argument("-o", "--output", required=True,
                        dest="output", help="Specify output instruct filename.")
    parser.add_argument("-i", "--input", required=True,
                        dest="input", help="Specify input picture.")
    parser.add_argument("-s", "--step", dest="step", type=int, default=100000,
                        help="Specify how many steps before resetting the pointer. This is useful if you do not "
                        "have a stable bluetooth device.")
    args = parser.parse_args()
    main(args.input, args.output, args.step)
