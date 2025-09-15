import cv2
import mediapipe as mp
import numpy as np

CHIN_POINT = 254

def representation(total_points_relative):
    if total_points_relative is None:
        return
    
    # Convert to numpy array and ensure proper shape
    total_points_relative = np.array(total_points_relative)
    
    # Check if array is 1D and reshape if needed
    if total_points_relative.ndim == 1:
        # If it's 1D, we need to determine how to reshape it
        # Assuming it's flattened (x1, y1, z1, x2, y2, z2, ...)
        if len(total_points_relative) % 3 == 0:
            total_points_relative = total_points_relative.reshape(-1, 3)
        elif len(total_points_relative) % 2 == 0:
            # If it's 2D points (x1, y1, x2, y2, ...)
            total_points_relative = total_points_relative.reshape(-1, 2)
        else:
            print(f"Error: Cannot reshape array of length {len(total_points_relative)}")
            return
    
    # Ensure we have at least 2D coordinates
    if total_points_relative.shape[1] < 2:
        print(f"Error: Points array has shape {total_points_relative.shape}, need at least 2 columns")
        return
    
    scale = 500
    offset = np.array([250, 250])
    canvas = np.zeros((500, 500, 3), dtype=np.uint8)
    
    # Take x, y coordinates
    points_2d = total_points_relative[:, :2]  
    points_2d = points_2d * scale + offset    # scale and shift
    
    for pt in points_2d:
        x, y = int(pt[0]), int(pt[1])
        # Check bounds to avoid drawing outside canvas
        if 0 <= x < 500 and 0 <= y < 500:
            cv2.circle(canvas, (x, y), 3, (0, 255, 0), -1)  # draw green point
    
    cv2.imshow("Relative Landmarks", canvas)
def open_camera():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hand = hands.process(rgb_frame)
        results_face = face_mesh.process(rgb_frame)

        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                mp_draw.draw_landmarks(frame, face_landmarks, mp_face.FACEMESH_CONTOURS)

        if results_hand.multi_hand_landmarks:
            text = "Hand detected"
            for hand_landmarks in results_hand.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            text = "Nothing"

        total_points = []

        # Suppose CHIN_POINT is the index of the chin in the face landmarks
        CHIN_POINT = 152  # example index in MediaPipe face mesh

        total_points = []

        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                face_points = [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]
                total_points.extend(face_points)

        if results_hand.multi_hand_landmarks:
            for hand_landmarks in results_hand.multi_hand_landmarks:
                hand_points = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                total_points.extend(hand_points)

        # Convert to NumPy array for easier math
        total_points = np.array(total_points, dtype=np.float32)

        if len(total_points) > CHIN_POINT:
            total_points_relative = total_points - total_points[CHIN_POINT]
        else:
            total_points_relative = total_points  # fallback

        # Scale factor for visualization
        representation(total_points_relative)

        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
          1, (0, 255, 0) if text == "Hand detected" else (0, 0, 255), 2)

        cv2.imshow('Hand Detection', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27 or cv2.getWindowProperty('Hand Detection', cv2.WND_PROP_VISIBLE) == 0:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    open_camera()
