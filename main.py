import glfw
from OpenGL.GL import *

from pyrr import matrix44 as m44, Vector3 as v3
import math

from shader import Shader
from loaded_object import LoadedObject


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
        self.current_shader = Shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")

        # Use shaders
        self.current_shader.use_program()
        glClearColor(0.6, 0.7, 0.7, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Get uniform locations

        # Necessary for objects to be loaded properly
        LoadedObject.shader_model_loc = self.current_shader.get_model_loc()
        LoadedObject.shader_switcher_loc = self.current_shader.get_switcher_loc()

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

        self.light_obj = LoadedObject("data/box/box-N3F_V3F.obj")
        self.light_color = v3([1.0, 1.0, 1.0])

    def _prepare_matrices(self) -> None:
        # Projection matrix
        self._fov = 45
        self._near = 0.1
        self._far = 100
        self.update_projection()

        # View matrix
        self._eye: v3 = v3([math.sin(0) * 5, 3, math.cos(0) * 5])
        self._target: v3 = v3([0, 0.5, 0])
        self._up: v3 = v3([0, 1, 0])
        self.update_view()

    def update_view(self) -> None:
        """Recalculate view matrix and upload it to shader."""
        self.view_matrix = m44.create_look_at(self._eye, self._target, self._up)
        view_loc = self.current_shader.get_view_loc()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.view_matrix)

    def update_projection(self) -> None:
        """Recalculate projection matrix and upload it to shader."""
        # Calculate projection matrix
        a = self._width / self._height
        self.projection_matrix = m44.create_perspective_projection(self._fov, a, self._near, self._far)
        # Upload projection matrix to shader
        projection_loc = self.current_shader.get_projection_loc()
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, self.projection_matrix)

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
            # cam_front = v3([0, 0, -1])
            # self._target = self._eye + cam_front   # Front facing camera

            # self._target = self.scene[1].pos
            self.update_view()

            glUniform1i(self.current_shader.get_switcher_loc(), 0)

            upside_down = m44.create_from_x_rotation(math.pi)
            rot_x = m44.create_from_x_rotation(0.5 * glfw.get_time())
            rot_y = m44.create_from_y_rotation(0.8 * glfw.get_time())
            trans_y = math.sin(glfw.get_time())
            translation = m44.create_from_translation(v3([0, trans_y, 0]))
            rotation = m44.multiply(rot_x, rot_y)

            model_1 = m44.multiply(upside_down, self.scene[1].pos)
            model_1 = m44.multiply(translation, model_1)
            self._target = v3.from_matrix44_translation(model_1)  # targeted moving camera
            self.update_view()
            model_1 = m44.multiply(rot_y, model_1)

            self.scene[1].model = model_1
            self.scene[3].model = m44.multiply(rotation, self.scene[3].pos)

            for o in self.scene:
                o.draw()

            glfw.swap_buffers(self._window)


def main():
    window = Window(1280, 720, "GK Final")
    window.main_loop()


if __name__ == '__main__':
    main()
    glfw.terminate()
