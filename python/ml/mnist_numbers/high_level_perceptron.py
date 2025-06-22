import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.datasets import mnist
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def load_and_preprocess_data():
    """Load and preprocess MNIST dataset"""
    # Load the data
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # Normalize pixel values to [0, 1]
    x_train = x_train.astype('float32') / 255.0
    x_test = x_test.astype('float32') / 255.0
    
    # Reshape for CNN (add channel dimension)
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
    
    # Convert labels to categorical one-hot encoding
    y_train = to_categorical(y_train, 10)
    y_test = to_categorical(y_test, 10)
    
    print(f"Training data shape: {x_train.shape}")
    print(f"Training labels shape: {y_train.shape}")
    print(f"Test data shape: {x_test.shape}")
    print(f"Test labels shape: {y_test.shape}")
    
    return (x_train, y_train), (x_test, y_test)

def create_cnn_model():
    """Create a high-performance CNN model for MNIST"""
    model = keras.Sequential([
        # First convolutional block
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Second convolutional block
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Third convolutional block
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.25),
        
        # Flatten and dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(10, activation='softmax')
    ])
    
    return model

def create_simple_model():
    """Create a simpler but still effective model"""
    model = keras.Sequential([
        layers.Flatten(input_shape=(28, 28, 1)),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(10, activation='softmax')
    ])
    
    return model

def plot_training_history(history):
    """Plot training history"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot training & validation accuracy
    ax1.plot(history.history['accuracy'], label='Training Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Validation Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Plot training & validation loss
    ax2.plot(history.history['loss'], label='Training Loss')
    ax2.plot(history.history['val_loss'], label='Validation Loss')
    ax2.set_title('Model Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

def save_weights_npz(model, filename="mnist_weights.npz"):
    """Save model weights in .npz format"""
    weights = model.get_weights()
    
    # Create dictionary for all weights
    weight_dict = {}
    
    # Save weights and biases with descriptive names
    layer_count = 0
    for i in range(0, len(weights), 2):
        if i+1 < len(weights):
            layer_count += 1
            weight_dict[f'W{layer_count}'] = weights[i]    # Weight matrix
            weight_dict[f'b{layer_count}'] = weights[i+1]  # Bias vector
    
    # Save to .npz file
    np.savez(filename, **weight_dict)
    print(f"Saved {len(weight_dict)} weight arrays to {filename}")
    
    # Print weight shapes for verification
    print("Weight shapes:")
    for key, value in weight_dict.items():
        print(f"  {key}: {value.shape}")
    
    return filename

def load_weights_npz(filename="mnist_weights.npz"):
    """Load and display weights from .npz file"""
    try:
        data = np.load(filename)
        print(f"\nLoaded weights from {filename}:")
        for key in data.files:
            print(f"  {key}: shape {data[key].shape}")
        return data
    except FileNotFoundError:
        print(f"File {filename} not found!")
        return None

def main():
    """Main training function"""
    print("Loading and preprocessing MNIST data...")
    (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
    
    # Choose model type
    model_type = input("Choose model type (1 for CNN, 2 for Simple): ").strip()
    
    if model_type == "1":
        print("Creating CNN model...")
        model = create_cnn_model()
        epochs = 50
        batch_size = 128
    else:
        print("Creating simple model...")
        model = create_simple_model()
        epochs = 100
        batch_size = 128
    
    # Compile the model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Print model summary
    model.summary()
    
    # Define callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=0.0001,
            verbose=1
        )
    ]
    
    # Train the model
    print("Training model...")
    history = model.fit(
        x_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_data=(x_test, y_test),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate the model
    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nTest accuracy: {test_accuracy:.4f}")
    print(f"Test loss: {test_loss:.4f}")
    
    # Plot training history
    plot_training_history(history)
    
    # Save the model in multiple formats
    model.save('mnist_model.h5')
    print("Model saved as 'mnist_model.h5'")
    
    # Save weights in .npz format
    npz_filename = save_weights_npz(model, "mnist_weights.npz")
    
    # Demonstrate loading the weights
    loaded_weights = load_weights_npz(npz_filename)
    
    # Make some predictions
    predictions = model.predict(x_test[:5])
    predicted_classes = np.argmax(predictions, axis=1)
    actual_classes = np.argmax(y_test[:5], axis=1)
    
    print("\nSample predictions:")
    for i in range(5):
        print(f"Image {i+1}: Predicted={predicted_classes[i]}, Actual={actual_classes[i]}")
    
    return model, history

if __name__ == "__main__":
    model, history = main()