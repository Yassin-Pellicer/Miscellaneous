#pragma once

#include <GLFW/glfw3.h>

class Navigator;
class Mandelbrot;
class Interface;

int render(GLFWwindow *window, Navigator &navigator, Mandelbrot &fractal, Interface &interface);
