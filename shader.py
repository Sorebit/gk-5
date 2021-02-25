from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, glUseProgram, glGetUniformLocation
from OpenGL.GL.shaders import compileShader, compileProgram, ShaderProgram


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

    def get_model_loc(self) -> int:
        return self._model_loc

    def get_projection_loc(self) -> int:
        return self._projection_loc

    def get_view_loc(self) -> int:
        return self._view_loc

    def get_switcher_loc(self) -> int:
        return self._switcher_loc

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
