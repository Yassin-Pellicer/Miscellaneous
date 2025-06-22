from tensorflow.keras.datasets import mnist
import numpy as np 

# Load MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Reshape the data to be 1 dimensional
x_train = x_train.reshape(-1, 28*28) / 255.0
x_test = x_test.reshape(-1, 28*28) / 255.0

# Create a helper function to convert a number to a one-hot vector
def one_hot(y, num_classes=10):
    return np.eye(num_classes)[y]

# Convert the training data to one-hot vectors
y_train_oh = one_hot(y_train)

# Convert the test data to one-hot vectors
y_test_oh = one_hot(y_test)


np.random.seed(42)

input_size = 784
hidden_size = 128
output_size = 10

# Weight initialization
W1 = np.random.randn(input_size, hidden_size) * 0.01
b1 = np.zeros((1, hidden_size))
W2 = np.random.randn(hidden_size, output_size) * 0.01
b2 = np.zeros((1, output_size))

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

def softmax(x):
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)

def cross_entropy(y_pred, y_true):
    m = y_true.shape[0]
    loss = -np.sum(y_true * np.log(y_pred + 1e-9)) / m
    return loss

def train(x, y, epochs=50, lr=0.001, batch_size=16):
    global W1, b1, W2, b2
    m = x.shape[0]
    
    for epoch in range(epochs):
        permutation = np.random.permutation(m)
        x = x[permutation]
        y = y[permutation]
        
        for i in range(0, m, batch_size):
            x_batch = x[i:i+batch_size]
            y_batch = y[i:i+batch_size]

            # Forward pass
            z1 = np.dot(x_batch, W1) + b1
            a1 = relu(z1)
            z2 = np.dot(a1, W2) + b2
            a2 = softmax(z2)

            # Loss (optional to track)
            loss = cross_entropy(a2, y_batch)

            # Backward pass
            dz2 = a2 - y_batch
            dW2 = np.dot(a1.T, dz2) / batch_size
            db2 = np.sum(dz2, axis=0, keepdims=True) / batch_size

            dz1 = np.dot(dz2, W2.T) * relu_derivative(z1)
            dW1 = np.dot(x_batch.T, dz1) / batch_size
            db1 = np.sum(dz1, axis=0, keepdims=True) / batch_size

            # Gradient descent update
            W2 -= lr * dW2
            b2 -= lr * db2
            W1 -= lr * dW1
            b1 -= lr * db1

        print(f"Epoch {epoch+1}, Loss: {loss:.4f}")

def predict(x):
    z1 = np.dot(x, W1) + b1
    a1 = relu(z1)
    z2 = np.dot(a1, W2) + b2
    a2 = softmax(z2)
    return np.argmax(a2, axis=1)

def accuracy(x, y_true):
    y_pred = predict(x)
    return np.mean(y_pred == y_true)

train(x_train, y_train_oh, epochs=50, lr=0.001)
print("Test Accuracy:", accuracy(x_test, y_test))

np.savez("weights.npz", W1=W1, b1=b1, W2=W2, b2=b2)
