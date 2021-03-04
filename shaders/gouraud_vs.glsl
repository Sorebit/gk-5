#version 330 core

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct SpotLight {
    vec3 position;
    vec3 direction;
    float cutOff;
    float outerCutOff;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

#define NR_POINT_LIGHTS 4

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_color;
layout(location = 3) in vec3 a_normal;

out vec3 LightingColor;
out vec2 v_texture;

uniform Material material;
uniform vec3 viewPos;
uniform DirLight dirLight;
uniform PointLight pointLights[NR_POINT_LIGHTS];
uniform SpotLight spotLight;


uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir);
vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);
vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir);

void main()
{
    // gouraud shading
    // ------------------------
    vec3 Position = vec3(model * vec4(a_pos, 1.0));
    vec3 Normal = mat3(transpose(inverse(model))) * a_normal;

    // Ambient
//    vec3 ambient = material.ambient * light.ambient;

    // Diffuse
//    vec3 norm = normalize(Normal);
//    vec3 lightDir = normalize(light.position - Position);
//    float diff = max(dot(norm, lightDir), 0.0);
//    vec3 diffuse = light.diffuse * (diff * material.diffuse);

    // Specular
//    vec3 viewDir = normalize(viewPos - Position);
//    vec3 reflectDir = reflect(-lightDir, norm);
//    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
//    vec3 specular = light.specular * (spec * material.specular);

    //

    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - Position);
//    vec4 texel = texture(s_texture, v_texture);

    // Directional light
    vec3 result = CalcDirLight(dirLight, norm, viewDir);

    // Point lights
    for(int i = 0; i < NR_POINT_LIGHTS; i++)
        result += CalcPointLight(pointLights[i], norm, Position, viewDir);

    // Spot light
    result += CalcSpotLight(spotLight, norm, Position, viewDir);



//    FragColor = vec4(result, texel.a);

    //
    LightingColor = result;
    v_texture = a_texture;
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
}

vec3 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);
    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // combine results
    vec3 ambient = light.ambient * material.ambient;
    vec3 diffuse = light.diffuse * diff * material.diffuse;
    vec3 specular = light.specular * spec * material.specular;

    return (ambient + diffuse + specular);
}

vec3 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    // combine results
    vec3 ambient  = light.ambient  * material.ambient;
    vec3 diffuse  = light.diffuse  * diff * material.diffuse;
    vec3 specular = light.specular * spec * material.specular;
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;

    return (ambient + diffuse + specular);
}

vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);
    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);
    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    // combine results
    vec3 ambient  = light.ambient  * material.ambient;
    vec3 diffuse  = light.diffuse  * diff * material.diffuse;
    vec3 specular = light.specular * spec * material.specular;
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;

    // spotlight intensity
    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    ambient  *= intensity;
    diffuse  *= intensity;
    specular *= intensity;

    return (ambient + diffuse + specular);
}