import cv2
import mediapipe as mp

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
