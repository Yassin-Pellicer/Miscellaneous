import time
import cv2
import mediapipe as mp
import numpy as np
import pickle
from tensorflow.keras.models import load_model # type: ignore
import landmarks as lm

class ImprovedGestureRecognizer:
    def __init__(self, model_path="gesture_model.keras", label_encoder_path="label_encoder.pkl"):
        self.FEATURE_DIM = 468
        self.SEQUENCE = 20
        self.buffer = []
        
        # Load model and label encoder
        try:
            self.model = load_model(model_path, compile=False)
            print("Model loaded successfully!")
            
            # Pre-compile the model with a dummy prediction for faster inference
            dummy_input = np.zeros((1, self.SEQUENCE, self.FEATURE_DIM), dtype=np.float32)
            _ = self.model.predict(dummy_input, verbose=0)
            print("Model warmed up!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            exit(1)

        try:
            with open(label_encoder_path, "rb") as f:
                self.label_encoder = pickle.load(f)
            print("Label encoder loaded successfully!")
        except Exception as e:
            print(f"Error loading label encoder: {e}")
            exit(1)

    def predict_gesture(self):
        if len(self.buffer) < self.SEQUENCE:
            return "No gesture", 0.0
            
        # Use the last SEQUENCE frames for consistency
        sequence = self.buffer[-self.SEQUENCE:]
        
        # Create properly shaped input matching training data format
        padded_sequence = np.zeros((self.SEQUENCE, self.FEATURE_DIM), dtype=np.float32)
        
        for i, frame_points in enumerate(sequence):
            if len(frame_points) > 0:
                # Ensure we have the right format - frame_points should be (N, 2) coordinates
                frame_points = np.array(frame_points, dtype=np.float32)
                
                # Flatten to 1D as expected by the model
                frame_flat = frame_points.flatten()
                
                # Fill the padded sequence with proper bounds checking
                copy_len = min(len(frame_flat), self.FEATURE_DIM)
                padded_sequence[i, :copy_len] = frame_flat[:copy_len]
        
        # Reshape for model input: (batch_size, sequence_length, features)
        input_data = padded_sequence.reshape(1, self.SEQUENCE, self.FEATURE_DIM)
        
        # Make prediction
        predictions = self.model.predict(input_data, verbose=0)[0]
        
        confidence = float(np.max(predictions))
        predicted_idx = int(np.argmax(predictions))
        predicted_class = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        return predicted_class, confidence

    def extract_landmarks_consistent(self, frame, results_hand, results_face):
        """Extract landmarks with consistent ordering matching training data"""
        total_points = []
        h, w = frame.shape[:2]

        # Face landmarks first - CONSISTENT ORDER IS CRUCIAL
        face_points = []
        if results_face.multi_face_landmarks:
            face_landmarks = results_face.multi_face_landmarks[0]
            for idx in lm.ALL:  # Make sure this matches your training order exactly
                if idx < len(face_landmarks.landmark):
                    pt = face_landmarks.landmark[idx]
                    cx, cy = int(pt.x * w), int(pt.y * h)
                    face_points.append((cx, cy))
                    
                    # Optional: visualize face landmarks
                    cv2.circle(frame, (cx, cy), 1, (0, 255, 0), -1)
        
        # Hand landmarks second - MAINTAIN CONSISTENT ORDER
        hand_points = []
        if results_hand.multi_hand_landmarks:
            # Sort hands by x-coordinate for consistency (left hand first)
            hands_with_x = []
            for hand_landmarks in results_hand.multi_hand_landmarks:
                hand_x = np.mean([lm.x for lm in hand_landmarks.landmark])
                hands_with_x.append((hand_x, hand_landmarks))
            
            # Sort by x-coordinate (leftmost first)
            hands_with_x.sort(key=lambda x: x[0])
            
            for _, hand_landmarks in hands_with_x:
                # Draw hand landmarks for visualization
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                )
                
                # Extract hand points in consistent order
                for landmark in hand_landmarks.landmark:
                    cx, cy = int(landmark.x * w), int(landmark.y * h)
                    hand_points.append((cx, cy))

        # Combine in the same order as training: face first, then hands
        total_points = face_points + hand_points
        return total_points

    def normalize_points_proper(self, points):
        """Proper normalization matching training data preprocessing"""
        if not points or len(points) == 0:
            return np.array([])
        
        points = np.array(points, dtype=np.float32)
        
        # Check if we have enough face landmarks for normalization
        if len(points) > max(lm.CHIN_POINT, lm.FOREHEAD_POINT):
            try:
                chin = points[lm.CHIN_POINT]
                forehead = points[lm.FOREHEAD_POINT]
                
                # Calculate face distance for scaling
                face_dist = np.linalg.norm(forehead - chin)
                
                if face_dist > 0:
                    # Scale based on face size (normalize to standard face size)
                    scale = 100.0 / face_dist
                    
                    # Center on chin and scale
                    normalized_points = (points - chin) * scale
                    
                    # Apply consistent offset (same as training)
                    OFFSET = np.array([250, 250])
                    normalized_points = normalized_points + OFFSET
                    
                    return normalized_points
                    
            except IndexError:
                print("Warning: Face landmarks not complete for normalization")
        
        # Fallback: simple center normalization
        if len(points) > 0:
            centroid = np.mean(points, axis=0)
            centered_points = points - centroid
            # Add standard offset
            return centered_points + np.array([250, 250])
        
        return points

    def run_inference(self):
        """Run inference with improved data quality"""
        cap = cv2.VideoCapture(0)
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize MediaPipe with settings that match training
        mp_hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Allow both hands like in training
            min_detection_confidence=0.6,  # Lower threshold for better detection
            min_tracking_confidence=0.6
        )
        mp_face = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,  # Enable for better accuracy
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        
        print("Starting improved gesture recognition...")
        print("Press 'q' to quit, 'r' to reset buffer")
        
        predicted_class = "No gesture"
        confidence = 0.0
        last_prediction_time = time.time()
        prediction_interval = 0.8  # Slightly longer for better accuracy
        
        # Performance tracking
        frame_count = 0
        prediction_times = []
        
        # Buffer quality indicators
        buffer_quality_scores = []
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame from camera")
                    break
                    
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process landmarks
                results_hand = mp_hands.process(rgb)
                results_face = mp_face.process(rgb)

                # Extract landmarks with consistent ordering
                total_points = self.extract_landmarks_consistent(frame, results_hand, results_face)
                
                # Normalize points properly
                norm_points = self.normalize_points_proper(total_points)
                
                # Quality check: only add good frames to buffer
                frame_quality = self.assess_frame_quality(norm_points, results_hand, results_face)
                buffer_quality_scores.append(frame_quality)
                
                # Only add high-quality frames to buffer
                if frame_quality > 0.3:  # Quality threshold
                    self.buffer.append(norm_points)
                    # Keep buffer size reasonable
                    if len(self.buffer) > self.SEQUENCE + 10:
                        self.buffer = self.buffer[-self.SEQUENCE:]
                
                # Make predictions with sufficient high-quality data
                current_time = time.time()
                if (current_time - last_prediction_time >= prediction_interval and 
                    len(self.buffer) >= self.SEQUENCE):
                    
                    # Check buffer quality
                    recent_quality = np.mean(buffer_quality_scores[-self.SEQUENCE:]) if len(buffer_quality_scores) >= self.SEQUENCE else 0
                    
                    if recent_quality > 0.4:  # Only predict with good quality data
                        pred_start = time.time()
                        predicted_class, confidence = self.predict_gesture()
                        pred_time = time.time() - pred_start
                        prediction_times.append(pred_time)
                        last_prediction_time = current_time
                        
                        print(f"Prediction: {predicted_class} (conf: {confidence:.3f}, quality: {recent_quality:.2f}, time: {pred_time*1000:.1f}ms)")
                
                # Display information
                text = f"Gesture: {predicted_class} ({confidence:.3f})"
                cv2.putText(frame, text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show buffer status and quality
                buffer_info = f"Buffer: {len(self.buffer)}/{self.SEQUENCE}, Quality: {frame_quality:.2f}"
                cv2.putText(frame, buffer_info, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show detection status
                hands_detected = "Hands: YES" if results_hand.multi_hand_landmarks else "Hands: NO"
                face_detected = "Face: YES" if results_face.multi_face_landmarks else "Face: NO"
                cv2.putText(frame, f"{hands_detected}, {face_detected}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                cv2.imshow("Improved Gesture Recognition", frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.buffer = []
                    buffer_quality_scores = []
                    print("Buffer reset!")
                
                frame_count += 1
        
        except KeyboardInterrupt:
            print("Interrupted by user")
        except Exception as e:
            print(f"Error during inference: {e}")
        finally:
            # Performance stats
            if prediction_times:
                avg_pred_time = np.mean(prediction_times) * 1000
                print(f"Average prediction time: {avg_pred_time:.1f}ms")
            
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            mp_hands.close()
            mp_face.close()
            print("Cleanup completed")

    def assess_frame_quality(self, norm_points, results_hand, results_face):
        """Assess the quality of the current frame for gesture recognition"""
        quality_score = 0.0
        
        # Check if we have landmarks
        if len(norm_points) == 0:
            return 0.0
        
        # Face detection quality
        if results_face.multi_face_landmarks:
            quality_score += 0.3
            
        # Hand detection quality
        if results_hand.multi_hand_landmarks:
            num_hands = len(results_hand.multi_hand_landmarks)
            quality_score += min(num_hands * 0.35, 0.7)  # Max 0.7 for hands
        
        # Landmark completeness
        expected_landmarks = len(lm.ALL) + 21 * 2  # Face + both hands
        actual_landmarks = len(norm_points)
        completeness = min(actual_landmarks / expected_landmarks, 1.0)
        quality_score *= completeness
        
        return min(quality_score, 1.0)


def main():
    recognizer = ImprovedGestureRecognizer()
    recognizer.run_inference()


if __name__ == "__main__":
    main()