/**
 * @file mandelbrot.cpp
 * @brief Implementation of the Mandelbrot class for GPU rendering.
 */

#include "mandelbrot.hpp"
#include "../init.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>
#include <mpfr.h>

namespace
{
  /**
   * @brief Read a GLSL shader file into a string.
   * @param path Relative path to the shader.
   * @param name Filename used in error messages.
   * @return Shader source text.
   */
  std::string readShader(const char *path, const char *name)
  {
    std::ifstream file(path);
    if (!file)
      throw std::runtime_error(std::string("Cannot open ") + name);
    return {std::istreambuf_iterator<char>{file}, std::istreambuf_iterator<char>{}};
  }

  constexpr double maximumZoom = 1e100;
  constexpr double minimumPreviewScale = 1.0 / 64.0;

  /**
   * @brief Choose MPFR precision from the zoom level.
   * @param zoom Current zoom factor.
   * @return Precision in bits.
   */
  mpfr_prec_t orbitPrecision(double zoom)
  {
    return std::max<mpfr_prec_t>(
        256, static_cast<mpfr_prec_t>(std::ceil(std::log2(zoom))) + 128);
  }

  /**
   * @brief Convert an MPFR value to a precision-preserving decimal string.
   * @param value Value to convert.
   * @return Decimal representation of the value.
   */
  std::string decimalString(mpfr_srcptr value)
  {
    const int digits = static_cast<int>(
                           std::ceil(mpfr_get_prec(value) * std::log10(2.0))) +
                       1;
    std::vector<char> buffer(digits + 32);
    mpfr_snprintf(buffer.data(), buffer.size(), "%.*Rg", digits, value);
    return buffer.data();
  }

  std::string decimalString(double value)
  {
    char buffer[32];
    std::snprintf(buffer, sizeof(buffer), "%.17g", value);
    return buffer;
  }
}

/**
 * @brief Load shaders and initialize OpenGL resources and the reference orbit.
 * @param x Real part of the center as a decimal string.
 * @param y Imaginary part of the center as a decimal string.
 * @param z Initial zoom factor.
 * @param n Maximum permitted iteration count.
 */
Mandelbrot::Mandelbrot(
    const std::string &x,
    const std::string &y,
    double z,
    int n)
    : centerX(x),
      centerY(y),
      zoom(z),
      iterationLimit(n)
{
  const std::string fullscreen =
      readShader("src/shaders/fullscreen.glsl", "fullscreen.glsl");
  const std::string fragment =
      readShader("src/shaders/mandelbrot.glsl", "mandelbrot.glsl");

  program = createProgram(fullscreen.c_str(), fragment.c_str());

  glGenVertexArrays(1, &vao);

  if (!std::isfinite(zoom) || zoom <= 0.0 || iterationLimit <= 0)
    throw std::invalid_argument("Invalid zoom or iteration limit");

  glGenBuffers(1, &orbitSSBO);

  resolutionLocation = glGetUniformLocation(program, "resolution");
  zoomLocation = glGetUniformLocation(program, "zoom");
  iterationsLocation = glGetUniformLocation(program, "maxIterations");
  centerLocation = glGetUniformLocation(program, "center");
  modeLocation = glGetUniformLocation(program, "renderMode");
  pixelScaleLocation = glGetUniformLocation(program, "pixelScale");
  samplesLocation = glGetUniformLocation(program, "sampleCount");
  paletteLocation = glGetUniformLocation(program, "palette");
  juliaLocation = glGetUniformLocation(program, "juliaMode");
  juliaZeroLocation = glGetUniformLocation(program, "juliaZero");
  juliaDistanceLocation = glGetUniformLocation(program, "juliaDistance");
  juliaParameterLocation = glGetUniformLocation(program, "juliaC");
  escapeRadiusLocation = glGetUniformLocation(program, "escapeRadiusSquared");

  computeReferenceOrbit(iterationBudget());
}

/** @brief Release GPU resources owned by this renderer. */
Mandelbrot::~Mandelbrot()
{
  for (const auto &timing : timings)
    if (timing.query)
      glDeleteQueries(1, &timing.query);
  glDeleteFramebuffers(2, framebuffers);
  glDeleteTextures(2, textures);
  glDeleteBuffers(1, &orbitSSBO);
  glDeleteVertexArrays(1, &vao);
  glDeleteProgram(program);
}

/**
 * @brief Zoom while keeping the supplied cursor point fixed.
 * @param factor Multiplicative zoom change.
 * @param x Horizontal cursor offset at unit zoom.
 * @param y Vertical cursor offset at unit zoom.
 */
void Mandelbrot::zoomBy(double factor, double x, double y)
{
  if (std::isnan(factor) || factor <= 0.0 || !std::isfinite(x) || !std::isfinite(y))
    return;

  const double nextZoom = std::clamp(zoom * factor, 0.1, maximumZoom);
  if (nextZoom == zoom)
    return;

  if (x != 0.0 || y != 0.0)
  {
    mpfr_t cx, cy, scale, delta;
    mpfr_inits2(std::max(orbitPrecision(zoom), orbitPrecision(nextZoom)),
                cx, cy, scale, delta, (mpfr_ptr)0);
    mpfr_set_str(cx, centerX.c_str(), 10, MPFR_RNDN);
    mpfr_set_str(cy, centerY.c_str(), 10, MPFR_RNDN);

    // Shift by cursor * (1 / oldZoom - 1 / newZoom), using MPFR
    // so even deep zooms retain the point underneath the cursor.
    mpfr_set_d(scale, zoom, MPFR_RNDN);
    mpfr_ui_div(scale, 1, scale, MPFR_RNDN);
    mpfr_set_d(delta, nextZoom, MPFR_RNDN);
    mpfr_ui_div(delta, 1, delta, MPFR_RNDN);
    mpfr_sub(scale, scale, delta, MPFR_RNDN);
    mpfr_mul_d(delta, scale, x, MPFR_RNDN);
    mpfr_add(cx, cx, delta, MPFR_RNDN);
    mpfr_mul_d(delta, scale, y, MPFR_RNDN);
    mpfr_add(cy, cy, delta, MPFR_RNDN);

    centerX = decimalString(cx);
    centerY = decimalString(cy);
    viewCenterX = mpfr_get_d(cx, MPFR_RNDN);
    viewCenterY = mpfr_get_d(cy, MPFR_RNDN);
    mpfr_clears(cx, cy, scale, delta, (mpfr_ptr)0);
    orbitDirty = true;
  }

  orbitDirty |= orbitPrecision(nextZoom) > orbitPrecision(zoom);
  zoom = nextZoom;
  ++revision;
}

/**
 * @brief Pan the complex-plane center using MPFR arithmetic.
 * @param x Horizontal offset, scaled by the current zoom.
 * @param y Vertical offset, scaled by the current zoom.
 */
void Mandelbrot::pan(double x, double y)
{
  if (!std::isfinite(x) || !std::isfinite(y) || (x == 0.0 && y == 0.0))
    return;

  mpfr_t cx, cy, delta;
  mpfr_inits2(orbitPrecision(zoom), cx, cy, delta, (mpfr_ptr)0);
  mpfr_set_str(cx, centerX.c_str(), 10, MPFR_RNDN);
  mpfr_set_str(cy, centerY.c_str(), 10, MPFR_RNDN);

  mpfr_set_d(delta, x, MPFR_RNDN);
  mpfr_div_d(delta, delta, zoom, MPFR_RNDN);
  mpfr_add(cx, cx, delta, MPFR_RNDN);
  mpfr_set_d(delta, y, MPFR_RNDN);
  mpfr_div_d(delta, delta, zoom, MPFR_RNDN);
  mpfr_add(cy, cy, delta, MPFR_RNDN);

  centerX = decimalString(cx);
  centerY = decimalString(cy);
  viewCenterX = mpfr_get_d(cx, MPFR_RNDN);
  viewCenterY = mpfr_get_d(cy, MPFR_RNDN);
  mpfr_clears(cx, cy, delta, (mpfr_ptr)0);

  orbitDirty = true;
  ++revision;
}

/**
 * @brief Compute the iteration budget used for both preview and refinement.
 * @return Number of iterations for the current zoom.
 */
int Mandelbrot::iterationBudget() const
{
  if (!automaticIterations)
    return iterationLimit;
  const int detail = static_cast<int>((isJulia() ? 512.0 : 128.0) +
                                      64.0 * std::log2(std::max(1.0, zoom)));
  return std::min(iterationLimit, detail);
}

/** @brief Validate and apply coordinates, zoom and iteration settings together. */
void Mandelbrot::setView(const std::string &x, const std::string &y, double z, int n, bool automatic)
{
  if (!std::isfinite(z) || z < 0.1 || z > maximumZoom)
    throw std::invalid_argument("Zoom must be between 0.1 and 1e100");
  if (n < 1 || n > 1000000)
    throw std::invalid_argument("Iterations must be between 1 and 1000000");

  mpfr_t cx, cy;
  mpfr_inits2(orbitPrecision(z), cx, cy, (mpfr_ptr)0);
  const bool valid = mpfr_set_str(cx, x.c_str(), 10, MPFR_RNDN) == 0 &&
                     mpfr_set_str(cy, y.c_str(), 10, MPFR_RNDN) == 0 &&
                     mpfr_number_p(cx) && mpfr_number_p(cy);
  const double nextX = mpfr_get_d(cx, MPFR_RNDN);
  const double nextY = mpfr_get_d(cy, MPFR_RNDN);
  mpfr_clears(cx, cy, (mpfr_ptr)0);
  if (!valid || !std::isfinite(nextX) || !std::isfinite(nextY))
    throw std::invalid_argument("Coordinates must be finite decimal numbers");

  centerX = x;
  centerY = y;
  viewCenterX = nextX;
  viewCenterY = nextY;
  zoom = z;
  iterationLimit = n;
  automaticIterations = automatic;
  orbitDirty = true;
  ++revision;
}

/** @brief Restore the cached image before drawing interface controls. */
void Mandelbrot::redraw(int width, int height)
{
  if (width <= 0 || height <= 0)
    return;
  if (targetWidth != width || targetHeight != height || !previewWidth)
    draw(width, height, true);
  else if (refinementStarted)
    present(framebuffers[1], width, height, width, height);
  else
    present(framebuffers[0], previewWidth, previewHeight, width, height);
}

/** @brief Select the escape-color palette. */
void Mandelbrot::setPalette(int value)
{
  if (value < 0 || value >= paletteCount)
    throw std::invalid_argument("Invalid palette");
  if (palette == value)
    return;
  palette = value;
  ++revision;
}

/** @brief Update slider values while retaining untouched precise components. */
void Mandelbrot::setJuliaParameter(double x, double y)
{
  setJuliaParameter(x == juliaX ? juliaReal : decimalString(x),
                    y == juliaY ? juliaImaginary : decimalString(y));
}

/** @brief Apply decimal Julia values without reducing them to double precision. */
void Mandelbrot::setJuliaParameter(const std::string &x, const std::string &y)
{
  mpfr_t cx, cy;
  const auto bits = std::max<mpfr_prec_t>(256, 4 * std::max(x.size(), y.size()));
  mpfr_inits2(bits, cx, cy, (mpfr_ptr)0);
  const bool valid = mpfr_set_str(cx, x.c_str(), 10, MPFR_RNDN) == 0 &&
                     mpfr_set_str(cy, y.c_str(), 10, MPFR_RNDN) == 0 &&
                     mpfr_number_p(cx) && mpfr_number_p(cy) &&
                     mpfr_cmp_d(cx, -2.0) >= 0 && mpfr_cmp_d(cx, 2.0) <= 0 &&
                     mpfr_cmp_d(cy, -2.0) >= 0 && mpfr_cmp_d(cy, 2.0) <= 0;
  const double nextX = mpfr_get_d(cx, MPFR_RNDN), nextY = mpfr_get_d(cy, MPFR_RNDN);
  const bool zero = mpfr_zero_p(cx) && mpfr_zero_p(cy);
  mpfr_clears(cx, cy, (mpfr_ptr)0);
  if (!valid)
    throw std::invalid_argument("Julia coordinates must be finite numbers between -2 and 2");
  if (x == juliaReal && y == juliaImaginary && juliaMode)
    return;
  juliaReal = x;
  juliaImaginary = y;
  juliaX = nextX;
  juliaY = nextY;
  juliaParameterZero = zero;
  juliaMode = true;
  orbitDirty = true;
  ++revision;
}

/** @brief Switch fractal modes without changing the selected Julia parameter. */
void Mandelbrot::setJuliaMode(bool enabled)
{
  if (juliaMode == enabled)
    return;
  juliaMode = enabled;
  orbitDirty = true;
  ++revision;
}

/** @brief Preserve distance to the Julia unit circle even at deep zooms. */
void Mandelbrot::updateJuliaUniforms()
{
  glUniform2d(juliaParameterLocation, juliaX, juliaY);
  if (!juliaParameterZero)
    return;
  mpfr_t x, y, distance, square;
  mpfr_inits2(orbitPrecision(zoom), x, y, distance, square, (mpfr_ptr)0);
  mpfr_set_str(x, centerX.c_str(), 10, MPFR_RNDN);
  mpfr_set_str(y, centerY.c_str(), 10, MPFR_RNDN);
  mpfr_mul(distance, x, x, MPFR_RNDN);
  mpfr_mul(square, y, y, MPFR_RNDN);
  mpfr_add(distance, distance, square, MPFR_RNDN);
  mpfr_sub_ui(distance, distance, 1, MPFR_RNDN);
  glUniform2d(centerLocation, mpfr_get_d(x, MPFR_RNDN), mpfr_get_d(y, MPFR_RNDN));
  glUniform1d(juliaDistanceLocation, mpfr_get_d(distance, MPFR_RNDN));
  mpfr_clears(x, y, distance, square, (mpfr_ptr)0);
}

/**
 * @brief Estimate per-pixel GPU work for preview scaling.
 * @return Estimated work in iteration-weighted units.
 */
double Mandelbrot::previewPixelWork() const
{
  return 2.0 * (isJulia() && juliaParameterZero ? 1.0 :
      iterationBudget() * (zoom <= 32.0 ? 1.0 : 4.0));
}

/** @brief Poll completed GPU timer queries and adapt preview/tile sizes. */
void Mandelbrot::collectTimings()
{
  for (auto &timing : timings)
  {
    if (!timing.pending)
      continue;
    GLint available = GL_FALSE;
    glGetQueryObjectiv(timing.query, GL_QUERY_RESULT_AVAILABLE, &available);
    if (!available)
      continue;

    GLuint64 nanoseconds = 0;
    glGetQueryObjectui64v(timing.query, GL_QUERY_RESULT, &nanoseconds);
    timing.pending = false;
    const double ms = std::max(0.01, nanoseconds / 1e6);
    if (timing.preview && targetWidth > 0 && targetHeight > 0)
    {
      const double desired = std::sqrt(timing.pixels * (8.0 / ms) *
                                      (timing.work / previewPixelWork()) /
                                      (double(targetWidth) * targetHeight));
      if (ms > 12.0 || ms < 5.0)
        previewScale = std::clamp(desired, std::max(minimumPreviewScale, previewScale * 0.7),
                                  std::min(0.75, previewScale * 1.3));
    }
    else if (!timing.preview)
    {
      const double desired = timing.pixels * (8.0 / ms);
      tilePixels = static_cast<int>(std::clamp(
          desired, std::max(256.0, tilePixels * 0.7),
          std::min(262144.0, tilePixels * 1.3)));
    }
  }
}

/**
 * @brief Begin a nonblocking GPU timing query, if one is available.
 * @param preview Whether this query measures a preview pass.
 * @param pixels Number of rendered pixels.
 * @return Query identifier, or zero when none is available.
 */
GLuint Mandelbrot::beginTiming(bool preview, int pixels)
{
  for (auto &timing : timings)
  {
    if (timing.pending)
      continue;
    if (!timing.query)
      glGenQueries(1, &timing.query);
    timing.pending = true;
    timing.preview = preview;
    timing.pixels = pixels;
    timing.work = previewPixelWork();
    glBeginQuery(GL_TIME_ELAPSED, timing.query);
    return timing.query;
  }
  return 0;
}

/**
 * @brief Create or resize the two offscreen framebuffer targets.
 * @param width Target width in pixels.
 * @param height Target height in pixels.
 */
void Mandelbrot::ensureTargets(int width, int height)
{
  if (targetWidth == width && targetHeight == height)
    return;
  if (!framebuffers[0])
  {
    glGenFramebuffers(2, framebuffers);
    glGenTextures(2, textures);
  }
  for (int i = 0; i < 2; ++i)
  {
    glBindTexture(GL_TEXTURE_2D, textures[i]);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffers[i]);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                           GL_TEXTURE_2D, textures[i], 0);
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
      throw std::runtime_error("Cannot create fractal render target");
  }
  glBindTexture(GL_TEXTURE_2D, 0);
  glBindFramebuffer(GL_FRAMEBUFFER, 0);
  targetWidth = width;
  targetHeight = height;
  previewWidth = previewHeight = 0;
  refinementStarted = false;
}

/**
 * @brief Blit an offscreen framebuffer to the default framebuffer.
 * @param source Source framebuffer ID.
 * @param sourceWidth Source width.
 * @param sourceHeight Source height.
 * @param width Destination width.
 * @param height Destination height.
 */
void Mandelbrot::present(GLuint source, int sourceWidth, int sourceHeight,
                         int width, int height)
{
  glDisable(GL_SCISSOR_TEST);
  glBindFramebuffer(GL_READ_FRAMEBUFFER, source);
  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
  glBlitFramebuffer(0, 0, sourceWidth, sourceHeight, 0, 0, width, height,
                    GL_COLOR_BUFFER_BIT, GL_LINEAR);
  glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

/**
 * @brief Draw a full frame or an adaptive interactive preview.
 * @param width Output width.
 * @param height Output height.
 * @param interactive Whether to render the scaled interactive preview.
 */
void Mandelbrot::draw(int width, int height, bool interactive)
{
  if (width <= 0 || height <= 0)
    return;

  if (!interactive)
  {
    collectTimings();
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    drawPass(width, height, width, height, iterationBudget(), 2);
    return;
  }

  ensureTargets(width, height);
  const double work = previewPixelWork();
  if (previewWork == 0.0)
    previewScale = std::min(previewScale, std::sqrt(16e6 / (work * width * height)));
  else
    previewScale *= std::sqrt(previewWork / work);
  previewScale = std::clamp(previewScale, minimumPreviewScale, 0.75);
  previewWork = work;
  collectTimings();
  previewWidth = std::max(1, static_cast<int>(width * previewScale));
  previewHeight = std::max(1, static_cast<int>(height * previewScale));
  const auto query = beginTiming(true, previewWidth * previewHeight);
  glBindFramebuffer(GL_FRAMEBUFFER, framebuffers[0]);
  drawPass(width, height, previewWidth, previewHeight, iterationBudget(), 2);
  present(framebuffers[0], previewWidth, previewHeight, width, height);
  if (query)
    glEndQuery(GL_TIME_ELAPSED);
  refinementStarted = false;
  tilePixels = std::min(tilePixels, 32768);
}

/**
 * @brief Refine the preview with full-resolution horizontal strips.
 * @param width Output width.
 * @param height Output height.
 * @return True once all rows are refined.
 */
bool Mandelbrot::refine(int width, int height)
{
  if (width <= 0 || height <= 0)
    return true;
  collectTimings();
  ensureTargets(width, height);
  if (!previewWidth)
    draw(width, height, true);

  if (!refinementStarted)
  {
    glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffers[0]);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, framebuffers[1]);
    glBlitFramebuffer(0, 0, previewWidth, previewHeight, 0, 0, width, height,
                      GL_COLOR_BUFFER_BIT, GL_LINEAR);
    refinedRows = 0;
    refinementStarted = true;
  }
  if (refinedRows >= height)
    return true;

  const int rows = std::min(height - refinedRows, std::max(1, tilePixels / width));
  const auto query = beginTiming(false, width * rows);
  glBindFramebuffer(GL_FRAMEBUFFER, framebuffers[1]);
  glEnable(GL_SCISSOR_TEST);
  glScissor(0, refinedRows, width, rows);
  drawPass(width, height, width, height, iterationBudget(), 2);
  refinedRows += rows;
  present(framebuffers[1], width, height, width, height);
  if (query)
    glEndQuery(GL_TIME_ELAPSED);
  return refinedRows >= height;
}

/**
 * @brief Submit one fractal draw using the selected precision mode.
 * @param width Logical output width.
 * @param height Logical output height.
 * @param renderWidth Actual pass width.
 * @param renderHeight Actual pass height.
 * @param count Iteration limit for this pass.
 * @param samples Shader sample count.
 */
void Mandelbrot::drawPass(int width, int height, int renderWidth, int renderHeight,
                          int count, int samples)
{
  const int mode = zoom <= 32.0 ? 0 : (zoom < 1e8 ? 1 : 2);
  const bool juliaZero = isJulia() && juliaParameterZero;
  if (!juliaZero && mode == 2 && (orbitDirty || (!referenceEscaped && referenceIterations < count)))
    computeReferenceOrbit(count);

  glViewport(0, 0, renderWidth, renderHeight);

  glUseProgram(program);
  glBindVertexArray(vao);

  glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, orbitSSBO);

  glUniform2f(resolutionLocation, float(width), float(height));

  glUniform1d(zoomLocation, zoom);
  glUniform2d(centerLocation, viewCenterX, viewCenterY);
  glUniform1i(paletteLocation, palette);
  glUniform1i(juliaLocation, isJulia());
  glUniform1i(juliaZeroLocation, juliaZero);
  glUniform1d(escapeRadiusLocation, isJulia() ? std::max(4.0, juliaX * juliaX + juliaY * juliaY) : 4.0);
  if (isJulia())
    updateJuliaUniforms();
  glUniform1i(modeLocation, mode);
  glUniform2f(pixelScaleLocation, float(width) / renderWidth, float(height) / renderHeight);
  glUniform1i(samplesLocation, samples);

  glUniform1i(iterationsLocation, count);

  glDrawArrays(GL_TRIANGLES, 0, 3);

  glBindVertexArray(0);
}

/**
 * @brief Compute a high-precision Mandelbrot reference orbit and upload it.
 * @param count Requested number of orbit iterations.
 */
void Mandelbrot::computeReferenceOrbit(int count)
{
  struct OrbitPoint
  {
    double x;
    double y;
  };

  static_assert(sizeof(OrbitPoint) == 16);

  mpfr_prec_t bits = orbitPrecision(zoom);
  // Near the Julia critical point, squaring a pixel-sized offset needs
  // twice the zoom precision before adding the fixed parameter.
  if (isJulia())
    bits = std::max(bits, static_cast<mpfr_prec_t>(std::ceil(2.0 * std::log2(zoom))) + 128);

  mpfr_t cx, cy, zx, zy, nx, ny, a, b;

  mpfr_inits2(bits, cx, cy, zx, zy, nx, ny, a, b, (mpfr_ptr)0);

  bool valid =
      mpfr_set_str(cx, centerX.c_str(), 10, MPFR_RNDN) == 0 &&
      mpfr_set_str(cy, centerY.c_str(), 10, MPFR_RNDN) == 0;

  if (!valid)
  {
    mpfr_clears(cx, cy, zx, zy, nx, ny, a, b, (mpfr_ptr)0);

    throw std::runtime_error("Invalid reference center");
  }

  viewCenterX = mpfr_get_d(cx, MPFR_RNDN);
  viewCenterY = mpfr_get_d(cy, MPFR_RNDN);
  if (isJulia())
  {
    mpfr_set(zx, cx, MPFR_RNDN);
    mpfr_set(zy, cy, MPFR_RNDN);
    mpfr_set_str(cx, juliaReal.c_str(), 10, MPFR_RNDN);
    mpfr_set_str(cy, juliaImaginary.c_str(), 10, MPFR_RNDN);
  }
  else
  {
    mpfr_set_zero(zx, 0);
    mpfr_set_zero(zy, 0);
  }

  std::vector<OrbitPoint> orbit;
  orbit.reserve(count + 1);
  referenceEscaped = false;

  orbit.push_back({mpfr_get_d(zx, MPFR_RNDN), mpfr_get_d(zy, MPFR_RNDN)});
  const double escapeRadius = isJulia() ? std::max(4.0, juliaX * juliaX + juliaY * juliaY) : 4.0;

  for (int i = 0; i < count; ++i)
  {
    mpfr_mul(a, zx, zx, MPFR_RNDN);
    mpfr_mul(b, zy, zy, MPFR_RNDN);
    mpfr_sub(nx, a, b, MPFR_RNDN);
    mpfr_add(nx, nx, cx, MPFR_RNDN);

    mpfr_mul(ny, zx, zy, MPFR_RNDN);
    mpfr_mul_ui(ny, ny, 2, MPFR_RNDN);
    mpfr_add(ny, ny, cy, MPFR_RNDN);

    mpfr_swap(zx, nx);
    mpfr_swap(zy, ny);

    orbit.push_back({mpfr_get_d(zx, MPFR_RNDN),
                     mpfr_get_d(zy, MPFR_RNDN)});

    mpfr_mul(a, zx, zx, MPFR_RNDN);
    mpfr_mul(b, zy, zy, MPFR_RNDN);
    mpfr_add(a, a, b, MPFR_RNDN);
    if (mpfr_cmp_d(a, escapeRadius) > 0)
    {
      referenceEscaped = true;
      break;
    }
  }

  mpfr_clears(cx, cy, zx, zy, nx, ny, a, b, (mpfr_ptr)0);

  glBindBuffer(GL_SHADER_STORAGE_BUFFER, orbitSSBO);

  glBufferData(GL_SHADER_STORAGE_BUFFER, orbit.size() * sizeof(OrbitPoint),
               orbit.data(), GL_DYNAMIC_DRAW);

  glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, orbitSSBO);

  glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0);
  referenceIterations = static_cast<int>(orbit.size()) - 1;
  orbitDirty = false;
}
