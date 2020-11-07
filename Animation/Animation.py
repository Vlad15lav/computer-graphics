import numpy as np
import matplotlib.pyplot as plt
import os
import math
from tqdm import tqdm
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg.exe'

# Parsing
file_data = 'teapot.obj'
with open(file_data, 'r') as file:
    s = [x.split() for x in file.read().splitlines()]

# Grouping X and Y, Vertexes
x, y = [], []
f1, f2, f3 = [], [], []
for coord in s:
    if coord == []:
        continue
    if coord[0] == 'f':
        f1.append(coord[1])
        f2.append(coord[2])
        f3.append(coord[3])
        continue
    x.append(coord[1])
    y.append(coord[2])

x = np.array(x)
y = np.array(y)
xy = np.zeros((len(x), 2))
xy[:, 0] = x
xy[:, 1] = y

triangle = np.zeros((len(f1), 3), dtype=np.int32)
triangle[:, 0] = f1
triangle[:, 1] = f2
triangle[:, 2] = f3
triangle -= 1

# MirrorHor
xy[:, 1] *= -1

# Scale
xy = np.array(xy * 65, dtype=np.int32)

# ToCenter
xy += 512 - np.mean(xy, axis=0, dtype=np.int32)

# Functions
def DrawPixel(img, x0, y0, red, green, blue):
    img[y0, x0, 0] = red
    img[y0, x0, 1] = green
    img[y0, x0, 2] = blue

def LineBresenham(img, x0, y0, x1, y1, r, g, b):
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

        DrawPixel(img, x, y, r, g, b)

# Create Animation
# Transforms
def shiftMatr(vec):
    mtr = np.array([[1, 0, vec[0]],
                    [0, 1, vec[1]],
                    [0, 0, 1]])
    return mtr

def rotMatr(ang):
    mtr = np.array([[np.cos(ang), -np.sin(ang), 0],
                    [np.sin(ang), np.cos(ang), 0],
                    [0, 0, 1]])
    return mtr

def scaMatr(k):
    mtr = np.array([[k, 0, 0],
                    [0, k, 0],
                    [0, 0, 1]])
    return mtr

def to_cart_coords(x): # (x1, x2, x3) -> (x1/x3, x2/x3)
    x = x[:-1]/x[-1]
    return x

# Create Animation
# To coords (x1, x2) -> (x1, x2, 1)
X = np.ones((3, len(xy)))
X[0, :] = xy[:, 0]
X[1, :] = xy[:, 1]

N = 100 # frames count

# Color Animation
up_color = np.array(np.linspace(0, 255, int(N / 2)), dtype=np.int32)
down_color = np.flip(np.array(np.linspace(0, 255, int(N / 2)), dtype=np.int32))

red_line = np.zeros(N)
red_line[:int(N/2)] = down_color
red_line[int(N/2):] = up_color
green_line = np.zeros(N)
green_line[:int(N/2)] = up_color
green_line[int(N/2):] = down_color

# Scale Animation
scale_anim = np.ones(N)
scale_anim[:int(N / 4)] = np.linspace(1, 2, int(N / 4))
scale_anim[int(N / 4):int(N / 2)] = np.flip(np.linspace(1, 2, int(N / 4)))
scale_anim[int(N / 2):int((3 * N) / 4)] = np.flip(np.linspace(0.5, 1, int(N / 4)))
scale_anim[int((3 * N) / 4):] = np.linspace(0.5, 1, int(N / 4))

# Shift
fig_center = np.flip(np.mean(xy, axis=0, dtype=np.int32))
T = shiftMatr(-fig_center)
inv_T = np.linalg.inv(T)

# Create frames
frames = []
fig = plt.figure()
for i in tqdm(range(N)):
    deg = i * 2 * np.pi / (N / 2)
    R = rotMatr(deg)
    S = scaMatr(scale_anim[i])
    X_new = inv_T @ S @ R @ T @ X
    X_new = to_cart_coords(X_new)
    xy = np.array(X_new.T, dtype=np.int32)

    # draw update
    img = np.zeros((1024, 1024, 3), dtype=np.uint8)
    img[:, :, 0] = 255
    img[:, :, 1] = 255
    img[:, :, 2] = 255

    for vec in triangle:
        LineBresenham(img, xy[vec[0]][0], xy[vec[0]][1], xy[vec[1]][0], xy[vec[1]][1], red_line[i], green_line[i], 0)
        LineBresenham(img, xy[vec[1]][0], xy[vec[1]][1], xy[vec[2]][0], xy[vec[2]][1], red_line[i], green_line[i], 0)
        LineBresenham(img, xy[vec[0]][0], xy[vec[0]][1], xy[vec[2]][0], xy[vec[2]][1], red_line[i], green_line[i], 0)

    im = plt.imshow(img)
    frames.append([im])

print('Frames creation finshed.')

# gif animation creation
ani = animation.ArtistAnimation(fig, frames, interval=30, blit=True, repeat_delay=0)
writer = PillowWriter(fps=24)
ani.save("teapot_anim.gif", writer=writer)
