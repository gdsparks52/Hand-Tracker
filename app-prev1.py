import cv2
import mediapipe as mp

def count_fingers():
    #Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    #Track 1 hand with strong confidence threshold
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7)

    tip_ids = [4, 8, 12, 16, 20]
    cap = cv2.VideoCapture(0)

    print("Finger Counter Active! Hold up your hand anywhere on screen.")

    while cap.isOpened():
        success, image = cap.read()
        if not success or image is None:
            continue

        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_image)
        finger_count = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand skeleton overlay
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                landmarks = hand_landmarks.landmark
                fingers = []
                #Thumb tracking (horizontal check)
                if landmarks[tip_ids[0]].x < landmarks[tip_ids[0] - 1].x:
                    fingers.append(1)
                else:
                    fingers.append(0)
                #Four fingers tracking (vertical check: tip higher than knuckle)
                for tip_id in tip_ids[1:]:
                    if landmarks[tip_id].y < landmarks[tip_id - 2].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                finger_count = sum(fingers)

        #overlay result text
        cv2.putText(
            image, f"Fingers: {finger_count}", (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.imshow("Finger Counter", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    count_fingers()