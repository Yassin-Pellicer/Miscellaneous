import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

class NeuralNetwork:
    def __init__(self, input_size=784, hidden_sizes=[128, 64], output_size=10, random_seed=42):
        """
        Initialize a multi-layer neural network with customizable architecture.
        
        Args:
            input_size: Number of input features
            hidden_sizes: List of hidden layer sizes
            output_size: Number of output classes
            random_seed: Random seed for reproducibility
        """
        np.random.seed(random_seed)
        self.layers = []
        
        # Build network architecture
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        
        for i in range(len(layer_sizes) - 1):
            # Xavier/Glorot initialization for better gradient flow
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            limit = np.sqrt(6 / (fan_in + fan_out))
            
            W = np.random.uniform(-limit, limit, (fan_in, fan_out))
            b = np.zeros((1, fan_out))
            
            self.layers.append({'W': W, 'b': b})
        
        # Training history
        self.history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU"""
        return (x > 0).astype(float)
    
    def softmax(self, x):
        """Softmax activation function with numerical stability"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def cross_entropy_loss(self, y_pred, y_true):
        """Cross-entropy loss with numerical stability"""
        m = y_true.shape[0]
        # Clip predictions to prevent log(0)
        y_pred_clipped = np.clip(y_pred, 1e-12, 1 - 1e-12)
        loss = -np.sum(y_true * np.log(y_pred_clipped)) / m
        return loss
    
    def forward_pass(self, x):
        """Forward propagation through the network"""
        activations = [x]
        z_values = []
        
        for i, layer in enumerate(self.layers):
            z = np.dot(activations[-1], layer['W']) + layer['b']
            z_values.append(z)
            
            if i < len(self.layers) - 1:  # Hidden layers use ReLU
                a = self.relu(z)
            else:  # Output layer uses softmax
                a = self.softmax(z)
            
            activations.append(a)
        
        return activations, z_values
    
    def backward_pass(self, activations, z_values, y_true):
        """Backward propagation to compute gradients"""
        m = y_true.shape[0]
        gradients = []
        
        # Output layer gradient
        dz = activations[-1] - y_true
        
        for i in reversed(range(len(self.layers))):
            dW = np.dot(activations[i].T, dz) / m
            db = np.sum(dz, axis=0, keepdims=True) / m
            
            gradients.append({'dW': dW, 'db': db})
            
            if i > 0:  # Not the first layer
                dz = np.dot(dz, self.layers[i]['W'].T) * self.relu_derivative(z_values[i-1])
        
        return list(reversed(gradients))
    
    def update_weights(self, gradients, learning_rate):
        """Update weights using gradient descent"""
        for i, grad in enumerate(gradients):
            self.layers[i]['W'] -= learning_rate * grad['dW']
            self.layers[i]['b'] -= learning_rate * grad['db']
    
    def predict(self, x):
        """Make predictions"""
        activations, _ = self.forward_pass(x)
        return np.argmax(activations[-1], axis=1)
    
    def predict_proba(self, x):
        """Get prediction probabilities"""
        activations, _ = self.forward_pass(x)
        return activations[-1]
    
    def accuracy(self, x, y_true):
        """Calculate accuracy"""
        y_pred = self.predict(x)
        return np.mean(y_pred == y_true)
    
    def train(self, x_train, y_train, x_val=None, y_val=None, epochs=50, 
              learning_rate=0.001, batch_size=128, verbose=True):
        """
        Train the neural network with improved features
        
        Args:
            x_train, y_train: Training data
            x_val, y_val: Validation data (optional)
            epochs: Number of training epochs
            learning_rate: Learning rate with decay
            batch_size: Mini-batch size
            verbose: Whether to print progress
        """
        m = x_train.shape[0]
        initial_lr = learning_rate
        
        for epoch in range(epochs):
            # Learning rate decay
            current_lr = initial_lr * (0.95 ** (epoch // 10))
            
            # Shuffle training data
            indices = np.random.permutation(m)
            x_train_shuffled = x_train[indices]
            y_train_shuffled = y_train[indices]
            
            epoch_losses = []
            
            # Mini-batch training
            for i in range(0, m, batch_size):
                x_batch = x_train_shuffled[i:i+batch_size]
                y_batch = y_train_shuffled[i:i+batch_size]
                
                # Forward pass
                activations, z_values = self.forward_pass(x_batch)
                
                # Calculate loss
                loss = self.cross_entropy_loss(activations[-1], y_batch)
                epoch_losses.append(loss)
                
                # Backward pass
                gradients = self.backward_pass(activations, z_values, y_batch)
                
                # Update weights
                self.update_weights(gradients, current_lr)
            
            # Record training metrics
            avg_loss = np.mean(epoch_losses)
            train_acc = self.accuracy(x_train, np.argmax(y_train, axis=1))
            
            self.history['train_loss'].append(avg_loss)
            self.history['train_acc'].append(train_acc)
            
            # Validation metrics
            if x_val is not None and y_val is not None:
                val_activations, _ = self.forward_pass(x_val)
                val_loss = self.cross_entropy_loss(val_activations[-1], y_val)
                val_acc = self.accuracy(x_val, np.argmax(y_val, axis=1))
                
                self.history['val_loss'].append(val_loss)
                self.history['val_acc'].append(val_acc)
                
                if verbose and epoch % 5 == 0:
                    print(f"Epoch {epoch+1:3d}: Loss={avg_loss:.4f}, Acc={train_acc:.4f}, "
                          f"Val_Loss={val_loss:.4f}, Val_Acc={val_acc:.4f}, LR={current_lr:.5f}")
            else:
                if verbose and epoch % 5 == 0:
                    print(f"Epoch {epoch+1:3d}: Loss={avg_loss:.4f}, Acc={train_acc:.4f}, LR={current_lr:.5f}")
    
    def plot_training_history(self):
        """Plot training history"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Loss plot
        ax1.plot(self.history['train_loss'], label='Training Loss')
        if self.history['val_loss']:
            ax1.plot(self.history['val_loss'], label='Validation Loss')
        ax1.set_title('Training History - Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy plot
        ax2.plot(self.history['train_acc'], label='Training Accuracy')
        if self.history['val_acc']:
            ax2.plot(self.history['val_acc'], label='Validation Accuracy')
        ax2.set_title('Training History - Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()

def load_and_preprocess_data():
    """Load and preprocess MNIST data with train/validation split"""
    # Load MNIST dataset
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # Normalize pixel values to [0, 1]
    x_train = x_train.reshape(-1, 28*28).astype(np.float32) / 255.0
    x_test = x_test.reshape(-1, 28*28).astype(np.float32) / 255.0
    
    # Create validation set from training data
    val_size = 10000
    x_val = x_train[-val_size:]
    y_val = y_train[-val_size:]
    x_train = x_train[:-val_size]
    y_train = y_train[:-val_size]
    
    # One-hot encode labels
    def one_hot(y, num_classes=10):
        return np.eye(num_classes)[y]
    
    y_train_oh = one_hot(y_train)
    y_val_oh = one_hot(y_val)
    y_test_oh = one_hot(y_test)
    
    return (x_train, y_train, y_train_oh), (x_val, y_val, y_val_oh), (x_test, y_test, y_test_oh)

def evaluate_model(model, x_test, y_test, y_test_oh):
    """Comprehensive model evaluation"""
    # Predictions
    y_pred = model.predict(x_test)
    test_acc = model.accuracy(x_test, y_test)
    
    print(f"Test Accuracy: {test_acc:.4f}")
    
    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()
    
    return test_acc

def visualize_predictions(model, x_test, y_test, num_samples=16):
    """Visualize model predictions"""
    indices = np.random.choice(len(x_test), num_samples, replace=False)
    
    fig, axes = plt.subplots(4, 4, figsize=(12, 12))
    axes = axes.ravel()
    
    for i, idx in enumerate(indices):
        image = x_test[idx].reshape(28, 28)
        true_label = y_test[idx]
        pred_proba = model.predict_proba(x_test[idx:idx+1])[0]
        pred_label = np.argmax(pred_proba)
        confidence = pred_proba[pred_label]
        
        axes[i].imshow(image, cmap='gray')
        axes[i].set_title(f'True: {true_label}, Pred: {pred_label}\nConf: {confidence:.3f}')
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    # Load and preprocess data
    print("Loading and preprocessing data...")
    (x_train, y_train, y_train_oh), (x_val, y_val, y_val_oh), (x_test, y_test, y_test_oh) = load_and_preprocess_data()
    
    print(f"Training set: {x_train.shape[0]} samples")
    print(f"Validation set: {x_val.shape[0]} samples")
    print(f"Test set: {x_test.shape[0]} samples")
    
    # Create and train model
    print("\nCreating neural network...")
    model = NeuralNetwork(
        input_size=784,
        hidden_sizes=[128, 64],  # Two hidden layers
        output_size=10,
        random_seed=42
    )
    
    print("Training model...")
    model.train(
        x_train, y_train_oh,
        x_val, y_val_oh,
        epochs=50,
        learning_rate=0.001,
        batch_size=32,
        verbose=True
    )
    
    # Plot training history
    model.plot_training_history()
    
    # Evaluate model
    print("\nEvaluating model...")
    test_accuracy = evaluate_model(model, x_test, y_test, y_test_oh)
    
    # Visualize predictions
    print("\nVisualizing predictions...")
    visualize_predictions(model, x_test, y_test)