import numpy as np
import pywavefront
from PIL import Image
from pyrr import matrix44 as m44, Vector3 as v3
from OpenGL.GL import *


class LoadedObject:
    shader_model_loc: int = None

    def __init__(self, path: str, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        """Object loaded from .obj and .mtl files, ready to be drawn."""
        self._path = path
        self._wavefront = None
        self.vaos = None
        self._vbos = None
        self.textures = None
        self.use_texture = False
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
            if material.texture is not None:
                self._load_texture(material.texture.path, self.textures[ind])
                self.use_texture = True

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
        # glUniform1i(self.switcher_loc, 0)
        for vao, tex, length in zip(self.vaos, self.textures, self.lengths):
            glBindVertexArray(vao)
            glBindTexture(GL_TEXTURE_2D, tex)
            glUniformMatrix4fv(self._model_loc, 1, GL_FALSE, self.model)
            glDrawArrays(GL_TRIANGLES, 0, length)
