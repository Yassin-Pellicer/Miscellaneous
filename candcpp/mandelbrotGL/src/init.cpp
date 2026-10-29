
// Libraries
#include <glad/gl.h>
#include <GLFW/glfw3.h>
#include <stdexcept>
#include <utility>
#include <iostream>

/**
 * Initialize GLFW and configure OpenGL.
 * @return 0 on success, -1 on failure
 */
int gl_init()
{
  if (!glfwInit())
  {
    std::cerr << "Failed to initialize GLFW\n";
    return -1;
  }
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE,
                 GLFW_OPENGL_CORE_PROFILE);
  return 0;
}

/**
 * Create an OpenGL window.
 * @return Window pointer or nullptr on failure
 */
GLFWwindow *create_window()
{
  GLFWwindow *window = glfwCreateWindow(
      800, 600,
      "My OpenGL Project",
      nullptr, nullptr);

  if (!window)
  {
    std::cerr << "Failed to create window\n";
    return nullptr;
  }

  return window;
}

/**
 * Activate OpenGL context and initialize GLAD.
 * @return 0 on success, -1 on failure
 */
int load_context(GLFWwindow *window)
{
  if (!window)
  {
    std::cerr << "Invalid window pointer\n";
    return -1;
  }

  glfwMakeContextCurrent(window);

  if (!gladLoadGL((GLADloadfunc)glfwGetProcAddress))
  {
    std::cerr << "Failed to load GLAD\n";
    return -1;
  }

  return 0;
}

/**
 * Initialize GLFW, create a window, and load OpenGL.
 * @return Window pointer or nullptr on failure
 */
GLFWwindow *init()
{
  if (gl_init() != 0)
  {
    return nullptr;
  }

  GLFWwindow *window = create_window();

  if (!window)
  {
    glfwTerminate();
    return nullptr;
  }

  if (load_context(window) != 0)
  {
    glfwDestroyWindow(window);
    glfwTerminate();
    return nullptr;
  }

  return window;
}

/**
 * Compile a shader from source code.
 * @param type Shader type (GL_VERTEX_SHADER or GL_FRAGMENT_SHADER)
 * @param source Shader source code
 * @return Compiled shader ID
 * @throws std::runtime_error on compilation failure
 */
GLuint compileShader(GLenum type, const char *source)
{
  GLuint shader = glCreateShader(type);
  glShaderSource(shader, 1, &source, nullptr);
  glCompileShader(shader);

  GLint success;
  glGetShaderiv(shader, GL_COMPILE_STATUS, &success);

  if (!success)
  {
    char log[1024];
    glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
    glDeleteShader(shader);
    throw std::runtime_error(log);
  }

  return shader;
}

/**
 * Create an OpenGL program from vertex and fragment shaders.
 * @param vertex Vertex shader source code
 * @param fragment Fragment shader source code
 * @return Program ID
 * @throws std::runtime_error on linking failure
 */
GLuint createProgram(const char *vertex, const char *fragment)
{
  GLuint program = glCreateProgram();

  try
  {
    for (auto [type, source] : {
             std::pair<GLenum, const char *>{GL_VERTEX_SHADER, vertex},
             std::pair<GLenum, const char *>{GL_FRAGMENT_SHADER, fragment}})
    {
      GLuint shader = compileShader(type, source);
      glAttachShader(program, shader);
      glDeleteShader(shader);
    }

    glLinkProgram(program);

    GLint success;
    glGetProgramiv(program, GL_LINK_STATUS, &success);

    if (!success)
    {
      char log[1024];
      glGetProgramInfoLog(program, sizeof(log), nullptr, log);
      throw std::runtime_error(log);
    }
  }
  catch (...)
  {
    glDeleteProgram(program);
    throw;
  }

  return program;
}
