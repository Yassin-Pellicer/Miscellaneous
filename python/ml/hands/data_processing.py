import cv2
import mediapipe as mp
import numpy as np
import pickle
import os
import time
import landmarks as lm   # your custom landmarks file

def save_sequence(class_name, sequence):
    """Save recorded sequence to pickle"""
    if not sequence:
        return
    filename = f"{class_name}.pickle"
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            dataset = pickle.load(f)
    else:
        dataset = []
    dataset.append({"class_name": class_name, "points": sequence})
    with open(filename, "wb") as f:
        pickle.dump(dataset, f)
    print(f"Saved sequence ({len(sequence)} frames) to {filename}")

def normalize_points(points):
    """Normalize points based on chin-forehead distance if available"""
    if not points:
        return np.array([])
    points = np.array(points, dtype=np.float32)

    # scale face if chin + forehead available
    if len(points) > max(lm.CHIN_POINT, lm.FOREHEAD_POINT):
        chin, forehead = points[lm.CHIN_POINT], points[lm.FOREHEAD_POINT]
        dist = np.linalg.norm(forehead - chin)
        if dist > 0:
            scale = 100.0 / dist
            points = (points - chin) * scale

    OFFSET = np.array([250, 250])  # shift for display
    return points + OFFSET

def process_landmarks(frame, results_hand, results_face):
    """Extract 2D landmark coordinates for face + both hands"""
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

    # Hand landmarks (both hands)
    if results_hand.multi_hand_landmarks:
        for hand_landmarks in results_hand.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
            )
            total_points.extend([
                (int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark
            ])

    return total_points

def record_sequence(cap, hands, face_mesh, class_name="default", duration=2, num_frames=20):
    """Record a sequence of frames and save to pickle"""
    sequence = []

    # Countdown (non-blocking, live video)
    countdown_duration = 3
    countdown_start = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            return
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hand = hands.process(rgb)
        results_face = face_mesh.process(rgb)
        total_points = process_landmarks(frame, results_hand, results_face)

        elapsed = time.time() - countdown_start
        remaining = countdown_duration - elapsed

        # Draw countdown text
        if remaining > 0:
            cv2.putText(frame, f"GET READY {int(remaining)+1}", (50, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        else:
            break  # countdown finished

        # Show normalized points
        norm_canvas = np.zeros((500, 500, 3), dtype=np.uint8)
        norm_points = normalize_points(total_points)
        for (x, y) in norm_points.astype(int):
            cv2.circle(norm_canvas, (x, y), 3, (0, 255, 0), -1)

        cv2.imshow("Hand Detection", frame)
        cv2.imshow("Normalized Points", norm_canvas)

        if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
            return

    # Start recording
    print("Recording started...")
    start_time = time.time()
    capture_times = np.linspace(0, duration, num_frames)
    idx = 0

    while idx < num_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results_hand = hands.process(rgb)
        results_face = face_mesh.process(rgb)
        total_points = process_landmarks(frame, results_hand, results_face)

        elapsed = time.time() - start_time
        if elapsed >= capture_times[idx]:
            norm_points = normalize_points(total_points)
            sequence.append(norm_points.tolist())
            print(f"Captured frame {idx+1}/{num_frames}")
            idx += 1

        # Show normalized points
        norm_canvas = np.zeros((500, 500, 3), dtype=np.uint8)
        norm_points = normalize_points(total_points)
        for (x, y) in norm_points.astype(int):
            cv2.circle(norm_canvas, (x, y), 3, (0, 255, 0), -1)

        cv2.putText(frame, f"Recording... {max(0, duration - elapsed):.1f}s left",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Hand Detection", frame)
        cv2.imshow("Normalized Points", norm_canvas)

        if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
            break

    save_sequence(class_name, sequence)
    print("Recording finished!")

def open_camera():
    mp_hands = mp.solutions.hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_face = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    print("Controls: 'c' to record, 'q'/ESC to exit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results_hand = mp_hands.process(rgb)
            results_face = mp_face.process(rgb)
            total_points = process_landmarks(frame, results_hand, results_face)

            # Normalized live preview
            norm_canvas = np.zeros((500, 500, 3), dtype=np.uint8)
            norm_points = normalize_points(total_points)
            for (x, y) in norm_points.astype(int):
                cv2.circle(norm_canvas, (x, y), 3, (0, 255, 0), -1)

            cv2.putText(frame, "Press 'c' to record, 'q' to quit", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Hand Detection", frame)
            cv2.imshow("Normalized Points", norm_canvas)

            key = cv2.waitKey(1) & 0xFF
            if key in [27, ord('q')]:
                break
            elif key == ord('c'):
                record_sequence(cap, mp_hands, mp_face, class_name="pickles/hola")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        mp_hands.close()
        mp_face.close()

if __name__ == "__main__":
    open_camera()
