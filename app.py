import cv2  #OpenCV for video processing, GUI rendering, and drawing
import numpy as np  #NumPy to handle math
import mediapipe as mp  #Google MediaPipe for 3D hand tracking

#Calculate 3D Distance
def calculate_distance(p1, p2):
    """Calculates Euclidean distance between two 3D joint points."""
    #sqrt((x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2)
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

#Main function
def count_fingers():
    #MediaPipe hand tracking and drawing utility solutions
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    #hand tracking model settings
    hands = mp_hands.Hands(
        static_image_mode=False,      #Optimized for continuous video stream
        max_num_hands=2,              #Tracks up to 2 hands
        min_detection_confidence=0.7, #70% certainty needed to detect a hand
        min_tracking_confidence=0.7)   #70% certainty needed to keep tracking joints

    #MediaPipe landmark indices for finger tips and base knuckles
    #Index order: [Thumb, Index, Middle, Ring, Pinky]
    finger_tips = [4, 8, 12, 16, 20]
    finger_bases = [2, 6, 10, 14, 18]

    #connection to the built in Mac camera, 0 for iPhone, 1 for Mac
    cap = cv2.VideoCapture(1)

    print("Accurate Finger Counter Running! Press 'q' to quit.")

    #Main video processing loop
    while cap.isOpened():
        #Read the next video frame from the camera feed
        success, image = cap.read()
        if not success or image is None:
            continue  # Skip processing if frame was dropped

        #Mirror image horizontally
        image = cv2.flip(image, 1)
        
        #BGR to RGB conversion for MediaPipe processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        #Pass frame into MediaPipe to locate hand joints
        results = hands.process(rgb_image)
        finger_count = 0  #Reset total finger count for current frame

        #If MediaPipe detects a hand in the current frame
        if results.multi_hand_landmarks:
            all_hands_fist = True
            all_hands_open = True
            hand_finger_counts = []

            # First pass: calculate counts across all hands to determine color state
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = hand_landmarks.landmark
                wrist = landmarks[0]
                fingers = []

                #Thumb Geometry Logic (Distance to Pinky Base Knuckle landmark 17)
                pinky_mcp = landmarks[17]
                thumb_tip_to_pinky = calculate_distance(landmarks[4], pinky_mcp)
                thumb_ip_to_pinky = calculate_distance(landmarks[3], pinky_mcp)
                
                if thumb_tip_to_pinky > thumb_ip_to_pinky * 1.1:
                    fingers.append(1)
                else:
                    fingers.append(0)

                #Four Fingers Geometry Logic (Orientation-Agnostic Radial Distance)
                for tip_idx in finger_tips[1:]:
                    pip_idx = tip_idx - 2
                    tip_wrist_dist = calculate_distance(landmarks[tip_idx], wrist)
                    pip_wrist_dist = calculate_distance(landmarks[pip_idx], wrist)

                    if tip_wrist_dist > pip_wrist_dist:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                hand_open_fingers = sum(fingers)
                hand_finger_counts.append(hand_open_fingers)

                if hand_open_fingers != 0:
                    all_hands_fist = False
                if hand_open_fingers != 5:
                    all_hands_open = False

            # Assign dynamic color and gesture text (Red for fist, Green for open/neither)
            if all_hands_fist:
                state_color = (0, 0, 255)  # BGR Red
                gesture_text = "FIST"
            elif all_hands_open:
                state_color = (0, 255, 0)  # BGR Green
                gesture_text = "WIDE OPEN"
            else:
                state_color = (0, 255, 0)  # BGR Green
                gesture_text = ""

            # Define MediaPipe skeletal line and joint dot drawing specs with state color
            landmark_style = mp_drawing.DrawingSpec(color=state_color, thickness=2, circle_radius=4)
            connection_style = mp_drawing.DrawingSpec(color=state_color, thickness=2)

            # Second pass: Draw skeletal lines & sum total finger count
            for hand_landmarks, count in zip(results.multi_hand_landmarks, hand_finger_counts):
                #Draw skeletal lines and joint dots on top of the video image
                mp_drawing.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=landmark_style,
                    connection_drawing_spec=connection_style
                )
                finger_count += count
        else:
            state_color = (0, 255, 0)  # Default color when no hand is detected
            gesture_text = ""

        #Overlay green finger count text onto the top-left of the image
        cv2.putText(
            image, f"Fingers: {finger_count}", (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 2, state_color, 3)

        #Overlay gesture status text underneath the finger count
        if gesture_text:
            cv2.putText(
                image, gesture_text, (50, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, state_color, 3)

        #Render updated video frame in window titled "Finger Counter"
        cv2.imshow("Finger Counter", image)

        #Break loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()           #Release webcam
    cv2.destroyAllWindows() #Close all OpenCV windows

#Run count_fingers() automatically when script is executed directly
if __name__ == "__main__":
    count_fingers()