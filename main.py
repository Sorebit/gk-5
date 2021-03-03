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
        self._background_color_night = v3([0.0, 0.05, 0.1])
        self._background_color_day = v3([0.6, 0.7, 0.75])

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Camera
        self.sel_camera: str = "static"  # Selected camera name
        self.update_camera: bool = True
        self._static_target: v3 = v3([0, 2.0, 0])
        self._default_eye: v3 = v3([math.sin(0) * 10, 8, math.cos(0) * 10])

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
        self._fog_on = False
        self._fog_color = v3([0, 0, 0])

        # Scene
        self.scene = {
            "floor": LoadedObject("data/floor.obj"),
            "earth": LoadedObject("data/uv_sphere.obj", 0, 1.4 * 1.5, 0, scale=1.4),
            "race_monkey": LoadedObject("data/monkey.obj", -3, 1.2, 0, ),
        }
        self.scene = {**dict(self._box_gen(6, 7.0)), **self.scene}  # Generate boxes

        # Lighting
        self._point_light_obj = LoadedObject("data/uv_sphere.obj")  # sphere to represent point light sources
        self._light_obj = LoadedObject("data/box/box-V3F.obj")  # Box to represent light sources

        self.sun_moon = DirLight(amb=v3([0.05, 0.05, 0.05]), dif=v3([0.4, 0.4, 0.8]), spe=v3([0.4, 0.4, 0.8]),
                                 direction=v3([-0.2, -1.0, -0.3]), uni_name="dirLight")
        point_lights = [
            (v3([5.5, 0.2, -5.5]), v3([1.0, 1.0, 1.0])),  # red
            (v3([-5.5, 0.2, 0.0]), v3([1.0, 1.0, 0.3])),  # yellow
            (v3([7.5, 2.2, 1.0]), v3([0.3, 0.3, 1.0])),  # blue
            (v3([3.0, 0.2, 3.0]), v3([1.0, 0.3, 0.3]))  # white
        ]
        self.point_lights = list(self._pl_gen(point_lights))

        self.spot_light_offset = v3([0.0, -0.8, 0.75])  # Relative offset from monkey
        self.spot_light_def_dir = v3([0.0, -0.2, 0.0])  # Default direction (same as monkey)
        self.spot_light_angle_offset = 0  # TODO: Add changing with keyboard
        self.spot_light = SpotLight(amb=v3([0.0, 0.0, 0.0]), dif=v3([0.0, 1.0, 0.5]), spe=v3([0.0, 1.0, 0.5]),
                                    k=v3([1.0, 0.07, 0.017]), pos=v3([0.0] * 3), direction=self.spot_light_def_dir,
                                    co=math.cos(math.radians(22.5)), oco=math.cos(math.radians(25.0)),
                                    uni_name="spotLight", lss=self.shaders["light_source"], obj=None)

    def _pl_gen(self, positions):
        """Point lights generator."""
        for i, (p, c) in enumerate(positions):
            light = PointLight(amb=0.05 * c, dif=1.0 * c, spe=1.0 * c,
                               k=v3([1.0, 0.07, 0.017]), pos=p,
                               uni_name=f"pointLights[{i}]", lss=self.shaders["light_source"],
                               obj=self._point_light_obj)
            yield light

    def _box_gen(self, num, mx):
        box_path = "data/box/box-T2F_N3F_V3F.obj"
        p = lambda n: (mx * 2) / num * (n % num) - mx + 1

        for i in range(num * 4):
            if i < num:
                yield f"box_{i}", LoadedObject(box_path, p(i), 1.0, -mx - 1)
                yield f"box_{i}_", LoadedObject(box_path, p(i), 3.0, -mx - 1)
            elif i < num * 2:
                yield f"box_{i}", LoadedObject(box_path, p(i), 1.0, mx + 1)
                yield f"box_{i}_", LoadedObject(box_path, p(i), 3.0, mx + 1)
            elif i < num * 3:
                yield f"box_{i + 12}", LoadedObject(box_path, mx + 1, 1.0, p(i))
                yield f"box_{i + 12}_", LoadedObject(box_path, mx + 1, 3.0, p(i))
            else:
                yield f"box_{i + 18}", LoadedObject(box_path, -mx - 1, 1.0, p(i))

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
        left_right = {glfw.KEY_LEFT: 0.1, glfw.KEY_RIGHT: -0.1}
        if key in left_right:
            self.spot_light_angle_offset += left_right[key]
            return

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
        elif key == glfw.KEY_F:
            self._fog_on = not self._fog_on

    def _set_daytime(self):
        blend_factor = (math.sin(glfw.get_time() * 0.1) + 1) / 2
        c = self._background_color_day * (1 - blend_factor) + self._background_color_night * blend_factor

        self.sun_moon._diffuse = 0.9 * c
        self.sun_moon._specular = 0.9 * c
        self._fog_color = c
        glClearColor(c.x, c.y, c.z, 1)

    def _move_objects(self) -> None:
        time = glfw.get_time()
        # Move and rotate earth
        rot_y = m44.create_from_y_rotation(-0.5 * time)
        translation = m44.create_from_translation(v3([0, math.sin(time), 0]))

        model = m44.create_from_x_rotation(math.pi)  # upside down
        model = m44.multiply(translation, m44.multiply(model, self.scene["earth"].pos))  # up-down movement
        self.scene["earth"].model = m44.multiply(rot_y, model)  # rotation

        # Move and orientate race_monkey
        translation = v3([math.sin(time) * 5, 1.2, math.cos(time) * 5])
        o = self.scene["race_monkey"]
        o.set_pos(translation)
        o.model = m44.multiply(m44.create_from_y_rotation(-time - math.pi / 2), o.model)

        # Move and orientate spotlight relatively to race_monkey
        pos = m44.multiply(m44.create_from_translation(self.spot_light_offset), o.model)
        self.spot_light.set_pos(v3.from_matrix44_translation(pos))
        light_dir = self._get_monkey_look_dir() + self.spot_light_def_dir
        self.spot_light.set_dir(light_dir)

    def _get_monkey_look_dir(self):
        angle = glfw.get_time() + math.pi / 2 + self.spot_light_angle_offset
        return v3([math.sin(angle), 0.0, math.cos(angle)])

    def _process_camera(self) -> None:
        if not self.update_camera:
            return

        if self.sel_camera == "static":
            self._eye = self._default_eye
            self._target = self._static_target
            self.update_camera = False  # Static camera needs to be calculated only once.
        elif self.sel_camera == "following":
            self._eye = self._default_eye
            self._target = v3.from_matrix44_translation(self.scene["race_monkey"].model)
        elif self.sel_camera == "moving":
            m = m44.multiply(m44.create_from_translation(v3([0, 1.0, 0])), self.scene["race_monkey"].model)
            self._eye = v3.from_matrix44_translation(m)
            self._target = self._eye + + self._get_monkey_look_dir()  # Front facing camera
        self._update_view()

    def _fog_params(self):
        self.current_shader.set_bool("fogParams.on", self._fog_on)
        if self._fog_on:
            fog_start = math.sin(glfw.get_time() * 0.5) * 4 + 8
            self.current_shader.set_v3("fogParams.color", self._fog_color)
            self.current_shader.set_float("fogParams.start", fog_start)
            self.current_shader.set_float("fogParams.end", fog_start + 10)

    def _draw_light_sources(self) -> None:
        """Draws light sources with appropriate shaders."""
        self._use_shader(self.shaders["light_source"])
        self._fog_params()
        for light in self.point_lights:
            light.draw()
        self.spot_light.draw()

    def _draw_objects(self) -> None:
        """Sets currently selected shader, then draws shaded objects."""
        self._use_shader(self.shaders[self.sel_shader_key])
        self.current_shader.set_v3("viewPos", self._eye)
        self._fog_params()

        # Use lights
        self.sun_moon.use_light(self.current_shader)
        for light in self.point_lights:
            light.use_light(self.current_shader)
        self.spot_light.use_light(self.current_shader)

        # Draw objects
        for o in self.scene.values():
            o.draw(self.current_shader)

    def main_loop(self) -> None:
        while not glfw.window_should_close(self._window):
            glfw.poll_events()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Update scene
            self._set_daytime()
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
