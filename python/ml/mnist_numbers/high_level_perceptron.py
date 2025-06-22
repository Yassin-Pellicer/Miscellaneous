from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
import numpy as np

# Load dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Normalize and reshape
x_train = x_train / 255.0
x_test = x_test / 255.0

# One-hot encoding
y_train_oh = to_categorical(y_train, 10)
y_test_oh = to_categorical(y_test, 10)

# Build model
model = Sequential([
    Flatten(input_shape=(28, 28)),      # Flatten 28x28 to 784
    Dense(128, activation='relu'),      # Hidden layer
    Dense(10, activation='softmax')     # Output layer
])

# Compile model
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Train model
model.fit(x_train, y_train_oh, epochs=10, batch_size=16)

# Evaluate on test set
test_loss, test_acc = model.evaluate(x_test, y_test_oh)
print(f"Test Accuracy: {test_acc:.4f}")

# Save weights
model.save_weights(".weights.h5")
