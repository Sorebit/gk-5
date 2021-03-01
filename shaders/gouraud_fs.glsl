#version 330 core
out vec4 FragColor;

in vec2 v_texture;
in vec3 LightingColor;

uniform sampler2D s_texture;

void main()
{
   vec4 texel = texture(s_texture, v_texture);
   vec3 result = LightingColor * texel.rgb;

   FragColor = vec4(result, 1.0);
}
