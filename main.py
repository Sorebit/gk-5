import glfw
from OpenGL.GL import *
from pyrr import matrix44 as m44, Vector3 as v3
import math

from shader import Shader
from loaded_object import LoadedObject


class Light:
    def __init__(self, amb: v3, dif: v3, spe: v3, pos: v3):
        self.ambient: v3 = amb
        self.diffusion: v3 = dif
        self.specular: v3 = spe
        self._pos: v3 = pos
        self._model: m44 = m44.create_from_translation(self._pos)

    def set_pos(self, pos: v3):
        self._pos = pos
        self._model = m44.create_from_translation(self._pos)

    def use_light(self, shader: Shader) -> None:
        shader.set_v3("light.ambient", self.ambient)
        shader.set_v3("light.diffuse", self.diffusion)
        shader.set_v3("light.specular", self.specular)
        shader.set_v3("lightPos", self._pos)

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

        # Set options
        glClearColor(0.6, 0.7, 0.7, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Matrices
        self._fov, self._near, self._far = None, None, None
        self._eye, self._target, self._up = None, None, None
        self.projection_matrix, self.view_matrix = None, None
        self._prepare_matrices()

        # Shaders
        self.current_shader: Shader = None
        self.normal_shader = Shader("shaders/vertex_shader.glsl", "shaders/fragment_shader.glsl")
        self.phong_shader = Shader("shaders/phong_vs.glsl", "shaders/phong_fs.glsl")
        self.gouraud_shader = Shader("shaders/gouraud_vs.glsl", "shaders/gouraud_fs.glsl")
        self.light_source_shader = Shader("shaders/light_source_vs.glsl", "shaders/light_source_fs.glsl")
        self.use_shader(self.gouraud_shader)

        self.scene = [
            LoadedObject("data/floor.obj"),
            LoadedObject("data/uv_sphere.obj", x=2, y=1.5, z=-1),
            LoadedObject("data/box/box-T2F_N3F_V3F.obj", x=-1, y=1, z=-2),
            LoadedObject("data/monkey.obj", x=0, y=1, z=1),
        ]

        self.light_obj = LoadedObject("data/box/box-V3F.obj", x=1.2, y=3.0, z=2.0)
        self.light = Light(amb=v3([0.3, 0.3, 0.3]),
                           dif=v3([1.0, 1.0, 1.0]),
                           spe=v3([1.0, 1.0, 1.0]),
                           pos=v3([1.2, 3.0, 2.0]))


    def use_shader(self, shader: Shader) -> None:
        self.current_shader = shader
        self.current_shader.use()
        # Update matrices after changing shader
        self.update_projection()
        self.update_view()

    def _prepare_matrices(self) -> None:
        # Projection matrix
        self._fov = 45
        self._near = 0.1
        self._far = 100
        # View matrix
        self._eye: v3 = v3([math.sin(0) * 5, 8, math.cos(0) * 10])
        self._target: v3 = v3([0, 2.0, 0])
        self._up: v3 = v3([0, 1, 0])

    def update_view(self) -> None:
        """Recalculate view matrix and upload it to shader."""
        self.view_matrix = m44.create_look_at(self._eye, self._target, self._up)
        self.current_shader.set_view(self.view_matrix)

    def update_projection(self) -> None:
        """Recalculate projection matrix and upload it to shader."""
        a = self._width / self._height
        self.projection_matrix = m44.create_perspective_projection(self._fov, a, self._near, self._far)
        self.current_shader.set_projection(self.projection_matrix)

    def on_resize(self, _window, width, height) -> None:
        self._width, self._height = width, height
        glViewport(0, 0, self._width, self._height)
        self.update_projection()

    def main_loop(self) -> None:
        cnt = 0
        while not glfw.window_should_close(self._window):
            glfw.poll_events()

            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # self.current_shader.set_switcher(1)

            rot_x = m44.create_from_x_rotation(0.5 * glfw.get_time())
            rot_y = m44.create_from_y_rotation(0.8 * glfw.get_time())
            trans_y = math.sin(glfw.get_time())
            translation = m44.create_from_translation(v3([0, trans_y, 0]))
            rotation = m44.multiply(rot_x, rot_y)

            upside_down = m44.create_from_x_rotation(math.pi)
            model_1 = m44.multiply(upside_down, self.scene[1].pos)
            model_1 = m44.multiply(translation, model_1)
            model_1 = m44.multiply(rot_y, model_1)
            self.scene[1].model = model_1

            # self.scene[2].model = m44.multiply(rotation, self.scene[2].pos)
            self.scene[3].model = m44.multiply(rotation, self.scene[3].pos)

            # View
            cam_x = math.sin(glfw.get_time() * 0.5) * 7
            cam_z = math.cos(glfw.get_time() * 0.5) * 7
            # self._eye = v3([-cam_x, 3.0, cam_z])
            cam_front = v3([0, 0, -1])
            # self._target = self._eye + cam_front   # Front facing camera
            # self._target = v3.from_matrix44_translation(model_1)  # targeted moving camera

            self.use_shader(self.light_source_shader)
            self.light_obj.pos = m44.create_from_translation(v3([cam_x, 4.0, cam_z]))
            self.light_obj.model = m44.multiply(m44.create_from_scale(v3([0.2, 0.2, 0.2])), self.light_obj.pos)
            self.light.set_pos(v3([cam_x, 4.0, cam_z]))

            # print(self.light_obj.pos)
            # print(self.light_obj.model)
            self.light_obj.draw(self.current_shader)

            # Lighting shader
            # if cnt < 1000:
            #     self.use_shader(self.gouraud_shader)
            # else:
            self.use_shader(self.phong_shader)
                # if cnt == 2000:
                #     cnt = 0
            # cnt += 1

            self.current_shader.set_v3("viewPos", self._eye)

            # light_color = v3([
            #     math.sin(glfw.get_time() * 2.0),
            #     math.sin(glfw.get_time() * 0.7),
            #     math.sin(glfw.get_time() * 1.3)
            # ])
            #
            # diffuse_color = light_color * v3([0.5]*3)
            # ambient_color = diffuse_color * v3([0.2]*3)
            #
            # self.current_shader.set_v3("light.ambient", ambient_color)
            # self.current_shader.set_v3("light.diffuse", diffuse_color)

            # self.current_shader.set_v3("lightPos", v3.from_matrix44_translation(self.light_obj.pos))
            #
            # self.current_shader.set_v3("light.ambient", v3([0.3, 0.3, 0.3]))
            # self.current_shader.set_v3("light.diffuse", v3([1.0, 1.0, 1.0]))
            # self.current_shader.set_v3("light.specular", v3([1.0, 1.0, 1.0]))
            self.light.use_light(self.current_shader)
            # Draw shaded objects
            for o in self.scene:
                o.draw(self.current_shader)

            # Swap buffers
            glfw.swap_buffers(self._window)


def main():
    window = Window(1280, 720, "GK Final")
    window.main_loop()


if __name__ == '__main__':
    main()
    glfw.terminate()
