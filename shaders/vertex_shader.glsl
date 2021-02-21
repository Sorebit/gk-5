# version 330 core

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 v_color;
out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0f);
    v_texture = a_texture;
    v_color = a_color;
}