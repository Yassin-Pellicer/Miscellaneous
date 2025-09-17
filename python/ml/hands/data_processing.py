import cv2
import mediapipe as mp
import numpy as np
import landmarks as lm
import pickle
import os
import time

FRAME_COUNT = 0
BUFFER = []
RECORDING = False
FIRST_TIME = True

def capture_and_store_class(class_name, points_2d):
    """Store captured points with frame number to pickle file"""
    # Ensure points_2d is a Python list
    points_list = points_2d.tolist() if isinstance(points_2d, np.ndarray) else points_2d
    if not points_list:
        return

    data_entry = {"class_name": class_name, "points": points_list}

    filename = f"{class_name}.pickle"
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            dataset = pickle.load(f)
    else:
        dataset = []

    dataset.append(data_entry)

    with open(filename, "wb") as f:
        pickle.dump(dataset, f)

    print(f"Saved points under class '{class_name}' in {filename}")

def representation(total_points):
    """Process and display landmarks with recording functionality"""
    global BUFFER, FRAME_COUNT, RECORDING, FIRST_TIME
    
    if not total_points:
        return

    total_points = np.array(total_points, dtype=np.float32)
    total_points_relative = total_points

    # Normalize points if we have face landmarks
    if len(total_points) > max(lm.CHIN_POINT, lm.FOREHEAD_POINT):
        total_points_relative = total_points - total_points[lm.CHIN_POINT]
        chin = total_points[lm.CHIN_POINT]
        forehead = total_points[lm.FOREHEAD_POINT]
        dist = np.linalg.norm(forehead - chin)
        TARGET_DIST = 150
        if dist > 0:
            total_points_relative *= (TARGET_DIST / dist)

    # Ensure proper shape
    if total_points_relative.ndim == 1 and len(total_points_relative) % 2 == 0:
        total_points_relative = total_points_relative.reshape(-1, 2)
    
    if total_points_relative.shape[1] < 2:
        print(f"Error: Points array has shape {total_points_relative.shape}")
        return

    OFFSET = np.array([350, 250])
    points_2d = total_points_relative[:, :2] + OFFSET

    # Handle recording logic
    if RECORDING:
        FIRST_TIME = False
        BUFFER.append(points_2d.copy())  # Store a copy
        FRAME_COUNT += 1
    else:
        # Save data when recording stops (only once)
        if not FIRST_TIME and len(BUFFER) > 0:
            BUFFER = []

def process_landmarks(frame, results_hand, results_face):
    total_points = []
    
    # Process face landmarks
    if results_face.multi_face_landmarks:
        for face_landmarks in results_face.multi_face_landmarks:
            for idx in lm.ALL:
                if idx < len(face_landmarks.landmark):
                    lm_point = face_landmarks.landmark[idx]
                    h, w, _ = frame.shape
                    cx, cy = int(lm_point.x * w), int(lm_point.y * h)
                    cv2.circle(frame, (cx, cy), 2, (0, 255, 0), -1)
                    total_points.append((cx, cy))
    
    # Process hand landmarks
    text = "Nothing"
    if results_hand.multi_hand_landmarks:
        text = "Hand detected"
        mp_draw = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        for hand_landmarks in results_hand.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            total_points.extend([(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark])
    
    return total_points, text

def record_sequence(cap, hands, face_mesh, duration=2, num_captures=20):
    """Record a fixed number of frames evenly across the duration"""
    global RECORDING, FRAME_COUNT, BUFFER

    BUFFER = []
    FRAME_COUNT = 0

    print("Get ready! Recording will start in 3 seconds...")
    countdown_start = time.time()
    countdown_duration = 3

    # Countdown
    while time.time() - countdown_start < countdown_duration:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_hand = hands.process(rgb_frame)
        results_face = face_mesh.process(rgb_frame)
        total_points, text = process_landmarks(frame, results_hand, results_face)

        # Display countdown
        remaining = countdown_duration - (time.time() - countdown_start)
        cv2.putText(frame, f"GET READY! {int(remaining)+1}", (50, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        cv2.imshow("Hand Detection", frame)
        if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
            return

    # Recording phase
    RECORDING = True
    print(f"Recording now for {duration} seconds... capturing {num_captures} frames")
    start_time = time.time()

    # Calculate exact timestamps for each capture
    capture_times = np.linspace(0, duration, num_captures)

    capture_idx = 0
    while capture_idx < num_captures:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_hand = hands.process(rgb_frame)
        results_face = face_mesh.process(rgb_frame)
        total_points, text = process_landmarks(frame, results_hand, results_face)

        elapsed = time.time() - start_time
        if elapsed >= capture_times[capture_idx]:
            BUFFER.append(total_points.copy())
            FRAME_COUNT += 1
            print(f"Captured frame {FRAME_COUNT}/{num_captures}")
            capture_idx += 1

        # Recording indicator
        remaining_time = max(0, duration - elapsed)
        cv2.putText(frame, f"RECORDING... {remaining_time:.1f}s left", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Hand Detection", frame)

        if cv2.waitKey(1) & 0xFF in [27, ord('q')]:
            break

    for i, frame_points in enumerate(BUFFER):
        capture_and_store_class("afternoon", frame_points)

    RECORDING = False
    print("Recording finished!")

def open_camera():
    global RECORDING, FRAME_COUNT, BUFFER, FIRST_TIME

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.4, min_tracking_confidence=0.4)
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(min_detection_confidence=0.4, min_tracking_confidence=0.4)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    cv2.namedWindow('Hand Detection', cv2.WINDOW_AUTOSIZE)

    print("Controls:")
    print("- Press 'c' to start recording")
    print("- Press 'q' or ESC to exit")
    print("- Close any window to exit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results_hand = hands.process(rgb_frame)
            results_face = face_mesh.process(rgb_frame)

            total_points, text = process_landmarks(frame, results_hand, results_face)

            # Display info on main frame
            status_color = (0, 255, 0) if text == "Hand detected" else (0, 0, 255)
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            
            if not RECORDING:
                cv2.putText(frame, "Press 'c' to record, 'q'/ESC to exit", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            representation(total_points)
            cv2.imshow('Hand Detection', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("Exiting...")
                break

            # Start recording when 'c' is pressed and not already recording
            if key == ord('c') and not RECORDING:
                record_sequence(cap, hands, face_mesh, duration=2)

            # Check for window closure
            try:
                if cv2.getWindowProperty('Hand Detection', cv2.WND_PROP_VISIBLE) < 1:
                    print("Exiting due to main window closure...")
                    break
            except cv2.error:
                print("Window was destroyed, exiting...")
                break

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        face_mesh.close()
        print("Program ended successfully!")

if __name__ == '__main__':
    open_camera()