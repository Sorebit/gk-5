#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform vec3 lightPos;

out vec3 v_normal;
out vec3 frag_pos;
out vec3 LightPos;
out vec3 v_color;
out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
    frag_pos = vec3(view * model * vec4(a_pos, 1.0));
    v_normal = mat3(transpose(inverse(view * model))) * a_normal;
    LightPos = vec3(view * vec4(lightPos, 1.0));
    v_texture = a_texture;
    v_color = a_color;
}