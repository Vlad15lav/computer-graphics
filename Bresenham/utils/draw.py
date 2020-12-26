import numpy as np
import matplotlib.pyplot as plt
import os
import math


def drawObj(path, img_size=(1024, 1024), bgcolor=(255, 255, 255), color=(0, 0, 255), scale=145, save=False):
    with open(path, 'r') as file:
        s = [x.split() for x in file.read().splitlines()]

    # Grouping X and Y, Vertexes
    x, y = [], []
    a, b, c = [], [], []
    for coord in s:
        if coord == []:
            continue
        if coord[0] == 'f':
            a.append(coord[1])
            b.append(coord[2])
            c.append(coord[3])
            continue
        x.append(coord[1])
        y.append(coord[2])

    x = np.array(x)
    y = np.array(y)
    xy = np.zeros((len(x), 2))
    xy[:, 0] = x
    xy[:, 1] = y

    triangle = np.zeros((len(a), 3), dtype=np.int32)
    triangle[:, 0] = a
    triangle[:, 1] = b
    triangle[:, 2] = c
    triangle -= 1

    # Image
    img = np.zeros((*img_size, 3), dtype=np.uint8)
    img[:] = bgcolor

    # Point center
    idx_center = 0
    for i in range(len(x)):
        if xy[i][0] == 0 and xy[i][1] == 0:
            idx_center = i

    # MirrorHor
    xy[:, 1] *= -1

    # Scale
    xy[:, 0] *= scale
    xy[:, 1] *= scale

    # ToCorner
    xy[:, 0] += np.abs(np.min(xy[:, 0]))
    xy[:, 1] += np.abs(np.min(xy[:, 1]))

    # ToCenter
    xy[:, 0] += img_size[0] / 2 - xy[idx_center, 0]
    xy[:, 1] += img_size[1] / 2 - xy[idx_center, 1]

    xy = np.array(xy, dtype=np.int32)

    # Functions
    def DrawPixel(x0, y0, color):
        try:
            img[y0, x0] = color
        except:
            pass

    def LineBresenham(x0, y0, x1, y1):
        deltaX = x1 - x0
        deltaY = y1 - y0

        move_x = int(math.copysign(1, deltaX))
        deltaX = abs(deltaX)

        move_y = int(math.copysign(1, deltaY))
        deltaY = abs(deltaY)

        if deltaX > deltaY:
            step_x, step_y, step, length = move_x, 0, deltaY, deltaX # movement x
        else:
            step_x, step_y, step, length = 0, move_y, deltaX, deltaY # movement y

        x, y = x0, y0
        error = 0

        for i in range(length):
            error -= step
            if error < 0:
                error += length
                x += move_x
                y += move_y
            else:
                x += step_x
                y += step_y

            DrawPixel(x, y, color)

    # Draw vertexes
    for vec in triangle:
        LineBresenham(xy[vec[0]][0], xy[vec[0]][1], xy[vec[1]][0], xy[vec[1]][1])
        LineBresenham(xy[vec[1]][0], xy[vec[1]][1], xy[vec[2]][0], xy[vec[2]][1])
        LineBresenham(xy[vec[0]][0], xy[vec[0]][1], xy[vec[2]][0], xy[vec[2]][1])

    # Show Image
    plt.figure()
    plt.imshow(img)
    if save:
        plt.savefig(path.split('/')[-1].split('.')[0])
    plt.show()