import glfw
from OpenGL.GL import *
from pyrr import matrix44 as m44, Vector3 as v3
import math

from shader import Shader
from loaded_object import LoadedObject
from light import DirLight, PointLight, SpotLight


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
        glfw.set_window_size_callback(self._window, self._on_resize)
        # Set keyboard input handler
        glfw.set_key_callback(self._window, self._on_key_input)
        # Set window as current context
        glfw.make_context_current(self._window)

        # Set options
        self._background_color = [0.7, 0.7, 0.6]
        glClearColor(*self._background_color, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Camera
        self.sel_camera: str = "static"  # Selected camera name
        self.update_camera: bool = True
        self._static_target: v3 = v3([0, 2.0, 0])
        self._default_eye: v3 = v3([math.sin(0) * 5, 8, math.cos(0) * 10])
        self._camera_front = v3([0, 0, -1])

        # Matrices
        self._fov, self._near, self._far = None, None, None
        self._eye, self._target, self._up = None, None, None
        self.projection_matrix, self.view_matrix = None, None
        self._prepare_matrices()

        # Shaders
        # TODO: Update Gouraud
        self.shaders = {
            "phong": Shader("shaders/phong_vs.glsl", "shaders/phong_fs.glsl"),
            "gouraud": Shader("shaders/gouraud_vs.glsl", "shaders/gouraud_fs.glsl"),
            "light_source": Shader("shaders/light_source_vs.glsl", "shaders/light_source_fs.glsl"),
        }
        self.current_shader: Shader = None
        self.sel_shader_key: str = "phong"  # Shaders dict key for selected shader
        self._use_shader(self.shaders[self.sel_shader_key])

        # Scene
        self.scene = [
            LoadedObject("data/floor.obj"),
            LoadedObject("data/uv_sphere.obj", 2, 1.5, -1),
            LoadedObject("data/box/box-T2F_N3F_V3F.obj", -1, 1, -2),
            LoadedObject("data/monkey.obj", 0, 1, 1),
        ]

        # Lighting
        self._point_light_obj = LoadedObject("data/uv_sphere.obj")  # sphere to represent point light sources
        self._light_obj = LoadedObject("data/box/box-V3F.obj")  # Box to represent light sources

        # TODO: animate direction and color for night/day cycle
        self.sun_moon = DirLight(amb=v3([0.05, 0.05, 0.05]), dif=v3([0.4, 0.4, 0.8]), spe=v3([0.5, 0.5, 0.8]),
                                 direction=v3([-0.2, -1.0, -0.3]), uni_name="dirLight")
        point_lights_pos = [
            v3([0.7, 0.2, 2.0]),
            v3([2.3, -3.3, -4.0]),
            v3([-1.0, 3.0, -2.0]),
            v3([0.0, 0.0, -3.0])
        ]
        self.point_lights = list(self._pl_gen(point_lights_pos))

        self.spot_light = SpotLight(amb=v3([0.0, 0.0, 0.0]), dif=v3([0.0, 1.0, 0.5]), spe=v3([0.0, 1.0, 0.5]),
                                    k=v3([1.0, 0.09, 0.032]), pos=v3([5.0, 1.5, -1.0]), direction=v3([-1.0, -0.2, 0.0]),
                                    co=math.cos(math.radians(12.5)), oco=math.cos(math.radians(15.0)),
                                    uni_name="spotLight", lss=self.shaders["light_source"], obj=self._light_obj)

    def _pl_gen(self, positions):
        """Point lights generator."""
        for i, p in enumerate(positions):
            light = PointLight(amb=v3([0.05, 0.05, 0.05]), dif=v3([0.8, 0.8, 0.8]), spe=v3([1.0, 1.0, 1.0]),
                               k=v3([1.0, 0.09, 0.032]), pos=p,
                               uni_name=f"pointLights[{i}]", lss=self.shaders["light_source"], obj=self._point_light_obj)
            yield light

    def _use_shader(self, shader: Shader) -> None:
        self.current_shader = shader
        self.current_shader.use()
        # Update matrices after changing shader
        self._update_projection()
        self._update_view()

    def _prepare_matrices(self) -> None:
        # Projection matrix
        self._fov = 45
        self._near = 0.1
        self._far = 100
        # View matrix
        self._eye: v3 = self._default_eye
        self._target: v3 = self._static_target
        self._up: v3 = v3([0, 1, 0])

    def _update_view(self) -> None:
        """Recalculate view matrix and upload it to shader."""
        self.view_matrix = m44.create_look_at(self._eye, self._target, self._up)
        self.current_shader.set_view(self.view_matrix)

    def _update_projection(self) -> None:
        """Recalculate projection matrix and upload it to shader."""
        a = self._width / self._height
        self.projection_matrix = m44.create_perspective_projection(self._fov, a, self._near, self._far)
        self.current_shader.set_projection(self.projection_matrix)

    def _on_resize(self, _window, width, height) -> None:
        self._width, self._height = width, height
        glViewport(0, 0, self._width, self._height)
        self._update_projection()

    def _on_key_input(self, _window, key, _scancode, action, _mode) -> None:
        if action != glfw.PRESS:
            return
        cam = {glfw.KEY_1: "static", glfw.KEY_2: "following", glfw.KEY_3: "moving"}
        if key in cam:
            self.sel_camera = cam[key]
            self.update_camera = True
        elif key == glfw.KEY_O:
            self.sel_shader_key = "gouraud"
        elif key == glfw.KEY_P:
            self.sel_shader_key = "phong"

    def _move_objects(self) -> None:
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

    def _process_camera(self) -> None:
        if not self.update_camera:
            return

        if self.sel_camera == "static":
            self._eye = self._default_eye
            self._target = self._static_target
            self.update_camera = False  # Static camera needs to be calculated only once.
        elif self.sel_camera == "following":
            self._eye = self._default_eye
            self._target = v3.from_matrix44_translation(self.scene[1].model)
        elif self.sel_camera == "moving":
            cam_x = math.sin(glfw.get_time() * 0.5) * 7
            cam_z = math.cos(glfw.get_time() * 0.5) * 7
            self._eye = v3([-cam_x, 3.0, cam_z])
            self._target = self._eye + self._camera_front  # Front facing camera
        self._update_view()

    def _draw_light_sources(self) -> None:
        """Draws light sources with appropriate shaders."""
        self._use_shader(self.shaders["light_source"])
        for light in self.point_lights:
            light.draw()
        self.spot_light.draw()

    def _draw_objects(self) -> None:
        """Sets currently selected shader, then draws shaded objects."""
        self._use_shader(self.shaders[self.sel_shader_key])
        self.current_shader.set_v3("viewPos", self._eye)

        fog_start = math.sin(glfw.get_time() * 0.5) * 6 + 6
        self.current_shader.set_v3("fogParams.color", v3(self._background_color))
        self.current_shader.set_float("fogParams.start", fog_start)
        self.current_shader.set_float("fogParams.end", fog_start + 10)

        # Use lights
        self.sun_moon.use_light(self.current_shader)
        for light in self.point_lights:
            light.use_light(self.current_shader)
        self.spot_light.use_light(self.current_shader)

        # Draw objects
        for o in self.scene:
            o.draw(self.current_shader)

    def main_loop(self) -> None:
        while not glfw.window_should_close(self._window):
            glfw.poll_events()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Update scene
            self._move_objects()
            self._process_camera()

            # Draw scene
            self._draw_light_sources()
            self._draw_objects()

            # Swap buffers
            glfw.swap_buffers(self._window)


def main():
    window = Window(1280, 720, "GK Final")
    window.main_loop()
    glfw.terminate()


if __name__ == '__main__':
    main()
