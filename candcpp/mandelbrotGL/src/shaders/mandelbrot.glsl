#version 430 core

uniform vec2 resolution;
uniform double zoom;
uniform dvec2 center;
uniform int maxIterations;
uniform int renderMode;
uniform vec2 pixelScale;
uniform int sampleCount;
uniform int palette;
uniform bool juliaMode;
uniform bool juliaZero;
uniform double juliaDistance;
uniform dvec2 juliaC;
uniform double escapeRadiusSquared;

layout(std430, binding = 0) readonly buffer ReferenceOrbit {
  dvec2 orbit[];
};

out vec4 color;

dvec2 complexMul(dvec2 a, dvec2 b) {
  return dvec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

vec3 gradient(vec3 dark, vec3 middle, vec3 light, float value) {
  return mix(mix(dark, middle, smoothstep(0.0, 0.5, value)),
             light, smoothstep(0.5, 1.0, value));
}

vec3 paletteColor(float t) {
  float wave = 0.5 + 0.5 * cos(0.15 * t);
  if (palette == 1) return mix(vec3(0.01, 0.03, 0.15), vec3(0.15, 0.85, 1.0), wave);
  if (palette == 2) return vec3(wave, wave * wave, 0.15 * wave * wave * wave);
  if (palette == 3) return vec3(wave);
  if (palette == 4) return gradient(vec3(0.08, 0.01, 0.2), vec3(0.85, 0.08, 0.35), vec3(1.0, 0.75, 0.3), wave);
  if (palette == 5) return gradient(vec3(0.01, 0.06, 0.04), vec3(0.05, 0.4, 0.18), vec3(0.75, 0.95, 0.35), wave);
  if (palette == 6) return gradient(vec3(0.02, 0.08, 0.25), vec3(0.15, 0.6, 0.85), vec3(0.9, 1.0, 1.0), wave);
  if (palette == 7) return gradient(vec3(0.05, 0.0, 0.12), vec3(0.8, 0.0, 1.0), vec3(0.0, 1.0, 0.7), wave);
  if (palette == 8) return gradient(vec3(0.08, 0.03, 0.0), vec3(0.65, 0.3, 0.02), vec3(1.0, 0.9, 0.45), wave);
  if (palette == 9) return gradient(vec3(0.03, 0.01, 0.1), vec3(0.35, 0.08, 0.65), vec3(0.9, 0.7, 1.0), wave);
  if (palette == 10) return gradient(vec3(0.2, 0.02, 0.15), vec3(1.0, 0.3, 0.6), vec3(0.55, 0.95, 1.0), wave);
  if (palette == 11) {
    vec3 hue = abs(mod(0.12 * t + vec3(0.0, 4.0, 2.0), 6.0) - 3.0);
    return clamp(hue - 1.0, 0.0, 1.0);
  }
  return 0.5 + 0.5 * cos(0.15 * t + vec3(0.0, 2.0, 4.0));
}

vec3 escapedColor(int iteration, float magnitude2) {
  float t = float(iteration + 1) + 1.0 - log2(0.5 * log2(magnitude2));
  return paletteColor(t);
}

vec3 julia(dvec2 dc) {
  // With c = 0, z -> z*z: the filled Julia set is the unit disk.
  double distance = juliaDistance + 2.0 * dot(center, dc) + dot(dc, dc);
  if (distance <= 0.0) return vec3(0.0);

  float logLogRadius;
  if (distance < 0.001) {
    // Avoid rounding 1 + distance to 1 at high zoom levels.
    int exponent;
    double mantissa = frexp(distance, exponent);
    double correction = (1.0 - 0.5 * distance + distance * distance / 3.0) / 1.3862943611198906;
    logLogRadius = log2(float(mantissa)) + float(exponent) + log2(float(correction));
  } else {
    logLogRadius = log2(0.5 * log2(1.0 + float(distance)));
  }
  float t = 1.0 - logLogRadius;
  if (float(maxIterations) <= t - 1.0) return vec3(0.0);
  return paletteColor(t);
}

bool interior(vec2 c) {
  float x = c.x - 0.25;
  float y2 = c.y * c.y;
  float q = x * x + y2;
  // Leave a margin around the boundary for floating-point error.
  return q * (q + x) < 0.25 * y2 - 1e-7 ||
      (c.x + 1.0) * (c.x + 1.0) + y2 < 0.0625 - 1e-7;
}

bool interior(dvec2 c) {
  double x = c.x - 0.25;
  double y2 = c.y * c.y;
  double q = x * x + y2;
  return q * (q + x) < 0.25 * y2 - 1e-15 ||
      (c.x + 1.0) * (c.x + 1.0) + y2 < 0.0625 - 1e-15;
}

vec3 directFloat(vec2 c) {
  if (!juliaMode && interior(c)) return vec3(0.0);
  vec2 z = juliaMode ? c : vec2(0.0);
  vec2 parameter = juliaMode ? vec2(juliaC) : c;
  vec2 checkpoint = z;
  int nextCheckpoint = 32;
  for (int i = 0; i < maxIterations; ++i) {
    z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + parameter;
    float magnitude2 = dot(z, z);
    if (magnitude2 > float(escapeRadiusSquared)) return escapedColor(i, magnitude2);
    if ((i & 15) == 15) {
      if (all(equal(z, checkpoint))) return vec3(0.0);
      if (i + 1 == nextCheckpoint) {
        checkpoint = z;
        nextCheckpoint *= 2;
      }
    }
}
  return vec3(0.0);
}

vec3 directDouble(dvec2 c) {
  if (!juliaMode && interior(c)) return vec3(0.0);
  dvec2 z = juliaMode ? c : dvec2(0.0);
  dvec2 parameter = juliaMode ? juliaC : c;
  dvec2 checkpoint = z;
  int nextCheckpoint = 32;
  for (int i = 0; i < maxIterations; ++i) {
    z = complexMul(z, z) + parameter;
    double magnitude2 = dot(z, z);
    if (magnitude2 > escapeRadiusSquared) return escapedColor(i, float(magnitude2));
    if ((i & 15) == 15) {
      if (all(equal(z, checkpoint))) return vec3(0.0);
      if (i + 1 == nextCheckpoint) {
        checkpoint = z;
        nextCheckpoint *= 2;
      }
    }
  }
  return vec3(0.0);
}

vec3 perturbation(dvec2 dc) {
  if (!juliaMode && interior(center + dc)) return vec3(0.0);
  int orbitSize = orbit.length();
  if (orbitSize < 2) return vec3(1.0, 0.0, 1.0);

  dvec2 dz = juliaMode ? dc : dvec2(0.0);
  dvec2 deltaC = juliaMode ? dvec2(0.0) : dc;
  int refIndex = 0;
  for (int i = 0; i < maxIterations; ++i) {
    dvec2 nextDz = 2.0 * complexMul(orbit[refIndex], dz) +
                  complexMul(dz, dz) + deltaC;
    dvec2 z = orbit[refIndex + 1] + nextDz;
    double magnitude2 = dot(z, z);
    if (magnitude2 > escapeRadiusSquared) return escapedColor(i, float(magnitude2));

    // Rebase before running off a truncated reference orbit, or when
    // cancellation makes the perturbation larger than the pixel orbit.
    if (magnitude2 < dot(nextDz, nextDz) || refIndex + 2 >= orbitSize) {
        dz = juliaMode ? (orbit[refIndex + 1] - orbit[0]) + nextDz : z;
        refIndex = 0;
    } else {
        dz = nextDz;
        ++refIndex;
    }
  }
  return vec3(0.0);
}

vec3 sampleFractal(vec2 position) {
  if (juliaZero) {
    dvec2 pixel = dvec2(position) * dvec2(pixelScale) - dvec2(resolution) * 0.5;
    return julia(pixel * (3.0 / double(resolution.y) / zoom));
  }
  if (renderMode == 0) {
    vec2 pixel = position * pixelScale - resolution * 0.5;
    vec2 c = vec2(center) + pixel * (3.0 / resolution.y / float(zoom));
    return directFloat(c);
  } else {
    dvec2 pixel = dvec2(position) * dvec2(pixelScale) - dvec2(resolution) * 0.5;
    dvec2 dc = pixel * (3.0 / double(resolution.y) / zoom);
    if (renderMode == 1) return directDouble(center + dc);
    return perturbation(dc);
  }
}

void main() {
  if (sampleCount <= 1) {
    color = vec4(sampleFractal(gl_FragCoord.xy), 1.0);
    return;
  }

  // Maximum 16 samples per pixel.
  int samples = clamp(sampleCount, 1, 16);

  vec3 accumulated = vec3(0.0);

  // Golden-angle low-discrepancy sampling pattern.
  // Each sample is distributed inside the pixel.
  const float goldenAngle = 2.39996323;

  for (int i = 0; i < samples; ++i) {
    float radius = sqrt((float(i) + 0.5) / float(samples));
    float angle = float(i) * goldenAngle;

    vec2 offset = 0.5 * radius *
      vec2(cos(angle), sin(angle));

    accumulated += sampleFractal(gl_FragCoord.xy + offset);
  }

  color = vec4(accumulated / float(samples), 1.0);
}
