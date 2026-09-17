import cv2  #OpenCV for video processing, GUI rendering, and drawing
import numpy as np  #NumPy to handle fast math (square roots, powers)
import mediapipe as mp  #Google MediaPipe for 3D hand tracking

#Calculate 3D Distance
def calculate_distance(p1, p2):
    """Calculates Euclidean distance between two 3D joint points."""
    #sqrt((x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2)
    return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

#Main Tracking Function
def count_fingers():
    #MediaPipe hand tracking and drawing utility solutions
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    #hand tracking model settings
    hands = mp_hands.Hands(
        static_image_mode=False,     #Optimized for continuous video stream
        max_num_hands=1,            #Limit tracking to 1 main hand
        min_detection_confidence=0.7, #70% certainty needed to detect a hand
        min_tracking_confidence=0.7   #70% certainty needed to keep tracking joints
    )

    #MediaPipe landmark indices for finger tips and base knuckles
    #Index order: [Thumb, Index, Middle, Ring, Pinky]
    finger_tips = [4, 8, 12, 16, 20]
    finger_bases = [2, 6, 10, 14, 18]

    #connection to the built in Mac camera
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
            for hand_landmarks, hand_handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                #Draw skeletal lines and joint dots on top of the video image
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                #Extract the array of 21 3D joint coordinates
                landmarks = hand_landmarks.landmark
                wrist = landmarks[0]  #Landmark 0 is the wrist joint (anchor point)
                fingers = []  #Array to store status 
                #(1 = extended, 0 = closed)

                #Thumb Geometry Logic
                pinky_base = landmarks[17]  #Pinky base knuckle as thumb reference
                #Measure distance from thumb tip to pinky knuckle
                thumb_tip_dist = calculate_distance(landmarks[4], pinky_base)
                #Measure distance from thumb base joint to pinky knuckle
                thumb_base_dist = calculate_distance(landmarks[2], pinky_base)
                
                #Thumb is open if tip extends outward across the X-axis relative to joint 3
                hand_label = hand_handedness.classification[0].label
                if hand_label == "Right":
                    if landmarks[4].x < landmarks[3].x:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:
                    if landmarks[4].x > landmarks[3].x:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                #Four Fingers Geometry Logic
                #Loop through tip/base index pairs for Index, Middle, Ring, Pinky
                for tip_idx, base_idx in zip(finger_tips[1:], finger_bases[1:]):
                    #Measure distance from finger tip to wrist landmark
                    tip_dist = calculate_distance(landmarks[tip_idx], wrist)
                    #Measure distance from lower knuckle to wrist landmark
                    base_dist = calculate_distance(landmarks[base_idx], wrist)

                    #Finger is open if tip is higher than middle joint (Y decreases upward)
                    pip_idx = tip_idx - 2
                    if landmarks[tip_idx].y < landmarks[pip_idx].y:
                        fingers.append(1)
                    else:
                        fingers.append(0)

                #Sum all 1s in array to calculate total open fingers
                finger_count = sum(fingers)

        #Overlay green finger count text onto the top-left of the image
        cv2.putText(
            image, f"Fingers: {finger_count}", (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        #Render updated video frame in window titled "Finger Counter"
        cv2.imshow("Finger Counter", image)

        #Break loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()           #Release webcam hardware connection cleanly
    cv2.destroyAllWindows() #Close all OpenCV active desktop preview windows

#Run count_fingers() automatically when script is executed directly
if __name__ == "__main__":
    count_fingers()