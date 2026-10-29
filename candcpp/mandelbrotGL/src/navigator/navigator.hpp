
#pragma once

#include <GLFW/glfw3.h>
#include "../mandelbrot/mandelbrot.hpp"

class Navigator
{
public:
  Navigator(GLFWwindow *window, Mandelbrot &fractal);
  void update(bool captured = false);

private:
  GLFWwindow *window;
  Mandelbrot &fractal;

  double lastX, lastY;
  bool dragging = false;
  bool mouseCaptured = false;

  static void scroll(GLFWwindow *window, double dx, double dy);
};
