from tensorflow.keras.models import load_model # type: ignore
import cv2
import mediapipe as mp
import numpy as np
import landmarks as lm
import os

# Load trained CNN model
model = load_model("gesture_recognition_cnn.h5")

# Define class names (adjust to your dataset)
CLASS_NAMES = sorted([name.split(".")[0] for name in os.listdir("pickles/")])

def preprocess_points(points, target_points=234):
    """
    Convert landmarks to shape (1, target_points, 2) for CNN.
    Pads with zeros if less than target_points.
    """
    points = np.array(points, dtype=np.float32)

    if len(points) < target_points:
        pad_len = target_points - len(points)
        points = np.vstack([points, np.zeros((pad_len, 2), dtype=np.float32)])
    else:
        points = points[:target_points]

    return np.expand_dims(points, axis=0)  # shape (1, target_points, 2)


def predict_gesture(points):
    """Run model inference on landmark points"""
    processed = preprocess_points(points)
    preds = model.predict(processed, verbose=0)
    class_id = np.argmax(preds)
    confidence = preds[0][class_id]
    if CLASS_NAMES[class_id] == "nosign":
      return "", 0 
    elif confidence < 0.6:
      return "", 0
    return CLASS_NAMES[class_id], confidence

def open_camera():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6)
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(min_detection_confidence=0.6, min_tracking_confidence=0.6)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    cv2.namedWindow('Gesture Recognition', cv2.WINDOW_AUTOSIZE)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results_hand = hands.process(rgb_frame)
            results_face = face_mesh.process(rgb_frame)

            total_points = []
            # Extract landmarks (face + hands)
            if results_face.multi_face_landmarks:
                for face_landmarks in results_face.multi_face_landmarks:
                    for idx in lm.ALL:
                        if idx < len(face_landmarks.landmark):
                            lm_point = face_landmarks.landmark[idx]
                            h, w, _ = frame.shape
                            cx, cy = int(lm_point.x * w), int(lm_point.y * h)
                            total_points.append((cx, cy))

            if results_hand.multi_hand_landmarks:
                for hand_landmarks in results_hand.multi_hand_landmarks:
                    h, w, _ = frame.shape
                    total_points.extend([(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark])
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Predict gesture if points exist
            if total_points:
                gesture, conf = predict_gesture(total_points)
                cv2.putText(frame, f"{gesture} ({conf:.2f})", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Gesture Recognition', frame)

            if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        face_mesh.close()

if __name__ == "__main__":
    open_camera()
