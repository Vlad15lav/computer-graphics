import argparse
import os
from utils.animator import anim

def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: Animation - Vlad15lav')
    parser.add_argument('-f', '--ffmpeg', type=str, default='ffmpeg.exe', help='path ffmpeg file')
    parser.add_argument('-p', '--path', type=str, default='source/teapot.obj', help='path obj file')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[255, 255, 255], help='background color')
    parser.add_argument('--frames', type=int, default=100, help='frames count')
    parser.add_argument('--fps', type=int, default=24, help='fps amim')
    parser.add_argument('--interval', type=int, default=30, help='interval amim')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    anim(opt.ffmpeg, opt.path, opt.bgcolor, opt.frames, opt.fps, opt.interval)
