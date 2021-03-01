#version 330 core
out vec4 FragColor;

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct Light {
    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 v_normal;
in vec3 frag_pos;
in vec3 v_color;
in vec2 v_texture;

uniform vec3 viewPos;
uniform Material material;
uniform Light light;

uniform sampler2D s_texture;

void main()
{
    // Ambient
    vec3 ambient = light.ambient * material.ambient;

    // Diffuse
    vec3 norm = normalize(v_normal);
    vec3 lightDir = normalize(light.position - frag_pos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * (diff * material.diffuse);

    // Specular
    vec3 viewDir = normalize(viewPos - frag_pos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * (spec * material.specular);

    vec4 texel = texture(s_texture, v_texture);
    vec3 result = (ambient + diffuse + specular) * texel.rgb;

    FragColor = vec4(result, texel.a);
}