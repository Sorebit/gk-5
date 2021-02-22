import glfw
from OpenGL.GL import *
import numpy as np
from pyrr import matrix44 as m44, Vector3 as v3
import math
import pywavefront
from PIL import Image

from shader_loader import compile_shader


class LoadedObject:
    shader_model_loc = None

    def __init__(self, path: str, x=0.0, y=0.0, z=0.0):
        """Object loaded from .obj and .mtl files, ready to be drawn."""
        self._path = path
        self._wavefront = None
        self.vaos = None
        self._vbos = None
        self.textures = None
        self.lengths = []
        self.pos = m44.create_from_translation(v3([x, y, z]))

        self.model = self.pos
        # Set uniform location for model matrix.
        if LoadedObject.shader_model_loc is None:
            raise Exception("Model loc not set!")
        self._model_loc = LoadedObject.shader_model_loc

        self._load_obj()

    def _load_obj(self) -> None:
        """Loads wavefront obj and materials. Stores vertex data into VAOs and VBOs."""
        self._wavefront = pywavefront.Wavefront(self._path, collect_faces=True, create_materials=True)

        # Generate buffers
        materials_count = len(self._wavefront.materials)
        self.vaos = glGenVertexArrays(materials_count)
        self._vbos = glGenBuffers(materials_count)
        self.textures = glGenTextures(materials_count)

        if materials_count == 1:
            # glGen* will return an int instead of an np.array if argument is 1.
            self.vaos = np.array([self.vaos], dtype=np.uint32)
            self._vbos = np.array([self._vbos], dtype=np.uint32)
            self.textures = np.array([self.textures], dtype=np.uint32)

        # For each material fill buffers and load a texture
        ind = 0
        for key, material in self._wavefront.materials.items():
            print(f'M: {key} : {material.vertex_format}, vs: {material.vertex_size}')
            vertex_size = material.vertex_size
            scene_vertices = np.array(material.vertices, dtype=np.float32)
            # Store length for drawing
            self.lengths.append(len(scene_vertices))
            # Load texture by path (may break in some weird cases, I guess)
            self._load_texture(material.texture.path, self.textures[ind])

            # Bind VAO
            glBindVertexArray(self.vaos[ind])
            # Fill VBO
            glBindBuffer(GL_ARRAY_BUFFER, self._vbos[ind])
            glBufferData(GL_ARRAY_BUFFER, scene_vertices.nbytes, scene_vertices, GL_STATIC_DRAW)

            # Set attribute buffers
            attr_format = {
                "T2F": (1, 2),  # Tex coords (2 floats): ind=1
                "C3F": (2, 3),  # Color (3 floats): ind=2
                "N3F": (3, 3),  # Normal (3 floats): ind=3
                "V3F": (0, 3),  # Position (3 floats): ind=0
            }

            cur_off = 0  # current start offset
            for attr in material.vertex_format.split("_"):
                if attr not in attr_format:
                    raise Exception("Unknown format")

                # Apply
                attr_ind, attr_size = attr_format[attr]
                glEnableVertexAttribArray(attr_ind)
                glVertexAttribPointer(attr_ind, attr_size, GL_FLOAT, GL_FALSE, scene_vertices.itemsize * vertex_size,
                                      ctypes.c_void_p(cur_off))
                cur_off += attr_size * 4

            # Unbind (Technically not necessary but used as a precaution)
            glBindVertexArray(0)
            ind += 1

    def _load_texture(self, path: str, texture: int) -> None:
        """
        Loads texture into buffer by given path and tex buffer ID.

        :param path: Texture path.
        :param texture: Texture buffer ID.
        """
        # For use with GLFW
        glBindTexture(GL_TEXTURE_2D, texture)
        # Set the texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # Set texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Load image
        image = Image.open(path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    def draw(self) -> None:
        """Draws loaded object onto GL buffer."""
        for vao, tex, length in zip(self.vaos, self.textures, self.lengths):
            # glUniform1i(self.switcher_loc, 1)
            glBindVertexArray(vao)
            glBindTexture(GL_TEXTURE_2D, tex)
            glUniformMatrix4fv(self._model_loc, 1, GL_FALSE, self.model)
            glDrawArrays(GL_TRIANGLES, 0, length)


class Window:
    def __init__(self, width: int, height: int, title: str):
        # Initialize window
        if not glfw.init():
            raise Exception("GLFW cannot be initialized!")

        self._width, self._height = width, height
        self._window = glfw.create_window(width, height, title, None, None)

        if not self._window:
            glfw.terminate()
            raise Exception("Window cannot be created!")

        # Set resize handler
        glfw.set_window_size_callback(self._window, self.on_resize)
        # Set window as current context
        glfw.make_context_current(self._window)

        # Compile shaders
        shader = compile_shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")

        # Use shaders
        glUseProgram(shader)
        glClearColor(0.6, 0.7, 0.7, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Get uniform locations
        self.model_loc = glGetUniformLocation(shader, "model")
        self.projection_loc = glGetUniformLocation(shader, "projection")
        self.view_loc = glGetUniformLocation(shader, "view")
        self.switcher_loc = glGetUniformLocation(shader, "switcher")
        # Necessary for objects to be loaded properly
        LoadedObject.shader_model_loc = self.model_loc

        self._fov, self._near, self._far = None, None, None
        self._eye, self._target, self._up = None, None, None
        self.projection_matrix, self.view_matrix = None, None
        self._prepare_matrices()

        self.scene = [
            LoadedObject("data/floor.obj"),
            LoadedObject("data/uv_sphere.obj", x=2, y=1.5, z=-1),
            LoadedObject("data/box/box-T2F_N3F_V3F.obj", x=-1, y=1, z=-2),
            LoadedObject("data/monkey.obj", x=0, y=1, z=1),
        ]

    def _prepare_matrices(self) -> None:
        # Projection matrix
        self._fov = 45
        self._near = 0.1
        self._far = 100
        self.update_projection()

        # View matrix
        self._eye = v3([math.sin(0) * 5, 3, math.cos(0) * 5])
        self._target = v3([0, 0.5, 0])
        self._up = v3([0, 1, 0])
        self.update_view()

    def update_view(self) -> None:
        """Recalculate view matrix and upload it to shader."""
        self.view_matrix = m44.create_look_at(self._eye, self._target, self._up)
        glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view_matrix)

    def update_projection(self) -> None:
        """Recalculate projection matrix and upload it to shader."""
        # Calculate projection matrix
        a = self._width / self._height
        self.projection_matrix = m44.create_perspective_projection(self._fov, a, self._near, self._far)
        # Upload projection matrix to shader
        glUniformMatrix4fv(self.projection_loc, 1, GL_FALSE, self.projection_matrix)

    def on_resize(self, _window, width, height) -> None:
        self._width, self._height = width, height
        glViewport(0, 0, self._width, self._height)
        self.update_projection()

    def main_loop(self) -> None:
        while not glfw.window_should_close(self._window):
            glfw.poll_events()

            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Update view matrix
            cam_x = math.sin(glfw.get_time() * 0.5) * 7
            cam_z = math.cos(glfw.get_time() * 0.5) * 7
            self._eye = v3([cam_x, 3.0, cam_z])
            self.update_view()

            glUniform1i(self.switcher_loc, 0)

            rot_x = m44.create_from_x_rotation(0.5 * glfw.get_time())
            rot_y = m44.create_from_y_rotation(0.8 * glfw.get_time())
            rotation = m44.multiply(rot_x, rot_y)

            self.scene[1].model = m44.multiply(rotation, self.scene[1].pos)

            for o in self.scene:
                o.draw()

            glfw.swap_buffers(self._window)


def main():
    window = Window(1280, 720, "GK Final")
    window.main_loop()


if __name__ == '__main__':
    main()
    glfw.terminate()
