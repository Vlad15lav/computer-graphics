import numpy as np
import matplotlib.pyplot as plt
import os
import math
import json
from tqdm import tqdm
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from utils.tools import Bezier, DrawPixel

def anim(ffmpeg_path, path_obj, t_thresh=200, u_thresh=24, bgcolor=(0, 0, 0), color=(0, 255, 0), fps=24, interval=30):
	plt.rcParams['animation.ffmpeg_path'] = ffmpeg_path

	# read json
	f = open(path_obj, 'r')
	digits = json.load(f)
	f.close()

	# Calculate curve
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
	frames = []
	fig = plt.figure()

	dm = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
	for i in tqdm(range(len(dm) - 1)):
	    for u in np.linspace(0, 1, u_thresh):
	        img = np.zeros((size, size, 3), dtype=np.uint8)
	        img[:] = bgcolor
	        for seg in range(4):
	            for p in range(t_thresh):
	                x = (1 - u) * digits_curve[dm[i]][seg][p][0] + u * digits_curve[dm[i + 1]][seg][p][0]
	                y = (1 - u) * digits_curve[dm[i]][seg][p][1] + u * digits_curve[dm[i + 1]][seg][p][1]
	                DrawPixel(img, int(x), int(y), color)
	        im = plt.imshow(img)
	        frames.append([im])
	print('Frames creation finshed.')

	# gif animation creation
	print('Create gif...')
	ani = animation.ArtistAnimation(fig, frames, interval=interval, blit=True, repeat_delay=0)
	writer = PillowWriter(fps=fps)
	ani.save("anim.gif", writer=writer)