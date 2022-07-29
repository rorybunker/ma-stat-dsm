import numpy as np
import math
from hausdorff import hausdorff_distance

def calculate_point_distance(x, y):
    return math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)


def calculate(trajectory_1, trajectory_2):
    max = 0
    for i in range(len(trajectory_1)):
        dist = calculate_point_distance(trajectory_1[i], trajectory_2[i])
        if dist > max:
            max = dist

    return max


def calculate_top_k(k, trajectory_1, trajectory_2):
    max = []
    for i in range(k):
        max.append(0)

    for i in range(len(trajectory_1)):
        dist = calculate_point_distance(trajectory_1[i], trajectory_2[i])
        
        if dist > max[0]:
            max.append(dist)
            max.sort()
            max = max[1:]

    return max, (sum(max) / k)


if __name__ == "__main__":
    a = [[139.9, 15.6], [138.9, 15.7], [137.7, 15.7]]
    b = [[139.8,16], [138.1,16.2], [136.3,16.6]]
    # a = [[137.7, 15.7]]
    # b = [[136.3, 16.6]]

    list_max, dist = calculate_top_k(1, a, b)
    print(list_max)
    print(dist)
