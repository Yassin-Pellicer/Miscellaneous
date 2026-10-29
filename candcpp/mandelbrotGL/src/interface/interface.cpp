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

/** @brief Build controls and apply validated view changes. */
void Interface::update()
{
  if (!editing)
    synchronize();

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
    if (!error.empty())
      ImGui::TextWrapped("%s", error.c_str());
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
