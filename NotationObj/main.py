import argparse
import os
from utils.parserObj import parseFile

def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: NotatinObj - Vlad15lav')
    parser.add_argument('-p', '--path', type=str, default='source/teapot.obj', help='path obj file')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    parseFile(opt.path)