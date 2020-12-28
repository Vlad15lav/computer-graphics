import numpy as np

def vec2cos(a, b):
    return np.sum(a * b) / (np.linalg.norm(a) * np.linalg.norm(b))

def vec2lenght(a):
    return np.linalg.norm(a)

def vec2norm(vec):
    vec_norm = np.linalg.norm(vec)
    if vec_norm == 0:
        vec_norm = 1
    return vec / vec_norm

def vec2scalar(a, b):
    return np.sum(a * b)

def xyz2xyz1(xyz):
    return np.hstack((xyz, np.ones((xyz.shape[0], 1))))

def xyz2xy(xyz):
    xyz[:, :2] /= xyz[:, 2].reshape(xyz.shape[0], -1)
    return xyz

# Affine transformation
def shift(c):
    return np.array(([1, 0, 0, c[0]],
                     [0, 1, 0, c[1]],
                     [0, 0, 1, c[2]],
                     [0, 0, 0, 1]))

def scale(k):
    return np.array(([k[0], 0, 0, 0],
                     [0, k[1], 0, 0],
                     [0, 0, k[2], 0],
                     [0, 0, 0, 1]))

def rotateX(alpha_rad):
    return np.array(([1, 0, 0, 0],
                     [0, np.cos(alpha_rad), -np.sin(alpha_rad), 0],
                     [0, np.sin(alpha_rad), np.cos(alpha_rad), 0],
                     [0, 0, 0, 1]))

def rotateY(alpha_rad):
    return np.array(([np.cos(alpha_rad), 0, np.sin(alpha_rad), 0],
                     [0, 1, 0, 0],
                     [-np.sin(alpha_rad), 0, np.cos(alpha_rad), 0],
                     [0, 0, 0, 1]))

def rotateZ(alpha_rad):
    return np.array(([np.cos(alpha_rad), -np.sin(alpha_rad), 0, 0],
                     [np.sin(alpha_rad), np.cos(alpha_rad), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]))

def rotate(alpha_deg):
    alpha_rad = np.radians(alpha_deg)
    return rotateX(alpha_rad[0]) @ rotateY(alpha_rad[1]) @ rotateZ(alpha_rad[2])

# Model local coord to world
def GetMo2W(location, alpha_deg, scl):
    T = shift(location)
    R = rotate(alpha_deg)
    S = scale(scl)
    return T @ R @ S

# World to camera
def rotateC(loc, look):
    gamma = vec2norm((loc - look))
    beta = vec2norm(np.cross([0, 1, 0], gamma))
    alpha = vec2norm(np.cross(gamma, beta))
    Rc = np.eye(4)
    Rc[0, :3], Rc[1, :3], Rc[2, :3] = beta, alpha, gamma
    return Rc

def GetMw2c(loc, look):
    Tc = shift(-loc)
    Rc = rotateC(loc, look)
    return Rc @ Tc

# To projection
def perspective(t, b, r, l, f, n):
    return np.array(([2 * n / (r - l), 0, (r + l) / (r - l), 0],
                     [0, 2 * n / (t - b), (t + b) / (t - b), 0],
                     [0, 0, -(f + n) / (f - n), - (2 * f * n / (f - n))],
                     [0, 0, -1, 0]))

def orthographic(t, b, r, l, f, n):
    return np.array(([2 / (r - l), 0, 0, -(r + l) / (r - l)],
                     [0, 2 / (t - b), 0, -(t + b) / (t - b)],
                     [0, 0, -2 / (f - n), -(f + n) / (f - n)],
                     [0, 0, 0, 1]))

def GetMproj(top, bot, right, left, far, near, isPerspective):
    if isPerspective:
        return perspective(top, bot, right, left, far, near)
    else:
        return orthographic(top, bot, right, left, far, near)

# To viewport
def GetMviewport(wh, xy):
    Tw = shift([xy[0] + (wh[0] - 1) / 2, xy[1] + (wh[1] - 1) / 2, 0])
    Sw = scale([(wh[0] - 1) / 2, (wh[1] - 1) / 2, 1])
    return Tw @ Sw