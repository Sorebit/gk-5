#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 eyeSpacePosition;

void main()
{
    eyeSpacePosition = view * model * vec4(a_pos, 1.0);
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
}