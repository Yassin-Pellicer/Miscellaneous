/**
 * @file render.cpp
 * @brief Implementation of the render function for the Mandelbrot application.
 */

// Libraries
#include <glad/gl.h>
#include <GLFW/glfw3.h>
#include <algorithm>
#include <limits>

// Dependencies
#include "mandelbrot/mandelbrot.hpp"
#include "navigator/navigator.hpp"
#include "interface/interface.hpp"
#include "render.hpp"

int render(GLFWwindow *window, Navigator &navigator, Mandelbrot &fractal, Interface &interface)
{
  glfwSwapInterval(1);
  constexpr double settleDelay = 0.12;
  auto renderedRevision = std::numeric_limits<std::uint64_t>::max();
  int previousWidth = -1;
  int previousHeight = -1;
  double lastInput = 0.0;
  bool refining = false;

  while (!glfwWindowShouldClose(window))
  {
    glfwPollEvents();
    if (glfwWindowShouldClose(window))
      break;
    interface.update();
    navigator.update(interface.capturesMouse());

    int width, height;
    glfwGetFramebufferSize(window, &width, &height);

    const auto revision = fractal.viewRevision();
    const bool changed = revision != renderedRevision ||
                         width != previousWidth || height != previousHeight;
    const double now = glfwGetTime();

    if (changed)
    {
      lastInput = now;
      refining = width > 0 && height > 0;
      if (refining)
      {
        fractal.draw(width, height, true);
      }
      renderedRevision = revision;
      previousWidth = width;
      previousHeight = height;
    }
    else if (refining && now - lastInput >= settleDelay)
    {
      // Refine a bounded tile, then process input before submitting more.
      refining = !fractal.refine(width, height);
    }
    else
      fractal.redraw(width, height);

    interface.draw();
    if (width > 0 && height > 0)
      glfwSwapBuffers(window);

    if (glfwWindowShouldClose(window))
      break;
    if (!refining)
      glfwWaitEventsTimeout(0.05);
    else if (glfwGetTime() - lastInput < settleDelay)
      glfwWaitEventsTimeout(std::min(0.05, std::max(0.001, settleDelay - (glfwGetTime() - lastInput))));
  }

  return 0;
}
