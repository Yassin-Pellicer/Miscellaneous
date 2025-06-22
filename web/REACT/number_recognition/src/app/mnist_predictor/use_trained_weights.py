from PIL import Image, ImageOps
import numpy as np
import os
import sys

# Load trained weights
weights_path = os.path.join(os.path.dirname(__file__), "weights.npz")
data = np.load(weights_path)
W1 = data["W1"]
b1 = data["b1"]
W2 = data["W2"]
b2 = data["b2"]

def image_to_mnist_format(path_to_image):
    """Convert image to MNIST format (28x28 grayscale, normalized)"""
    try:
        # Load image
        img = Image.open(path_to_image)
        
        # Convert to grayscale
        img = img.convert("L")
        
        # Resize to 28x28
        img = img.resize((28, 28), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Invert if background is white (common for drawn digits)
        # Check if the background (corners) are predominantly white
        corners = [img_array[0,0], img_array[0,-1], img_array[-1,0], img_array[-1,-1]]
        if np.mean(corners) > 127:  # Background is light, invert
            img_array = 255 - img_array
        
        # Normalize to [0, 1]
        img_array = img_array.astype(np.float32) / 255.0
        
        # Flatten for neural network input
        img_flat = img_array.flatten()
        
        return img_array, img_flat
    except Exception as e:
        print(f"Error processing image: {e}", file=sys.stderr)
        sys.exit(1)

def relu(x):
    """ReLU activation function"""
    return np.maximum(0, x)

def softmax(x):
    """Softmax activation function"""
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

def predict(x):
    """Make prediction using trained neural network"""
    # Forward pass
    z1 = np.dot(x, W1) + b1
    a1 = relu(z1)
    z2 = np.dot(a1, W2) + b2
    a2 = softmax(z2)
    return np.argmax(a2, axis=1), a2

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python use_trained_weights.py <image_path>", file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Process image
        mnist_img, mnist_flat = image_to_mnist_format(image_path)
        
        # Make prediction
        prediction, probabilities = predict(mnist_flat.reshape(1, -1))
        
        # Output result
        print(f"Predicted class: {prediction[0]}")
        
        # Optional: print confidence scores
        confidence = np.max(probabilities[0]) * 100
        print(f"Confidence: {confidence:.1f}%", file=sys.stderr)
        
    except Exception as e:
        print(f"Prediction error: {e}", file=sys.stderr)
        sys.exit(1)