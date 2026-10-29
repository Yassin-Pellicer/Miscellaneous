
/**
 * @file navigator.cpp
 * @brief Implementation of the Navigator class for handling user input and navigation.
 *
 * This file contains the implementation of the Navigator class, which is responsible for
 * handling mouse input and updating the view of the Mandelbrot set.
 */

 // Libraries
#include <cmath>

// Dependencies
#include "navigator.hpp"

Navigator::Navigator(GLFWwindow *window, Mandelbrot &fractal)
    : window(window), fractal(fractal)
{
  glfwGetCursorPos(window, &lastX, &lastY);
  glfwSetWindowUserPointer(window, this);
  glfwSetScrollCallback(window, scroll);
}

void Navigator::scroll(GLFWwindow *window, double, double dy)
{
  auto *nav = static_cast<Navigator *>(glfwGetWindowUserPointer(window));
  if (nav->mouseCaptured)
    return;

  double x, y;
  int width, height, framebufferWidth, framebufferHeight;
  glfwGetWindowSize(window, &width, &height);
  glfwGetFramebufferSize(window, &framebufferWidth, &framebufferHeight);
  if (width <= 0 || height <= 0 || framebufferWidth <= 0 || framebufferHeight <= 0)
    return;
  glfwGetCursorPos(window, &x, &y);

  nav->fractal.zoomBy(
      std::pow(1.1, dy),
      3.0 * (x / width - 0.5) * framebufferWidth / framebufferHeight,
      3.0 * (0.5 - y / height));
}

void Navigator::update(bool captured)
{
  mouseCaptured = captured;
  double x, y;
  int width, height;

  glfwGetCursorPos(window, &x, &y);
  glfwGetWindowSize(window, &width, &height);

  bool pressed = !captured && glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_LEFT) == GLFW_PRESS;

  if (pressed && dragging && height > 0)
  {
    fractal.pan(-3.0 * (x - lastX) / height,
                3.0 * (y - lastY) / height);
  }

  dragging = pressed;
  lastX = x;
  lastY = y;
}
