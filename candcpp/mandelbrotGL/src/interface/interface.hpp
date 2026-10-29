#pragma once

#include <string>

struct GLFWwindow;
class Mandelbrot;

class Interface
{
public:
  Interface(GLFWwindow *window, Mandelbrot &fractal);
  ~Interface();

  void update();
  void draw();
  bool capturesMouse() const;

private:
  void synchronize();

  Mandelbrot &fractal;
  std::string x, y, error;
  double zoom;
  int iterations;
  bool automatic;
  bool editing = false;
};
