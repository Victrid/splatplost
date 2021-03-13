#!/bin/python

import sys
import os
from PIL import Image
import numpy as np
import tqdm


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


def generate_point_sequence(original_plot):
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
    while current_difficulty != 0:
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
            q = march(init, item)
            for word in q:
                f.write(word+"\n")
                num += 1
            f.write("a\n")
            num += 1
            init = item
    return num


def main(argv):
    im = Image.open(argv[0])
    if not (im.size[0] == 320 and im.size[1] == 120):
        print("ERROR: Image must be 320px by 120px!")
        sys.exit()
    im = im.convert("1")
    image = np.array(im.getdata()).reshape(120, 320)/255
    image = image.astype(int)
    original_num = image.sum()+320*120-1
    optimized_num = generate_order_file(generate_point_sequence(image), argv[1])
    sys.stderr.write(
        f"Complete. Original difficulty: {original_num}, Optimized difficulty:{optimized_num}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
