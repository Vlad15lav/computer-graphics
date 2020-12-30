from tqdm import tqdm
from utils.read import readfile

import utils.tools as tool

import numpy as np
import matplotlib.pyplot as plt
import math
import pickle
import os

class Render:
    def __init__(self, obj_path, tga_path, img_size, bgcolor):
        self.vertexes, self.vertexes_t, self.vertexes_vn, self.faces, self.texture, self.tga_shape = readfile(obj_path, tga_path)
        self.img_size = img_size
        self.image = np.zeros((*img_size, 3), dtype=np.uint8)
        self.bgcolor = np.array(bgcolor)
        self.z_buffer = np.full(img_size, np.inf)

        self.cameraPos = np.zeros(3)
        self.cameraVec = np.zeros(3)

        self.lightPos = np.zeros(3)
        self.InverseSL = np.zeros(3)
        self.Ia_light = 0
        self.Id_light = 0
        self.Is_light = 0
        self.Is_alpha = 0

        self.normals = np.zeros((np.size(self.faces[:, 0, 0]), 3))
        self.viewVec = np.zeros((np.size(self.faces[:, 0, 0]), 3))
        self.lightVec = np.zeros((np.size(self.faces[:, 0, 0]), 3))

    def setlight(self, lightPos, Ia, Ka, Id, Kd, Is, Ks, alpha, InverseSL):
        self.lightPos = lightPos
        self.Ia_light = tool.vec2scalar(Ia, Ka)
        self.Id_light = tool.vec2scalar(Id, Kd)
        self.Is_light = tool.vec2scalar(Is, Ks)
        self.Is_alpha = alpha
        self.InverseSL = InverseSL

    def __attenuation(self, d):
        return 1 / (self.InverseSL[0] + self.InverseSL[1] * d + self.InverseSL[2] * d * d)

    def transforms(self, pos, rot, sca, locCam, lookCam, t, b, r, l, f, n, isPerspective, viewwh, viewxy):
        self.cameraPos = locCam
        self.cameraVec = tool.vec2norm(lookCam - locCam)

        self.vertexes = (tool.GetMw2c(locCam, lookCam) @ tool.GetMo2W(pos, rot, sca) @ self.vertexes.T).T
        self.vertexes_vn = (np.linalg.inv(tool.GetMw2c(locCam, lookCam) @ tool.GetMo2W(pos, rot, sca)).T @ self.vertexes_vn.T).T

        for i in range(self.faces.shape[0]):
            x0, y0, z0 = self.vertexes[self.faces[i, 0, 0], 0],  self.vertexes[self.faces[i, 0, 0], 1],  self.vertexes[self.faces[i, 0, 0], 2]
            x1, y1, z1 =  self.vertexes[self.faces[i, 1, 0], 0],  self.vertexes[self.faces[i, 1, 0], 1],  self.vertexes[self.faces[i, 1, 0], 2]
            x2, y2, z2 =  self.vertexes[self.faces[i, 2, 0], 0],  self.vertexes[self.faces[i, 2, 0], 1],  self.vertexes[self.faces[i, 2, 0], 2]
            mean_xyz = np.mean(np.array([[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]]), axis=0)

            self.normals[i] = tool.vec2norm(np.cross([x1 - x0, y1 - y0, z1 - z0], [x2 - x0, y2 - y0, z2 - z0]))
            self.viewVec[i] = tool.vec2norm(locCam - mean_xyz)
            self.lightVec[i] = self.lightPos - mean_xyz

        if isPerspective:
            self.vertexes = tool.xyz2xy(self.vertexes)

        self.vertexes = (tool.GetMproj(t, b, r, l, f, n, isPerspective) @ self.vertexes.T).T
        
        self.vertexes[:, 3] = 1
        self.vertexes = (tool.GetMviewport(viewwh, viewxy) @ self.vertexes.T).T
        self.vertexes = np.int_(np.floor(self.vertexes))


    def __DrawPixel(self, x0, y0, color):
        if 0 <= x0 < self.image.shape[1] and 0 <= y0 < self.image.shape[0]:
            self.image[y0-1:y0+1, x0-1:x0+1] = color

    def __lineBresenham(self, x0, y0, x1, y1, color):
        deltaX, deltaY = x1 - x0, y1 - y0
        move_x, deltaX = int(math.copysign(1, deltaX)), abs(deltaX)
        move_y, deltaY = int(math.copysign(1, deltaY)), abs(deltaY)
        if deltaX > deltaY:
            step_x, step_y, step, length = move_x, 0, deltaY, deltaX  # movement x
        else:
            step_x, step_y, step, length = 0, move_y, deltaX, deltaY  # movement y
        x, y = x0, y0
        error = 0
        for i in range(length):
            error -= step
            if error < 0:
                error += length
                x += move_x
                y += move_y
            else:
                x += step_x
                y += step_y
            self.__DrawPixel(x, y, color)

    def wire(self):
        for i in tqdm(range(self.faces.shape[0])):
            x0, y0, z0 = self.vertexes[self.faces[i, 0, 0], 0], self.vertexes[self.faces[i, 0, 0], 1], self.vertexes[self.faces[i, 0, 0], 2]
            x1, y1, z1 = self.vertexes[self.faces[i, 1, 0], 0], self.vertexes[self.faces[i, 1, 0], 1], self.vertexes[self.faces[i, 1, 0], 2]
            x2, y2, z2 = self.vertexes[self.faces[i, 2, 0], 0], self.vertexes[self.faces[i, 2, 0], 1], self.vertexes[self.faces[i, 2, 0], 2]
            self.__lineBresenham(x0, y0, x1, y1, (0, 210, 210))
            self.__lineBresenham(x1, y1, x2, y2, (0, 210, 210))
            self.__lineBresenham(x2, y2, x0, y0, (0, 210, 210))

    def rasterization(self, isGray, isTexture, isLight, isZbuffer, isBfc):
        for i in tqdm(range(self.faces.shape[0])):
            light = tool.vec2scalar(self.normals[i], self.cameraVec)
            if light < 0 and isBfc:  # Back-face culling
                continue
            x0, y0, z0 = self.vertexes[self.faces[i, 0, 0], 0], self.vertexes[self.faces[i, 0, 0], 1], self.vertexes[self.faces[i, 0, 0], 2]
            x1, y1, z1 = self.vertexes[self.faces[i, 1, 0], 0], self.vertexes[self.faces[i, 1, 0], 1], self.vertexes[self.faces[i, 1, 0], 2]
            x2, y2, z2 = self.vertexes[self.faces[i, 2, 0], 0], self.vertexes[self.faces[i, 2, 0], 1], self.vertexes[self.faces[i, 2, 0], 2]
            vn00, vn01, vn02 = self.vertexes_vn[self.faces[i, 0, 2], 0], self.vertexes_vn[self.faces[i, 0, 2], 1], self.vertexes_vn[self.faces[i, 0, 2], 2]
            vn10, vn11, vn12 = self.vertexes_vn[self.faces[i, 1, 2], 0], self.vertexes_vn[self.faces[i, 1, 2], 1], self.vertexes_vn[self.faces[i, 1, 2], 2]
            vn20, vn21, vn22 = self.vertexes_vn[self.faces[i, 2, 2], 0], self.vertexes_vn[self.faces[i, 2, 2], 1], self.vertexes_vn[self.faces[i, 2, 2], 2]
            vtx0, vty0, vtz0 = self.vertexes_t[self.faces[i, 0, 1], 0], self.vertexes_t[self.faces[i, 0, 1], 1], self.vertexes_t[self.faces[i, 0, 1], 2]
            vtx1, vty1, vtz1 = self.vertexes_t[self.faces[i, 1, 1], 0], self.vertexes_t[self.faces[i, 1, 1], 1], self.vertexes_t[self.faces[i, 1, 1], 2]
            vtx2, vty2, vtz2 = self.vertexes_t[self.faces[i, 2, 1], 0], self.vertexes_t[self.faces[i, 2, 1], 1], self.vertexes_t[self.faces[i, 2, 1], 2]

            # Check correct triagle (square)
            if (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0) == 0:
                continue

            # bounding box
            y_min = min(y0, y1, y2)
            y_max = max(y0, y1, y2)
            x_min = min(x0, x1, x2)
            x_max = max(x0, x1, x2)

            T_inv = np.linalg.inv(np.array(([x0, x1, x2], [y0, y1, y2], [1, 1, 1])))

            for x_i in range(x_min, x_max + 1):
                for y_i in range(y_min, y_max + 1):
                    if not (0 <= x_i < self.image.shape[1] and 0 <= y_i < self.image.shape[0]):
                        continue
                    X = np.array(([x_i, y_i, 1]))
                    V = T_inv @ X
                    if not np.all(V >= 0):  # Inside the triangle
                        continue

                    # Z-buffer
                    z = tool.vec2scalar(V, np.array([z0, z1, z2]))
                    if not isZbuffer or z < self.z_buffer[y_i, x_i]:

                        if isGray:
                            self.__DrawPixel(x_i, y_i, np.abs(light * 255))
                        elif isTexture:
                            t_coord = [tool.vec2scalar(V, np.array([vtx0, vtx1, vtx2])),
                                       tool.vec2scalar(V, np.array([vty0, vty1, vty2]))]
                            if isLight:
                                pix_n = np.array((tool.vec2scalar(V, np.array([vn00, vn10, vn20])),
                                                  tool.vec2scalar(V, np.array([vn01, vn11, vn21])),
                                                  tool.vec2scalar(V, np.array([vn02, vn12, vn22]))))
                                
                                pix_norm = tool.vec2norm(pix_n)
                                lightV = tool.vec2norm(self.lightVec[i])
                                R = 2 * tool.vec2scalar(pix_norm, lightV) * pix_norm - lightV

                                Ia = self.Ia_light
                                Id = self.Id_light * tool.vec2cos(lightV, pix_n)
                                Is = self.Is_light * tool.vec2cos(R, self.viewVec[i]) ** self.Is_alpha
                                I = Ia + self.__attenuation(tool.vec2lenght(self.lightVec[i])) * (Id + Is)
                                
                                color = np.clip(self.texture[np.int_(np.round((1 - t_coord[1]) * (self.tga_shape[0] - 1))), np.int_(np.round(t_coord[0] * (self.tga_shape[1] - 1)))] * I / 255, 0, 255)
                                self.__DrawPixel(x_i, y_i, color)
                            else:
                                color = self.texture[int((1 - t_coord[1]) * (self.tga_shape[0] - 1)), int(t_coord[0] * (self.tga_shape[1] - 1))]
                                self.__DrawPixel(x_i, y_i, color)
                        elif isLight:
                            pix_n = np.array((tool.vec2scalar(V, np.array([vn00, vn10, vn20])),
                                              tool.vec2scalar(V, np.array([vn01, vn11, vn21])),
                                              tool.vec2scalar(V, np.array([vn02, vn12, vn22]))))
                            
                            pix_norm = tool.vec2norm(pix_n)
                            lightV = tool.vec2norm(self.lightVec[i])
                            R = 2 * tool.vec2scalar(pix_norm, lightV) * pix_norm - lightV
                            
                            Ia = self.Ia_light
                            Id = self.Id_light * tool.vec2cos(lightV, pix_n)
                            Is = self.Is_light * tool.vec2cos(R, self.viewVec[i]) ** self.Is_alpha
                            I = Ia + self.__attenuation(tool.vec2lenght(self.lightVec[i])) * (Id + Is)

                            color = np.clip(I, 0, 255)
                            self.__DrawPixel(x_i, y_i, color)

                        self.z_buffer[y_i, x_i] = z

    def clear(self):
        self.image[:] = self.bgcolor
        self.z_buffer[:] = np.full(self.img_size, np.inf)
    
    def save_scene(self, title=''):
        if not os.path.exists('scenes'):
            os.makedirs('scenes')
        f = open(r'scenes/{}.scene'.format(title), 'wb')
        obj = {'Image': self.image, 'Z_buffer': self.z_buffer}
        pickle.dump(obj, f)
        print('The scene is saved to file - {}.scene!'.format(title))
        f.close()
    
    def load_scene(self, title=''):
        try:
            f = open(r'scenes/{}.scene'.format(title), 'rb')
        except (OSError, IOError) as e:
            return
        obj = pickle.load(f)
        self.image = obj['Image']
        self.z_buffer = obj['Z_buffer']
        f.close()

    def show(self, title='', isSave=False):
        plt.figure(title)
        plt.imshow(self.image)
        plt.axis('off')
        if isSave:
            plt.savefig('images/{}.png'.format(title))
        plt.show()

    def getImage(self):
        return np.copy(self.image)
