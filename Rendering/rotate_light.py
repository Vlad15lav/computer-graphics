import argparse
import os
import yaml
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from logic.render import Render
from utils.tools import xyz2xyz1, rotate
from matplotlib.animation import PillowWriter

yaml_keys = ['model', 'camera', 'light']

class Params:
    def __init__(self, project_file):
        self.params = yaml.safe_load(open(project_file).read())
        for param in yaml_keys:
            for key, value in self.params[param].items():
                if type(value) == list:
                    self.params[param][key] = np.array(value)

    def __getattr__(self, item):
        return self.params.get(item, None)


def get_args():
    parser = argparse.ArgumentParser('Computer Graphics: 3D Rendering - Vlad15lav')
    parser.add_argument('-m', '--model', type=str, help='path save file')
    parser.add_argument('-f', '--ffmpeg', type=str, default='source/ffmpeg.exe', help='path ffmpeg file')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[0, 0, 0], help='background color')
    parser.add_argument('--wire', help='wire model', action="store_true")
    parser.add_argument('--gray', help='gray model by back-face culling', action="store_true")
    parser.add_argument('--texture', help='texture enable', action="store_true")
    parser.add_argument('--light', help='light enable', action="store_true")
    parser.add_argument('--frames', type=int, default=50, help='frames count')
    parser.add_argument('--fps', type=int, default=24, help='fps amim')
    parser.add_argument('--interval', type=int, default=30, help='interval amim')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    params = Params(f'config/{opt.model}.yml')

    plt.rcParams['animation.ffmpeg_path'] = opt.ffmpeg
    
    # Create frames
    frames = []
    fig = plt.figure()
    start_pos = xyz2xyz1(params.light['light_pos'].reshape(-1, 3))
    for i in range(opt.frames):
        deg = i * 360 / opt.frames
        params.light['light_pos'] = (rotate(np.array([0, deg, 0])) @ start_pos.T).T
        params.light['light_pos'] = params.light['light_pos'].reshape((-1,))[:-1]

        obj = Render(params.obj_path, params.tga_path, params.img_wh, opt.bgcolor)
        obj.setlight(*params.light.values())
        obj.transforms(*params.model.values(), *params.camera.values())
        
        if opt.wire:
            obj.wire()
            im = plt.imshow(obj.getImage())
        elif opt.gray or opt.texture or opt.light:
            obj.rasterization(isGray=opt.gray, isTexture=opt.texture, isLight=opt.light, isZbuffer=params.z_buffer, isBfc=params.bfc)
            im = plt.imshow(obj.getImage())
    
        frames.append([im])

    print('Frames creation finshed.')

    # gif animation creation
    ani = animation.ArtistAnimation(fig, frames, interval=opt.interval, blit=True, repeat_delay=0)
    writer = PillowWriter(fps=opt.fps)
    ani.save(f"images/{opt.model}.gif", writer=writer)
