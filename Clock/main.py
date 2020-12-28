import argparse
import os
from utils.clock import Clock

def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: Clock - Vlad15lav')
    parser.add_argument('-p', '--path', type=str, default='source/digits.json', help='path json file')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[0, 0, 0], help='background color')
    parser.add_argument('-c', '--color', type=int, nargs="+", default=[0, 0, 255], help='digits color')
    parser.add_argument('--bright', type=int, default=10, help='brightness digits 0-25')
    parser.add_argument('--zone', type=int, default=0, help='select timezone (hour)')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    clock = Clock(opt.path)
    clock.setcolor(opt.color)
    clock.setbgcolor(opt.bgcolor)
    clock.setbrightness(opt.bright)
    clock.show(zone=opt.zone)
