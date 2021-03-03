#version 330 core
out vec4 FragColor;

struct FogParams
{
	vec3 color;
	float start;
	float end;
    bool on;
};

uniform vec3 color;
uniform FogParams fogParams;
in vec4 eyeSpacePosition;

float getFogFactor(FogParams params, float fogCoordinate);

void main()
{
    if (fogParams.on)
    {
        float fogCoordinate = abs(eyeSpacePosition.z / eyeSpacePosition.w);
        FragColor = vec4(mix(color, fogParams.color, getFogFactor(fogParams, fogCoordinate)), 1.0f);
    }
    else
    {
        FragColor = vec4(color, 1.0f);
    }
}

float getFogFactor(FogParams params, float fogCoordinate)
{
    float fogLength = params.end - params.start;
    float result = (params.end - fogCoordinate) / fogLength;

	return 1.0 - clamp(result, 0.0, 1.0);;
}