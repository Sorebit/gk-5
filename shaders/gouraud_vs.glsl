#version 330 core

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

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

out vec3 LightingColor;
out vec2 v_texture;

uniform Material material;
uniform Light light;
uniform vec3 viewPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    // gouraud shading
    // ------------------------
    vec3 Position = vec3(model * vec4(a_pos, 1.0));
    vec3 Normal = mat3(transpose(inverse(model))) * a_normal;

    // Ambient
    vec3 ambient = material.ambient * light.ambient;

    // Diffuse
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - Position);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * (diff * material.diffuse);

    // Specular
    vec3 viewDir = normalize(viewPos - Position);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * (spec * material.specular);

    LightingColor = ambient + diffuse + specular;
    v_texture = a_texture;
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
}
