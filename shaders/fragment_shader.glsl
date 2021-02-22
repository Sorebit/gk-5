# version 330 core

in vec3 v_color;
in vec2 v_texture;

out vec4 out_color;
uniform int switcher;

uniform sampler2D s_texture;

void main()
{
    if (switcher == 0)
    {
        out_color = texture(s_texture, v_texture);
    }
    else if (switcher == 1)
    {
        out_color = vec4(v_color, 1.0f);
    }
}
