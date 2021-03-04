#version 330 core
out vec4 FragColor;

struct FogParams
{
	vec3 color;
	float start;
	float end;
    bool on;
};

in vec2 v_texture;
in vec3 LightingColor;

uniform FogParams fogParams;
uniform sampler2D s_texture;

float getFogFactor(FogParams params, float fogCoordinate);

void main()
{
   vec4 texel = texture(s_texture, v_texture);
   vec3 result = LightingColor * texel.rgb;

       // Apply fog
    if (fogParams.on)
    {
//        float fogCoordinate = abs(eyeSpacePosition.z / eyeSpacePosition.w);
//        result = mix(result, fogParams.color, getFogFactor(fogParams, fogCoordinate));
    }

   FragColor = vec4(result, 1.0);
}

float getFogFactor(FogParams params, float fogCoordinate)
{
    float fogLength = params.end - params.start;
    float result = (params.end - fogCoordinate) / fogLength;

	return 1.0 - clamp(result, 0.0, 1.0);;
}