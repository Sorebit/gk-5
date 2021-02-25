# version 330 core

in vec3 v_color;
in vec2 v_texture;
in vec3 v_normal;

out vec4 out_color;
uniform int switcher;

uniform sampler2D s_texture;
uniform vec3 light_color;

void main()
{
//    vec3 ambient_light_intensity = vec3(0.3f, 0.2f, 0.4f);
//    vec3 sun_light_intensity = vec3(0.9f, 0.9f, 0.9f);
//    vec3 sun_light_direction = normalize(vec3(0.0f, 0.0f, 2.0f));

//    vec3 light_intensity = ambient_light_intensity + sun_light_intensity * max(dot(v_normal, sun_light_direction), 0.0f);

    if (switcher == 0)
    {
        vec4 texel = texture(s_texture, v_texture);
//        out_color = vec4(texel.rgb * light_intensity, texel.a);
        out_color = vec4(texel.rgb * light_color, texel.a);
        out_color = texel;
    }
    else if (switcher == 1)
    {
        out_color = vec4(v_color, 1.0f);
    }
}
