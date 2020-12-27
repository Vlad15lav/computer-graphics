import numpy as np

def DrawPixel(img, x0, y0, color):
    img[y0, x0] = color

def Bezier(xy_cord, tr):
    xy_value = xy_cord[0, :] * ((1 - tr) ** 3) + 3 * xy_cord[1, :] * tr * ((1 - tr) ** 2)  + 3 * xy_cord[2, :] * (1 - tr) * (tr ** 2) + xy_cord[3, :] * (tr ** 3)
    xy_value = np.array(xy_value, dtype=np.int32)
    return xy_value[0], xy_value[1]