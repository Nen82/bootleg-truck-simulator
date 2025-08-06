#version 130

uniform sampler2D grassTex;
uniform sampler2D rockTex;
uniform sampler2D snowTex;

in vec2 texcoord;
in float height;

out vec4 fragColor;

void main() {
    vec4 grass = texture(grassTex, texcoord);
    vec4 rock = texture(rockTex, texcoord);
    vec4 snow = texture(snowTex, texcoord);

    if (height < 20.0)
        fragColor = grass;
    else if (height < 40.0)
        fragColor = mix(grass, rock, (height - 20.0) / 20.0);
    else if (height < 60.0)
        fragColor = mix(rock, snow, (height - 40.0) / 20.0);
    else
        fragColor = snow;
}
