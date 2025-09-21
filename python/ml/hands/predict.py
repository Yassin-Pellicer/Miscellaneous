import cv2
import mediapipe as mp
import numpy as np
import pickle
from collections import deque
from tensorflow.keras.models import load_model # type: ignore
import landmarks as lm

class GestureInference:
    def __init__(self, model_path="gesture_model.h5", label_encoder_path="label_encoder.pkl"):
        # Load trained model and label encoder
        self.model = load_model(model_path)
        with open(label_encoder_path, "rb") as f:
            self.label_encoder = pickle.load(f)
        
        # Model parameters (from training)
        self.max_seq_len = 20
        self.feature_dim = 468
        
        # Sequence buffer for real-time prediction
        self.sequence_buffer = deque(maxlen=20)
        
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_face = mp.solutions.face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Prediction smoothing
        self.recent_predictions = deque(maxlen=5)
        self.current_prediction = "No Gesture"
        self.confidence = 0.0
        
        print("Model loaded successfully!")
        print(f"Classes: {list(self.label_encoder.classes_)}")

    def normalize_points(self, points):
        """Normalize points based on chin-forehead distance"""
        if not points:
            return np.array([])
        
        points = np.array(points, dtype=np.float32)
        
        # Scale face if chin + forehead available
        if len(points) > max(lm.CHIN_POINT, lm.FOREHEAD_POINT):
            chin, forehead = points[lm.CHIN_POINT], points[lm.FOREHEAD_POINT]
            dist = np.linalg.norm(forehead - chin)
            if dist > 0:
                scale = 100.0 / dist
                points = (points - chin) * scale
        
        OFFSET = np.array([250, 250])
        return points + OFFSET

    def extract_landmarks(self, frame, results_hand, results_face):
        """Extract landmarks from face and hands"""
        total_points = []
        h, w, _ = frame.shape

        # Face landmarks
        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                for idx in lm.ALL:
                    if idx < len(face_landmarks.landmark):
                        pt = face_landmarks.landmark[idx]
                        cx, cy = int(pt.x * w), int(pt.y * h)
                        cv2.circle(frame, (cx, cy), 2, (0, 255, 0), -1)
                        total_points.append((cx, cy))

        # Hand landmarks
        if results_hand.multi_hand_landmarks:
            for hand_landmarks in results_hand.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                )
                total_points.extend([
                    (int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark
                ])

        return total_points

    def predict_gesture(self):
        """Predict gesture from current sequence buffer"""
        if len(self.sequence_buffer) < 10:
            return "Collecting...", 0.0
        
        # Prepare input data
        sequence = list(self.sequence_buffer)
        padded_sequence = np.zeros((self.max_seq_len, self.feature_dim), dtype=np.float32)
        
        for i, frame in enumerate(sequence):
            if i >= self.max_seq_len:
                break
            frame_flat = np.array(frame, dtype=np.float32).flatten()
            padded_sequence[i, :len(frame_flat)] = frame_flat[:self.feature_dim]
        
        # Predict
        input_data = padded_sequence.reshape(1, self.max_seq_len, self.feature_dim)
        predictions = self.model.predict(input_data, verbose=0)[0]
        
        confidence = np.max(predictions)
        predicted_idx = np.argmax(predictions)
        predicted_class = self.label_encoder.inverse_transform([predicted_idx])[0]
        
        return predicted_class, confidence

    def smooth_prediction(self, prediction, confidence):
        """Smooth predictions over recent frames"""
        if confidence > 0.2:  # Only consider confident predictions
            self.recent_predictions.append(prediction)
            
            if len(self.recent_predictions) >= 1:
                # Most common prediction in recent frames
                from collections import Counter
                most_common = Counter(self.recent_predictions).most_common(1)[0]
                
                if most_common[1] >= 2:  # At least 2 occurrences
                    self.current_prediction = most_common[0]
                    self.confidence = confidence

    def run_inference(self):
        """Run real-time inference"""
        cap = cv2.VideoCapture(0)
        
        print("Starting gesture recognition...")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process landmarks
            results_hand = self.mp_hands.process(rgb)
            results_face = self.mp_face.process(rgb)
            total_points = self.extract_landmarks(frame, results_hand, results_face)
            
            # Add to buffer and predict
            if total_points:
                norm_points = self.normalize_points(total_points)
                self.sequence_buffer.append(norm_points.tolist())
                
                prediction, confidence = self.predict_gesture()
                self.smooth_prediction(prediction, confidence)
            
            # Display results
            cv2.putText(frame, f"Gesture: {self.current_prediction}", 
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.putText(frame, f"Confidence: {self.confidence:.2f}", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"Buffer: {len(self.sequence_buffer)}/20", 
                       (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show normalized visualization
            viz = np.zeros((400, 400, 3), dtype=np.uint8)
            if total_points:
                norm_points = self.normalize_points(total_points)
                for x, y in norm_points.astype(int):
                    if 0 <= x < 400 and 0 <= y < 400:
                        cv2.circle(viz, (x, y), 2, (0, 255, 255), -1)
            
            cv2.putText(viz, f"{self.current_prediction}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            cv2.imshow("Gesture Recognition", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        inference = GestureInference()
        inference.run_inference()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure you have 'gesture_model.h5' and 'label_encoder.pkl' files")
    except Exception as e:
        print(f"Error: {e}")