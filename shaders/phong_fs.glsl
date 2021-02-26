#version 330 core

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct Light {
//    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};


in vec3 v_normal;
in vec3 frag_pos;
in vec3 v_color;
in vec2 v_texture;
in vec3 LightPos;

out vec4 FragColor;

uniform Material material;
uniform Light light;
uniform vec3 objectColor;

uniform sampler2D s_texture;

void main()
{
    // Ambient
    vec3 ambient = light.ambient * material.ambient;

    // Diffuse
    vec3 norm = normalize(v_normal);
    vec3 lightDir = normalize(LightPos - frag_pos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * (diff * material.diffuse);

    // Specular
    // the viewer is always at (0,0,0) in view-space, so viewDir is (0,0,0) - Position => -Position
    vec3 viewDir = normalize(-frag_pos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * (spec * material.specular);

    vec4 texel = texture(s_texture, v_texture);
    vec3 result = (ambient + diffuse + specular) * texel.rgb;

//    FragColor = vec4(result, 1.0);
    FragColor = vec4(result, texel.a);
}