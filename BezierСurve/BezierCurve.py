import numpy as np
import matplotlib.pyplot as plt
import os
import math
import json
from tqdm import tqdm
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg.exe'

# Parsing
f = open('digits.json', 'r')
digits = json.load(f)
f.close()

# Functions
def DrawPixel(img, x0, y0, red, green, blue):
    img[y0, x0, 0] = red
    img[y0, x0, 1] = green
    img[y0, x0, 2] = blue

def Bezier(xy_cord, tr):
    xy_value = xy_cord[0, :] * ((1 - tr) ** 3) + 3 * xy_cord[1, :] * tr * ((1 - tr) ** 2)  + 3 * xy_cord[2, :] * (1 - tr) * (tr ** 2) + xy_cord[3, :] * (tr ** 3)
    xy_value = np.array(xy_value, dtype=np.int32)
    return xy_value[0], xy_value[1]

# Calculate curve
t_thresh = 200
digits_curve = []
mean_coords = []
for i, digit in enumerate(digits):
    num = []
    x_list, y_list = [], []
    for segment in digits[digit]:
        seg = []
        xy = np.array(digits[digit][segment], dtype=np.int32)
        for t in np.linspace(0, 1, t_thresh):
            x, y = Bezier(xy, t)
            seg.append([x, y])
            x_list.append(x)
            y_list.append(y)

        num.append(seg)
    digits_curve.append(num)
digits_curve = np.array(digits_curve)

# To center
size = 700
for dig in range(10):
    center_x = (np.max(digits_curve[dig, :, :, 0]) + np.min(digits_curve[dig, :, :, 0])) / 2
    center_y = (np.max(digits_curve[dig, :, :, 1]) + np.min(digits_curve[dig, :, :, 1])) / 2
    for seg in range(4):
        for p in range(t_thresh):
            digits_curve[dig][seg][p][0] += (size / 2 - center_x)
            digits_curve[dig][seg][p][1] += (size / 2 - center_y)

# Create frames
thresh_interim = 24
frames = []
fig = plt.figure()

dm = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
for i in tqdm(range(len(dm) - 1)):
    for u in np.linspace(0, 1, thresh_interim):
        img = np.zeros((size, size, 3), dtype=np.uint8)
        for seg in range(4):
            for p in range(t_thresh):
                x = (1 - u) * digits_curve[dm[i]][seg][p][0] + u * digits_curve[dm[i + 1]][seg][p][0]
                y = (1 - u) * digits_curve[dm[i]][seg][p][1] + u * digits_curve[dm[i + 1]][seg][p][1]
                DrawPixel(img, int(x), int(y), 0, 255, 0)
        im = plt.imshow(img)
        frames.append([im])
print('Frames creation finshed.')

# gif animation creation
print('Create gif...')
ani = animation.ArtistAnimation(fig, frames, interval=30, blit=True, repeat_delay=0)
writer = PillowWriter(fps=24)
ani.save("digits_anim.gif", writer=writer)