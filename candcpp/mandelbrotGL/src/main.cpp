/**
 * @file main.cpp
 * @brief Main entry point for the application.
 *
 * mandelbrotGL is an OpenGL application for rendering the Mandelbrot set.
 * It uses GLFW for window management and GLAD for loading OpenGL functions.
 */

// Libraries
#include <iostream>
#include <exception>

// Dependencies
#include "init.hpp"
#include "render.hpp"
#include "navigator/navigator.hpp"
#include "mandelbrot/mandelbrot.hpp"
#include "interface/interface.hpp"

int main()
{
  GLFWwindow *window = init();

  if (!window)
  {
    std::cerr << "Failed to initialize OpenGL\n";
    return -1;
  }

  int result = 0;

  try
  {
    Mandelbrot fractal("-0.5", "0.0", 1.0, 32768);
    Navigator navigator(window, fractal);
    Interface interface(window, fractal);

    result = render(window, navigator, fractal, interface);
  }
  catch (const std::exception &e)
  {
    std::cerr << e.what() << '\n';
    result = -1;
  }

  glfwSetScrollCallback(window, nullptr);
  glfwSetWindowUserPointer(window, nullptr);
  glfwDestroyWindow(window);
  glfwTerminate();

  return result;
}
