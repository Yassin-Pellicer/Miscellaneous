from PIL import Image, ImageOps
import numpy as np

data = np.load("weights.npz")
W1 = data["W1"]
b1 = data["b1"]
W2 = data["W2"]
b2 = data["b2"]

def image_to_mnist_format(path_to_image):
  # Load image
  img = Image.open(path_to_image)

  # Convert to grayscale
  img = img.convert("L")  # 'L' mode = (8-bit pixels, black and white)

  # Invert colors if needed (MNIST digits are white on black)
  img = ImageOps.invert(img)

  # Resize to 28x28
  img = img.resize((28, 28))

  # Convert to NumPy array and normalize to [0, 1]
  img_array = np.array(img) / 255.0

  # Flatten to 1D if needed
  img_flat = img_array.flatten()

  return img_array, img_flat

mnist_img, mnist_flat = image_to_mnist_format("image.png")

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

def predict(x):
  z1 = np.dot(x, W1) + b1
  a1 = relu(z1)
  z2 = np.dot(a1, W2) + b2
  a2 = softmax(z2)
  return np.argmax(a2, axis=1)

# If you're using your model:
prediction = predict(mnist_flat.reshape(1, -1))
print("Predicted class:", prediction[0])


