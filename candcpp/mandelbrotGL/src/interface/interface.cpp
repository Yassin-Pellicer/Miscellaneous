/**
 * @file interface.cpp
 * @brief Controls for the Mandelbrot view and iteration count.
 */

// Libraries
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <misc/cpp/imgui_stdlib.h>
#include <stdexcept>

// Dependencies
#include "interface.hpp"
#include "../mandelbrot/mandelbrot.hpp"

/** @brief Initialize the GLFW and OpenGL interface backends. */
Interface::Interface(GLFWwindow *window, Mandelbrot &fractal)
    : fractal(fractal)
{
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGui::GetIO().IniFilename = nullptr;
  ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;
  ImGui::StyleColorsDark();

  if (!ImGui_ImplGlfw_InitForOpenGL(window, true))
  {
    ImGui::DestroyContext();
    throw std::runtime_error("Cannot initialize interface input");
  }
  if (!ImGui_ImplOpenGL3_Init("#version 430 core"))
  {
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    throw std::runtime_error("Cannot initialize interface renderer");
  }
  synchronize();
  synchronizeJulia();
}

/** @brief Release interface resources and restore GLFW callbacks. */
Interface::~Interface()
{
  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplGlfw_Shutdown();
  ImGui::DestroyContext();
}

/** @brief Copy the current view without rounding the center coordinates. */
void Interface::synchronize()
{
  x = fractal.getCenterX();
  y = fractal.getCenterY();
  zoom = fractal.getZoom();
  iterations = fractal.getIterationLimit();
  automatic = fractal.getAutomaticIterations();
  editing = false;
  error.clear();
}

/** @brief Copy the exact Julia parameter into the input fields. */
void Interface::synchronizeJulia()
{
  juliaReal = fractal.getJuliaReal();
  juliaImaginary = fractal.getJuliaImaginary();
  editingJulia = false;
  juliaError.clear();
}

/** @brief Build controls and apply validated view changes. */
void Interface::update()
{
  if (!editing)
    synchronize();
  if (!editingJulia)
    synchronizeJulia();

  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplGlfw_NewFrame();
  ImGui::NewFrame();
  ImGui::SetNextWindowPos(ImVec2(12, 12), ImGuiCond_FirstUseEver);
  ImGui::SetNextWindowSize(ImVec2(360, 0), ImGuiCond_FirstUseEver);

  if (ImGui::Begin("Mandelbrot controls", nullptr, ImGuiWindowFlags_AlwaysAutoResize))
  {
    editing |= ImGui::InputText("Real", &x);
    editing |= ImGui::InputText("Imaginary", &y);
    editing |= ImGui::InputDouble("Zoom", &zoom, 0, 0, "%.6e");
    editing |= ImGui::Checkbox("Automatic iterations", &automatic);
    editing |= ImGui::InputInt(automatic ? "Iteration limit" : "Iterations", &iterations, 1, 100);
    ImGui::Text("Active iterations: %d", fractal.getIterations());

    if (ImGui::Button("Apply"))
    {
      try
      {
        fractal.setView(x, y, zoom, iterations, automatic);
        synchronize();
      }
      catch (const std::exception &e)
      {
        error = e.what();
        editing = true;
      }
    }
    ImGui::SameLine();
    if (ImGui::Button("Current view"))
      synchronize();
    ImGui::SameLine();
    if (ImGui::Button("Reset view"))
    {
      fractal.setView(fractal.isJulia() ? "0" : "-0.5", "0", 1.0,
                      fractal.getIterationLimit(), fractal.getAutomaticIterations());
      synchronize();
    }
    if (!error.empty())
      ImGui::TextWrapped("%s", error.c_str());

    ImGui::Separator();
    int palette = fractal.getPalette();
    if (ImGui::Combo("Palette", &palette,
                     "Classic\0Ocean\0Fire\0Monochrome\0Sunset\0Forest\0Ice\0Neon\0"
                     "Gold\0Purple\0Candy\0Rainbow\0"))
      fractal.setPalette(palette);

    bool julia = fractal.isJulia();
    if (ImGui::Checkbox("Julia mode", &julia))
      fractal.setJuliaMode(julia);
    editingJulia |= ImGui::InputText("c real", &juliaReal);
    editingJulia |= ImGui::InputText("c imaginary", &juliaImaginary);
    if (ImGui::Button("Apply c"))
    {
      try
      {
        fractal.setJuliaParameter(juliaReal, juliaImaginary);
        synchronizeJulia();
      }
      catch (const std::exception &e)
      {
        juliaError = e.what();
        editingJulia = true;
      }
    }
    ImGui::SameLine();
    if (ImGui::Button("Reset c"))
    {
      fractal.setJuliaParameter("0", "0");
      synchronizeJulia();
    }
    if (!juliaError.empty())
      ImGui::TextWrapped("%s", juliaError.c_str());
    double juliaX = fractal.getJuliaX(), juliaY = fractal.getJuliaY();
    const double minimum = -2.0, maximum = 2.0;
    bool changed = ImGui::SliderScalar("Julia c X", ImGuiDataType_Double, &juliaX,
                                       &minimum, &maximum, "%.3f", ImGuiSliderFlags_AlwaysClamp);
    changed |= ImGui::SliderScalar("Julia c Y", ImGuiDataType_Double, &juliaY,
                                    &minimum, &maximum, "%.3f", ImGuiSliderFlags_AlwaysClamp);
    if (changed)
    {
      fractal.setJuliaParameter(juliaX, juliaY);
      synchronizeJulia();
    }
  }
  ImGui::End();
}

/** @brief Draw controls over the cached fractal image. */
void Interface::draw()
{
  ImGui::Render();
  ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

/** @brief Report whether the interface owns mouse input. */
bool Interface::capturesMouse() const
{
  return ImGui::GetIO().WantCaptureMouse;
}
