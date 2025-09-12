import cv2
import numpy as np
import tensorflow as tf
from ultralytics import YOLO

def predict_traffic_signs(img_path, model_path="keras/model.keras", yolo_path="yolo/best.pt"):
    """
    Fixed version of traffic sign prediction with proper preprocessing
    """
    # Load models
    try:
        yolo = YOLO(yolo_path)
        classifier = tf.keras.models.load_model(model_path)
        print(f"Models loaded successfully")
        print(f"Classifier expects input shape: {classifier.input_shape}")
        print(f"Number of classes: {classifier.output_shape[-1]}")
    except Exception as e:
        print(f"Error loading models: {e}")
        return
    
    # Load image
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not load {img_path}")
        return
    
    print(f"Image loaded: {img.shape}")
    
    # Get YOLO detections
    results = yolo(img, verbose=False)
    
    detection_count = 0
    target_size = (128, 128)  # Model expects 128x128
    
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box.cpu().numpy())
                
                # Add small margin around detection
                margin = 5
                x1 = max(0, x1 - margin)
                y1 = max(0, y1 - margin)
                x2 = min(img.shape[1], x2 + margin)
                y2 = min(img.shape[0], y2 + margin)
                
                # Extract crop
                crop = img[y1:y2, x1:x2]
                
                # Skip tiny crops
                if crop.shape[0] < 20 or crop.shape[1] < 20:
                    continue
                
                print(f"\nProcessing detection {detection_count + 1}")
                print(f"Crop size: {crop.shape}")
                
                # CRITICAL: Proper preprocessing pipeline
                # 1. Resize to model input size
                crop_resized = cv2.resize(crop, target_size)
                
                # 2. Convert BGR to RGB (OpenCV loads as BGR, but models usually expect RGB)
                crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
                
                # 3. Normalize to [0, 1] range
                crop_normalized = crop_rgb.astype(np.float32) / 255.0
                
                # 4. Add batch dimension
                crop_batch = np.expand_dims(crop_normalized, axis=0)
                
                print(f"Input shape to model: {crop_batch.shape}")
                print(f"Input range: [{crop_batch.min():.3f}, {crop_batch.max():.3f}]")
                
                # Make prediction
                try:
                    predictions = classifier.predict(crop_batch, verbose=0)
                    
                    # Get the predicted class and confidence
                    predicted_class = np.argmax(predictions[0])
                    confidence = predictions[0][predicted_class]
                    
                    print(f"Predicted class: {predicted_class}")
                    print(f"Confidence: {confidence:.4f}")
                    
                    # Show top 5 predictions
                    top_5_indices = np.argsort(predictions[0])[::-1][:5]
                    print("Top 5 predictions:")
                    for i, idx in enumerate(top_5_indices):
                        print(f"  {i+1}. Class {idx}: {predictions[0][idx]:.4f}")
                    
                    # Visualize the crop
                    cv2.imshow(f"Detection {detection_count + 1} - Class {predicted_class}", crop)
                    print("Press any key to continue to next detection...")
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                    
                except Exception as e:
                    print(f"Error making prediction: {e}")
                    continue
                
                detection_count += 1
    
    print(f"\nTotal detections processed: {detection_count}")

def test_model_sanity(model_path="keras/model.keras"):
    """
    Test if the model can make basic predictions
    """
    print("=== TESTING MODEL SANITY ===")
    
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"✓ Model loaded")
        
        # Create random test input
        test_input = np.random.random((1, 128, 128, 3)).astype(np.float32)
        
        # Make prediction
        prediction = model.predict(test_input, verbose=0)
        
        print(f"✓ Model can make predictions")
        print(f"  Output shape: {prediction.shape}")
        print(f"  Output sum: {np.sum(prediction):.4f} (should be ~1.0 for softmax)")
        print(f"  Max prediction: {np.max(prediction):.4f}")
        print(f"  Min prediction: {np.min(prediction):.4f}")
        
        # Check if all predictions are the same (indicating untrained model)
        if np.std(prediction) < 1e-6:
            print("⚠️  WARNING: All predictions are nearly identical - model might be untrained!")
        else:
            print("✓ Model shows variation in predictions")
            
    except Exception as e:
        print(f"✗ Error testing model: {e}")

def check_image_preprocessing(img_path):
    """
    Visualize the preprocessing pipeline
    """
    print("=== CHECKING IMAGE PREPROCESSING ===")
    
    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not load {img_path}")
        return
    
    # Take a sample crop
    h, w = img.shape[:2]
    crop = img[h//4:3*h//4, w//4:3*w//4]  # Center crop
    
    print(f"Original crop shape: {crop.shape}")
    print(f"Original range: [{crop.min()}, {crop.max()}]")
    
    # Preprocessing steps
    crop_resized = cv2.resize(crop, (128, 128))
    crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
    crop_normalized = crop_rgb.astype(np.float32) / 255.0
    crop_batch = np.expand_dims(crop_normalized, axis=0)
    
    print(f"After preprocessing:")
    print(f"  Shape: {crop_batch.shape}")
    print(f"  Range: [{crop_batch.min():.3f}, {crop_batch.max():.3f}]")
    print(f"  Dtype: {crop_batch.dtype}")

if __name__ == "__main__":
    # Test the model first
    test_model_sanity()
    
    # Check preprocessing
    check_image_preprocessing("yolo/image.png")
    
    # Run prediction
    predict_traffic_signs("yolo/image.png")