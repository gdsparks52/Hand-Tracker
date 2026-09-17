# Real-Time Cross-Platform Finger Counter & Gesture Tracker

An accurate, real-time Computer Vision application built using **OpenCV** and **Google MediaPipe**. The system tracks up to two hands simultaneously, counts extended fingers in 360-degree space, detects specific gestures (*FIST* vs. *WIDE OPEN*), and dynamically changes visual overlay colors based on hand states.

It includes automatic platform detection to handle camera index routing seamlessly across **macOS** and **Windows**.

---

## Features

* **Multi-Hand Tracking:** Detects and counts extended fingers on up to 2 hands simultaneously.
* **360° Orientation Invariant:** Uses radial distance math (finger tips relative to joint bases) rather than axis-bound checks to prevent miscounting when hands tilt, flip, or turn upside down.
* **Dynamic Visual Feedback:**
  * Displays real-time **Finger Count**.
  * **FIST Detection:** Turns hand skeleton, joints, and count text **Red** when all detected hands form a fist, displaying a `FIST` state label.
  * **WIDE OPEN Detection:** Displays a `WIDE OPEN` state label when all detected hands are fully extended.
* **Cross-Platform Camera Routing:** 
  * **macOS:** Targets camera index `1` with `AVFoundation` to avoid automatically grabbing an iPhone via Continuity Camera.
  * **Windows:** Targets camera index `0` using the DirectShow (`cv2.CAP_DSHOW`) backend for fast video stream initialization.

---

## Repository Structure

```text
├── .gitignore          # Excludes venv, pycache, and system files from version control
├── README.md           # Project documentation
├── requirements.txt    # Python package dependencies
├── app.py              # Main active application script
├── app-prev1.py        # Version history: Initial 3D distance single-hand prototype
├── app-prev2.py        # Version history: Dual-hand update
└── app-prev3.py        # Version history: Orientation & gesture color update# Hand-Tracker
