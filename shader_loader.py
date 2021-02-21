from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER
from OpenGL.GL.shaders import compileShader, compileProgram, ShaderProgram


def compile_shader(vs: str, fs: str) -> ShaderProgram:
    """
    Compile shaders from given source files.

    :param vs: Vertex shader filepath.
    :param fs: Fragment shader filepath.
    :return: Compiled shader program.
    """
    vert_shader = _load_shader(vs)
    frag_shader = _load_shader(fs)

    shader = compileProgram(compileShader(vert_shader, GL_VERTEX_SHADER),
                            compileShader(frag_shader, GL_FRAGMENT_SHADER))
    return shader


def _load_shader(shader_file: str) -> bytes:
    shader_source = ""
    with open(shader_file) as f:
        shader_source = f.read()
    return str.encode(shader_source)
