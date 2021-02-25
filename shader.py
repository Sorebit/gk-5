from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram, ShaderProgram
from pyrr import matrix44 as m44


class Shader:
    def __init__(self, vs: str, fs: str):
        """
        Shader program wrapper. Compiled and prepared for use.

        :param vs: Vertex shader filepath.
        :param fs: Fragment shader filepath.
        """
        self._vs_path = vs
        self._fs_path = fs
        self._shader = self._compile_shader()

        self._model_loc = glGetUniformLocation(self._shader, "model")
        self._projection_loc = glGetUniformLocation(self._shader, "projection")
        self._view_loc = glGetUniformLocation(self._shader, "view")
        self._switcher_loc = glGetUniformLocation(self._shader, "switcher")
        # self._light_color_loc = glGetUniformLocation(self._shader, "light_color")

    def use_program(self) -> None:
        glUseProgram(self._shader)

    def set_model(self, matrix: m44):
        glUniformMatrix4fv(self._model_loc, 1, GL_FALSE, matrix)

    def set_projection(self, matrix: m44):
        glUniformMatrix4fv(self._projection_loc, 1, GL_FALSE, matrix)

    def set_view(self, matrix: m44):
        glUniformMatrix4fv(self._view_loc, 1, GL_FALSE, matrix)

    def set_switcher(self, val: int) -> None:
        glUniform1i(self._switcher_loc, val)

    def _compile_shader(self) -> ShaderProgram:
        """
        Compile shaders from given source files.

        :return: Compiled shader program.
        """
        vert_shader = self._load_shader(self._vs_path)
        frag_shader = self._load_shader(self._fs_path)

        shader = compileProgram(compileShader(vert_shader, GL_VERTEX_SHADER),
                                compileShader(frag_shader, GL_FRAGMENT_SHADER))
        return shader

    @staticmethod
    def _load_shader(shader_file: str) -> bytes:
        shader_source = ""
        with open(shader_file) as f:
            shader_source = f.read()
        return str.encode(shader_source)
