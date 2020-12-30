import numpy as np
from PIL import Image
import os
import utils.tools as tool

def readfile(obj_path, tga_path):
        # Parsing obj
        with open(obj_path, 'r') as file:
            obj = [x.split() for x in file.read().splitlines()]
        v, vt, vn, f = [], [], [], [] # Grouping
        for row in obj:
            if row == []:
                continue
            if row[0] == 'v':
                v.append(row[1:])
            elif row[0] == 'vt':
                vt.append(row[1:])
            elif row[0] == 'vn':
                vn.append(row[1:])
            elif row[0] == 'f':
                f.append([row[1].split('/'), row[2].split('/'), row[3].split('/')])
        v = np.array(v, dtype=np.float32)
        vt = np.array(vt, dtype=np.float32)
        vn = np.array(vn, dtype=np.float32)
        fac = np.array(f, dtype=np.int32) - 1
        texture = np.asarray(Image.open(tga_path), dtype="int32")
        return tool.xyz2xyz1(v), vt, tool.xyz2xyz1(vn), fac, texture, texture.shape
