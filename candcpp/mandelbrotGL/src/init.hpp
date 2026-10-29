#pragma once

#include <glad/gl.h>
#include <GLFW/glfw3.h>

int gl_init();
GLFWwindow *create_window();
int load_context(GLFWwindow *window);
GLFWwindow *init();

GLuint compileShader(GLenum type, const char *source);
GLuint createProgram(const char *vertex, const char *fragment);
