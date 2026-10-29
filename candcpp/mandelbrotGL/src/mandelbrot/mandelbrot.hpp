
#pragma once

#include <glad/gl.h>
#include <array>
#include <cstdint>
#include <string>

class Mandelbrot
{
public:
  static constexpr int paletteCount = 12;

  Mandelbrot(
      const std::string &x,
      const std::string &y,
      double z,
      int n);

  ~Mandelbrot();

  void draw(int width, int height, bool interactive = false);
  void redraw(int width, int height);
  bool refine(int width, int height);
  void zoomBy(double factor, double x = 0.0, double y = 0.0);
  void pan(double x, double y);
  void setView(const std::string &x, const std::string &y, double z, int n, bool automatic);
  void setPalette(int value);
  void setJuliaParameter(double x, double y);
  void setJuliaParameter(const std::string &x, const std::string &y);
  void setJuliaMode(bool enabled);
  const std::string &getCenterX() const { return centerX; }
  const std::string &getCenterY() const { return centerY; }
  double getZoom() const { return zoom; }
  int getIterationLimit() const { return iterationLimit; }
  int getIterations() const { return iterationBudget(); }
  bool getAutomaticIterations() const { return automaticIterations; }
  int getPalette() const { return palette; }
  double getJuliaX() const { return juliaX; }
  double getJuliaY() const { return juliaY; }
  const std::string &getJuliaReal() const { return juliaReal; }
  const std::string &getJuliaImaginary() const { return juliaImaginary; }
  bool isJulia() const { return juliaMode; }
  std::uint64_t viewRevision() const { return revision; }

private:
  int iterationBudget() const;
  double previewPixelWork() const;
  void updateJuliaUniforms();
  void computeReferenceOrbit(int count);
  void ensureTargets(int width, int height);
  void drawPass(int width, int height, int renderWidth, int renderHeight,
                int count, int samples);
  void present(GLuint source, int sourceWidth, int sourceHeight,
               int width, int height);
  void collectTimings();
  GLuint beginTiming(bool preview, int pixels);

  std::string centerX;
  std::string centerY;

  double zoom;
  int iterationLimit;
  bool automaticIterations = true;
  int palette = 0;
  bool juliaMode = false;
  double juliaX = -0.8;
  double juliaY = 0.156;
  std::string juliaReal = "-0.8";
  std::string juliaImaginary = "0.156";
  bool juliaParameterZero = false;
  int referenceIterations = 0;
  bool referenceEscaped = false;
  std::uint64_t revision = 0;
  bool orbitDirty = false;
  double viewCenterX = 0.0;
  double viewCenterY = 0.0;

  GLuint program = 0;
  GLuint vao = 0;
  GLuint orbitSSBO = 0;
  GLuint framebuffers[2] = {};
  GLuint textures[2] = {};
  int targetWidth = 0;
  int targetHeight = 0;
  int previewWidth = 0;
  int previewHeight = 0;
  int refinedRows = 0;
  bool refinementStarted = false;
  double previewScale = 0.5;
  double previewWork = 0.0;
  int tilePixels = 32768;

  struct Timing
  {
    GLuint query = 0;
    bool pending = false;
    bool preview = false;
    int pixels = 0;
    double work = 0.0;
  };
  std::array<Timing, 3> timings;

  GLint resolutionLocation = -1;
  GLint zoomLocation = -1;
  GLint iterationsLocation = -1;
  GLint centerLocation = -1;
  GLint modeLocation = -1;
  GLint pixelScaleLocation = -1;
  GLint samplesLocation = -1;
  GLint paletteLocation = -1;
  GLint juliaLocation = -1;
  GLint juliaZeroLocation = -1;
  GLint juliaDistanceLocation = -1;
  GLint juliaParameterLocation = -1;
  GLint escapeRadiusLocation = -1;
};
