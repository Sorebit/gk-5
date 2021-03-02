from pyrr import matrix44 as m44, Vector3 as v3

from shader import Shader
from loaded_object import LoadedObject


class AbstractLight:
    """Abstract base class."""

    def __init__(self, amb: v3, dif: v3, spe: v3, uni_name: str):
        self._ambient: v3 = amb
        self._diffuse: v3 = dif
        self._specular: v3 = spe
        self._uniform_name: str = uni_name

    def use_light(self, shader: Shader) -> None:
        shader.set_v3(f"{self._uniform_name}.ambient", self._ambient)
        shader.set_v3(f"{self._uniform_name}.diffuse", self._diffuse)
        shader.set_v3(f"{self._uniform_name}.specular", self._specular)


class DirLight(AbstractLight):
    """Directional light."""

    def __init__(self, amb: v3, dif: v3, spe: v3, direction: v3, uni_name: str):
        super().__init__(amb, dif, spe, uni_name)

        self._direction: v3 = direction

    def use_light(self, shader: Shader) -> None:
        super(DirLight, self).use_light(shader)

        shader.set_v3(f"{self._uniform_name}.direction", self._direction)


class PointLight(AbstractLight):
    """Point light with attenuation."""

    def __init__(self, amb: v3, dif: v3, spe: v3, k: v3, pos: v3, uni_name: str,
                 lss: Shader, obj: LoadedObject):
        """Point light with attenuation.

        :param amb: Ambient color.
        :param dif: Diffusion color.
        :param spe: Specular color.
        :param k: Attenuation terms: [constant, linear, quadratic].
        :param pos: Position.
        :param uni_name: Uniform name.
        :param lss: Light source shader
        :param obj: LoadedObject containing a representation of the light source.
        """
        super().__init__(amb, dif, spe, uni_name)

        self._constant: float = k[0]
        self._linear: float = k[1]
        self._quadratic: float = k[2]

        self._light_source_shader: Shader = lss

        self._pos: v3 = pos
        self._scale: float = 0.1
        self._scale_matrix: m44 = m44.create_from_scale(v3([self._scale] * 3))
        pos_matrix = m44.create_from_translation(self._pos)
        self._model: m44 = m44.multiply(self._scale_matrix, pos_matrix)

        self._obj: LoadedObject = obj

    def set_pos(self, pos: v3):
        self._pos = pos
        pos_matrix = m44.create_from_translation(self._pos)
        self._model = m44.multiply(self._scale_matrix, pos_matrix)

    def use_light(self, shader: Shader) -> None:
        super(PointLight, self).use_light(shader)

        shader.set_v3(f"{self._uniform_name}.position", self._pos)
        shader.set_float(f"{self._uniform_name}.constant", self._constant)
        shader.set_float(f"{self._uniform_name}.linear", self._linear)
        shader.set_float(f"{self._uniform_name}.quadratic", self._quadratic)

    def draw(self) -> None:
        self._light_source_shader.set_v3("color", self._diffuse)
        self._obj.draw(self._light_source_shader, model=self._model)


class SpotLight(PointLight):
    """Spotlight."""

    def __init__(self, amb: v3, dif: v3, spe: v3, k: v3, pos: v3, direction: v3,
                 co: float, oco: float, uni_name: str, lss: Shader, obj: LoadedObject):
        """Spotlight.

        :param amb: Ambient color.
        :param dif: Diffusion color.
        :param spe: Specular color.
        :param k: Attenuation terms: [constant, linear, quadratic].
        :param pos: Position.
        :param direction: Direction.
        :param co: Cut off (cosine).
        :param oco: Outer cut off.
        :param uni_name: Uniform name.
        :param lss: Light source shader
        :param obj: LoadedObject containing a representation of the light source.
        """
        super().__init__(amb, dif, spe, k, pos, uni_name, lss, obj)

        self._direction: v3 = direction
        self._cut_off: float = co
        self._outer_cut_off: float = oco

    def use_light(self, shader: Shader) -> None:
        super(SpotLight, self).use_light(shader)

        shader.set_v3(f"{self._uniform_name}.direction", self._direction)
        shader.set_float(f"{self._uniform_name}.cutOff", self._cut_off)
        shader.set_float(f"{self._uniform_name}.outerCutOff", self._outer_cut_off)
