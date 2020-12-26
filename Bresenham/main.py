import argparse
import os
from utils.draw import drawObj

def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: Bresenham - Vlad15lav')
    parser.add_argument('-p', '--path', type=str, default='source/teapot.obj', help='path obj file')
    parser.add_argument('-s', '--size', type=int, nargs="+", default=[1024, 1024], help='img size')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[255, 255, 255], help='background color')
    parser.add_argument('-c', '--color', type=int, nargs="+", default=[0, 0, 255], help='color obj')
    parser.add_argument('--scale', type=int, default=145, help='scale obj')
    parser.add_argument('--save', type=bool, default=True, help='save img')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    drawObj(opt.path, opt.size, opt.bgcolor, opt.color, opt.scale, opt.save)