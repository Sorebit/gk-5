from pyrr import matrix44 as m44, Vector3 as v3

from shader import Shader
from loaded_object import LoadedObject


class Light:
    def __init__(self, amb: v3, dif: v3, spe: v3, pos: v3, lss: Shader, obj: LoadedObject):
        """

        :param amb: Ambient color.
        :param dif: Diffusion color.
        :param spe: Specular color.
        :param pos: Position.
        :param lss: Light source shader
        :param obj: LoadedObject containing a representation of the light source.
        """
        self.ambient: v3 = amb
        self.diffuse: v3 = dif
        self.specular: v3 = spe
        self._pos: v3 = pos
        self._model: m44 = m44.create_from_translation(self._pos)
        self._light_source_shader: Shader = lss
        self._scale = 0.2
        self._scale_matrix = m44.create_from_scale(v3([self._scale] * 3))
        self._obj = obj

    def set_pos(self, pos: v3):
        self._pos = pos
        pos_matrix = m44.create_from_translation(self._pos)
        self._model = m44.multiply(self._scale_matrix, pos_matrix)

    def draw(self) -> None:
        self._light_source_shader.set_v3("color", self.diffuse)
        self._obj.draw(self._light_source_shader, model=self._model)

    def use_light(self, shader: Shader) -> None:
        shader.set_v3("light.ambient", self.ambient)
        shader.set_v3("light.diffuse", self.diffuse)
        shader.set_v3("light.specular", self.specular)
        shader.set_v3("lightPos", self._pos)
