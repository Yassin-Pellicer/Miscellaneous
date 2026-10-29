#version 430 core

uniform vec2 resolution;
uniform double zoom;
uniform dvec2 center;
uniform int maxIterations;
uniform int renderMode;
uniform vec2 pixelScale;
uniform int sampleCount;

layout(std430, binding = 0) readonly buffer ReferenceOrbit {
  dvec2 orbit[];
};

out vec4 color;

dvec2 complexMul(dvec2 a, dvec2 b) {
  return dvec2(a.x * b.x - a.y * b.y, a.x * b.y + a.y * b.x);
}

vec3 escapedColor(int iteration, float magnitude2) {
  float t = float(iteration + 1) + 1.0 - log2(0.5 * log2(magnitude2));
  return 0.5 + 0.5 * cos(0.15 * t + vec3(0.0, 2.0, 4.0));
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
  if (interior(c)) return vec3(0.0);
  vec2 z = vec2(0.0);
  vec2 checkpoint = z;
  int nextCheckpoint = 32;
  for (int i = 0; i < maxIterations; ++i) {
    z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
    float magnitude2 = dot(z, z);
    if (magnitude2 > 4.0) return escapedColor(i, magnitude2);
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
  if (interior(c)) return vec3(0.0);
  dvec2 z = dvec2(0.0);
  dvec2 checkpoint = z;
  int nextCheckpoint = 32;
  for (int i = 0; i < maxIterations; ++i) {
    z = complexMul(z, z) + c;
    double magnitude2 = dot(z, z);
    if (magnitude2 > 4.0) return escapedColor(i, float(magnitude2));
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
  if (interior(center + dc)) return vec3(0.0);
  int orbitSize = orbit.length();
  if (orbitSize < 2) return vec3(1.0, 0.0, 1.0);

  dvec2 dz = dvec2(0.0);
  int refIndex = 0;
  for (int i = 0; i < maxIterations; ++i) {
    dvec2 nextDz = 2.0 * complexMul(orbit[refIndex], dz) +
                  complexMul(dz, dz) + dc;
    dvec2 z = orbit[refIndex + 1] + nextDz;
    double magnitude2 = dot(z, z);
    if (magnitude2 > 4.0) return escapedColor(i, float(magnitude2));

    // Rebase before running off a truncated reference orbit, or when
    // cancellation makes the perturbation larger than the pixel orbit.
    if (magnitude2 < dot(nextDz, nextDz) || refIndex + 2 >= orbitSize) {
        dz = z;
        refIndex = 0;
    } else {
        dz = nextDz;
        ++refIndex;
    }
  }
  return vec3(0.0);
}

vec3 sampleFractal(vec2 position) {
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
  // Actual fractal edges need subpixel evaluations: coverage MSAA on
  // the fullscreen triangle alone cannot smooth these interior edges.
  if (sampleCount == 2) {
      vec3 a = sampleFractal(gl_FragCoord.xy + vec2(-0.25, -0.25));
      vec3 b = sampleFractal(gl_FragCoord.xy + vec2(0.25, 0.25));
      color = vec4((a + b) * 0.5, 1.0);
  } else {
      color = vec4(sampleFractal(gl_FragCoord.xy), 1.0);
  }
}
