import numpy as np
import matplotlib.pyplot as plt
import os
import math


def parseFile(path):
	# Parsing
	with open(path, 'r') as file:
	    s = [x.split() for x in file.read().splitlines()]

	# Count v and f
	num_v = 0
	num_f = 0
	for coord in s:
	    if coord == []:
	        continue
	    if coord[0] == 'v':
	        num_v += 1
	    elif coord[0] =='f':
	        num_f += 1
	print('Count v - ' + str(num_v) + '\n' + 'Count f - ' + str(num_f))

	# Max and min value
	x, y, z = [], [], []
	for coord in s:
	    if coord == []:
	        continue
	    if coord[0] == 'f':
	        continue
	    x.append(coord[1])
	    y.append(coord[2])
	    z.append(coord[3])
	x = np.array(x)
	y = np.array(y)
	z = np.array(z)
	cord_matrix = np.zeros((num_v, 3))
	cord_matrix[:, 0] = x
	cord_matrix[:, 1] = y
	cord_matrix[:, 2] = z
	print('Minimum coordinate values - ' + str(np.min(cord_matrix, axis=0)))
	print('Maximum coordinate values - ' + str(np.max(cord_matrix, axis=0)))

	# Calculating the area
	def AreaTriangle(coords, v1, v2, v3):
	    # Pythagorean theorem
	    a = np.sqrt((coords[v1][0] - coords[v2][0]) ** 2 + (coords[v1][1] - coords[v2][1]) ** 2 + (
	                coords[v1][2] - coords[v2][2]) ** 2)
	    b = np.sqrt((coords[v2][0] - coords[v3][0]) ** 2 + (coords[v2][1] - coords[v3][1]) ** 2 + (
	                coords[v2][2] - coords[v3][2]) ** 2)
	    c = np.sqrt((coords[v3][0] - coords[v1][0]) ** 2 + (coords[v3][1] - coords[v1][1]) ** 2 + (
	                coords[v3][2] - coords[v1][2]) ** 2)
	    # Heron's Formula
	    p = (a + b + c) / 2
	    return np.sqrt(p * (p - a) * (p - b) * (p - c))
	squer_model = 0
	for f in s:
	    if f == []:
	        continue
	    if f[0] == 'v':
	        continue
	    squer_model += AreaTriangle(cord_matrix, int(f[1]) - 1, int(f[2]) - 1, int(f[3]) - 1)
	print("Teapot area = " + str(squer_model))