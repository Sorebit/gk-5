# 3D graphics course final project

This is a small 3D rendering engine written in OpenGL as a final project for a university course.

It features some basic functionality such as textures, shaders, basic models and materials support.


![preview](preview.png)

## Features

- Shaders ([shader.py](./shader.py) for wrapper, [shaders/](./shaders) for GLSL sources)
  - Gouraud shading with fog
  - Phong shading
- Light sources ([light.py](./light.py))
  - Directional
  - Point with attenuation
  - Spotlight
  - Material support
- Loading `*.obj` models and `*.mtl` materials ([loaded_object.py](./loaded_object.py))
- Multiple camera types (see Keyboard shortcuts)

## Installation

- Python 3.8
- `pip install -r requirements.txt`

## Usage

- `python main.py`

## Used libraries:

- `glfw` - Window creation
- `pyopengl` - OpenGL bindings
- `pyrr` + `numpy` - Vector and matrix operations
- `pillow` - Image loading
- `pywavefront` - Handling of `*.obj` and `*.mtl` files

## Keyboard shortcuts

### Camera

- `1` - Static camera
- `2` - Follow the monkey
- `3` - *Be* the monkey
  
### Shading options

- `O` - Gouraud shading
- `P` - Phong shading
- `F` - Toggle fog
- `<- / ->` - Change spotlight direction
