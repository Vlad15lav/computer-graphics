# Computer Graphics
Basic topics from Computer Graphics

1. Geometry description.
2. Displaying the model as polygons. The Algorithm Bresenham.
3. Animation creation, affine transformations.
4. Bezier curves.
5. Bezier clock.
6. Rendering 3D model. OpenGL.

# Requirements
```
pip install -U -r requirements.txt
```

## Obj format notation
Obj file - Utah Teapot model:</br>
1. The list of vertices - "v" market
2. Facets - "f" market

The program finds: number of vertices and faces, max and min values of (x, y, z) and the surface area.</br>
```
python main.py -p source/teapot.obj
```
![](/NotationObj/teapot.png)
## Algorithm Bresenham
Drawing of the teapot using the algorithm Bresenham.</br>
```
python main.py -p source/teapot.obj -s 1024 1024 -b 255 255 255 -c 0 0 255 --scale 145 --save True
```
![](/Bresenham/teapot.png)
## Animation gif
Create rotation animations, zoom, and color changes. Affine transformation.
Download ffmpeg.exe to create gif or mp4 animations. On the developer's website.</br>
```
wget https://github.com/Vlad15lav/Computer-Graphics/releases/download/animation/ffmpeg.exe -O source/ffmpeg.exe

python main.py -f source/ffmpeg.exe -p source/teapot.obj -b 255 255 255 --frames 100 --fps 24 --interval 30
```
![](/Animation/teapot_anim.gif)
## Bezier curves
Create an animation of changing digits (0-9) based on Bezier curves.</br>
```
wget https://github.com/Vlad15lav/Computer-Graphics/releases/download/animation/ffmpeg.exe -O source/ffmpeg.exe

python main.py -f source/ffmpeg.exe -p source/digits.json -t 200 -u 24 -b 0 0 0 -c 0 255 0 --fps 24 --interval 30
```
![](/BezierСurve/digits_anim.gif)
## Bezier clock
Creating the Bezier clock.</br>
```
python main.py -p source/digits.json -b 0 0 0 -c 0 0 255 --bright 10 --zone 3
```
![](/Clock/clock_anim.gif)
## Rendering 3D model. OpenGL
Rendering 3D model, OpenGL annotation.

Reference Coordinates in 3D graphics:
- Local space
- World space
- View space
- Clip space
- Screen space

![](/Rendering/images/spaces.png)

Culling of invisible faces
- Back-face culling
- Z-buffer

Texture overlay
- Texture coordinates (vt)
- Interpolation of barycentric coordinates

Lighting with the Phong reflection model
- Ambient, Diffuse, Specular
- Lighting attenuation

![](/Rendering/images/phong.png)

Rendering
- Wire model
- Model with faces (gray color)
- Model with textures
- Model with lighting
- Model with textures + lighting

**Rendering help:**
```
python main.py --help

usage: Computer Graphics: 3D Rendering - Vlad15lav [-h] [-m MODEL]
                                                   [-s LOAD_SCENE]
                                                   [-b BGCOLOR [BGCOLOR ...]]
                                                   [--wire] [--gray]
                                                   [--texture] [--light]
                                                   [--save] [--save_scene]

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        path yml file
  -s LOAD_SCENE, --load_scene LOAD_SCENE
                        path scene file
  -b BGCOLOR [BGCOLOR ...], --bgcolor BGCOLOR [BGCOLOR ...]
                        background color
  --wire                wire model
  --gray                gray model by back-face culling
  --texture             texture enable
  --light               light enable
  --save                save img
  --save_scene          save scene
```
**Rendering command:**
```
python main.py -m african_head --texture --light --save
```
![](/Rendering/images/heads.png)
### Creating scene:
**Rendering the african head**
```
python main.py -m african_head --texture --light --save_scene
```
**Add the model's eyes**
```
python main.py -m african_eyes --load_scene african_head --texture --light --save --save_scene
```
![](/Rendering/images/african_eyes.png)
### Creating an animation:
**Rotate african head model**
```
python rotate_model.py -m african_head -f source/ffmpeg.exe --texture --light
```
**Rotate the light source**
```
python rotate_light.py -m african_head -f source/ffmpeg.exe --texture --light
```
