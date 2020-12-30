import argparse
import os
import yaml
import numpy as np
from logic.render import Render

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
    parser.add_argument('-s', '--load_scene', type=str, help='path scene file')
    parser.add_argument('-b', '--bgcolor', type=int, nargs="+", default=[0, 0, 0], help='background color')
    parser.add_argument('--wire', help='wire model', action="store_true")
    parser.add_argument('--gray', help='gray model by back-face culling', action="store_true")
    parser.add_argument('--texture', help='texture enable', action="store_true")
    parser.add_argument('--light', help='light enable', action="store_true")
    parser.add_argument('--save', help='save img', action="store_true")
    parser.add_argument('--save_scene', help='save scene', action="store_true")

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    params = Params(f'config/{opt.model}.yml')
    obj = Render(params.obj_path, params.tga_path, params.img_wh, opt.bgcolor)
    obj.setlight(*params.light.values())
    obj.transforms(*params.model.values(), *params.camera.values())

    if not opt.load_scene is None:
        obj.load_scene(opt.load_scene)
    
    if opt.wire:
        obj.wire()
        obj.show(opt.model, opt.save)
        obj.clear()

    if opt.gray or opt.texture or opt.light:
        obj.rasterization(isGray=opt.gray, isTexture=opt.texture, isLight=opt.light, isZbuffer=params.z_buffer, isBfc=params.bfc)
        obj.show(opt.model, opt.save)
    
    if opt.save_scene:
        obj.save_scene(opt.model)
