import argparse
import os
from utils.animator import anim

def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: BezierCurve - Vlad15lav')
    parser.add_argument('-f', '--ffmpeg', type=str, default='source/ffmpeg.exe', help='path ffmpeg file')
    parser.add_argument('-p', '--path', type=str, default='source/digits.json', help='path json file')
    parser.add_argument('-t', '--t_thresh', type=int, default=200, help='threshold for Bezier curve')
    parser.add_argument('-u', '--u_thresh', type=int, default=24, help='threshold for transition digits')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[0, 0, 0], help='background color')
    parser.add_argument('-c', '--color', type=int, nargs="+", default=[0, 255, 0], help='digits color')
    parser.add_argument('--fps', type=int, default=24, help='fps anim')
    parser.add_argument('--interval', type=int, default=30, help='interval anim')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    anim(opt.ffmpeg, opt.path, opt.t_thresh, opt.u_thresh, opt.bgcolor, opt.color, opt.fps, opt.interval)