# AI-based-gesture-tracking-system

A touchless computer control system using hand gestures for presentations, browsing, and cursor control. Built with Python, OpenCV, and MediaPipe for real-time hand tracking and gesture recognition.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8+-green.svg)
![MediaPipe](https://img.shields.io/badge/mediapipe-0.10+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🎯 Features

### Single Hand Gestures
- **👆 Cursor Control**: Point with index finger only to move the mouse cursor
- **◀️ Next Slide**: Move hand left to advance presentation slides
- **▶️ Previous Slide**: Move hand right to go back in slides
- **🔽 Scroll Down**: Move hand downward for smooth scrolling
- **🔼 Scroll Up**: Move hand upward for smooth scrolling
- **⏸️ Pause**: Hold hand still to trigger pause action

### Two Hand Gestures (Zoom)
- **🔍 Zoom In**: Form a "kite" shape with both hands (touch index fingers and thumbs), then pull hands apart
- **🔍 Zoom Out**: From the "kite" shape, bring hands together

---

## 🚀 Demo

Perfect for:
- 📊 **Presentations** - Navigate PowerPoint/Google Slides without touching keyboard
- 📄 **Document Reading** - Scroll through PDFs and web pages hands-free
- 🎮 **Interactive Displays** - Control kiosks and exhibitions touchlessly
- ♿ **Accessibility** - Alternative input method for users with mobility constraints

---

## 📋 Prerequisites

- Python 3.8 or higher
- Webcam
- Windows/Mac/Linux OS

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/hand-gesture-control.git
cd hand-gesture-control
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv gesture_env
gesture_env\Scripts\activate

# Mac/Linux
python3 -m venv gesture_env
source gesture_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install opencv-python==4.8.1.78 mediapipe==0.10.21 numpy==1.26.4 pyautogui
```

**Important Note on Dependencies:**
- Use `opencv-python==4.8.1.78` and `numpy==1.26.4` for compatibility with MediaPipe
- Newer versions may cause dependency conflicts

---

## 🎮 Usage

### Basic Usage
```bash
python project.py
```

### Controls Summary

| Gesture | Action | Description |
|---------|--------|-------------|
| 👆 Index finger only | **Cursor Control** | Point to move mouse cursor |
| ✋ Hand moves left | **Next Slide** | Advance presentation forward |
| ✋ Hand moves right | **Previous Slide** | Go back in presentation |
| ✋ Hand moves down | **Scroll Down** | Smooth downward scrolling (555 units) |
| ✋ Hand moves up | **Scroll Up** | Smooth upward scrolling (555 units) |
| ✋ Hand stops | **Pause** | Trigger pause action |
| 🖐️🖐️ Two hands apart | **Zoom In** | Increase zoom level |
| 🖐️🖐️ Two hands together | **Zoom Out** | Decrease zoom level |

### Quit Application
Press **'q'** while the webcam window is in focus

---

## 📖 Detailed Gesture Guide

### Cursor Control (Index Finger Only)
1. Extend only your index finger
2. Keep all other fingers closed
3. Point in the direction you want the cursor to move
4. The cursor will follow your fingertip position

**Visual Feedback:** Green circle on fingertip

---

### Slide Navigation (Full Hand Movement)
1. Show your full hand (multiple fingers extended)
2. Move hand clearly left or right
3. Wait for cooldown (1 second) between slides

**Tips:**
- Make deliberate, clear movements
- The system tracks the hand's center point
- Orange trail shows movement path

---

### Scrolling (Full Hand Movement)
1. Show your full hand
2. Move hand up for scrolling up, down for scrolling down
3. Scrolling is smooth with 15 incremental steps

**Settings:**
- Scroll amount: 555 units per gesture
- Cooldown: 0.4 seconds between scrolls

---

### Zoom (Two Hands)
1. Bring both hands into camera view
2. Touch your index fingers and thumbs on each hand (forms a diamond/kite shape)
3. **To Zoom In:** Pull hands apart (increase distance by 80+ pixels)
4. **To Zoom Out:** Push hands together (decrease distance by 80+ pixels)

**Visual Feedback:**
- Yellow lines connect fingers on each hand
- Pink lines connect the two hands
- Distance counter shows pixel separation
- Progress indicator: "Pull more! 45/80px"

**Tips:**
- Start with hands close together
- Make exaggerated movements for easier detection
- Watch the distance counter for real-time feedback

---

### Pause Function
1. Hold your hand completely still
2. System detects lack of movement after 0.5 seconds
3. Automatically triggers pause action (press 'p')
4. Move hand to resume normal operation

---

## ⚙️ Configuration

You can customize the behavior by modifying these variables in `project.py`:

```python
# Movement Detection
MOVEMENT_THRESHOLD = 0.15      # Sensitivity for slides/scroll (lower = more sensitive)
MOVEMENT_DEQUE_LEN = 12        # Frames to track for movement detection

# Cooldowns (seconds)
ZOOM_COOLDOWN = 0.8           # Time between zoom actions
SLIDE_COOLDOWN = 1.0          # Time between slide changes
SCROLL_COOLDOWN = 0.4         # Time between scroll actions

# Zoom Settings
ZOOM_DISTANCE_CHANGE = 80     # Pixel change needed for zoom (lower = easier)

# Scrolling
# In the scroll section, modify the range and scroll amount:
for _ in range(15):           # Number of incremental scrolls
    pyautogui.scroll(37)      # Amount per increment
```

---

## 🔧 Troubleshooting

### Hand Not Detected
**Problem:** "No hand detected" message persists

**Solutions:**
- Ensure adequate lighting
- Position hand 1-2 feet from camera
- Check webcam permissions
- Make sure webcam is not in use by another application

---

### Gestures Not Triggering
**Problem:** Hand is detected but gestures don't activate

**Solutions:**
- Make larger, more deliberate movements
- Check cooldown timers (wait between gestures)
- Ensure only the intended fingers are extended
- Lower `MOVEMENT_THRESHOLD` in settings for increased sensitivity

---

### Zoom Not Working
**Problem:** Two hands detected but zoom doesn't trigger

**Solutions:**
- Check console output for debug messages
- Make larger hand movements (80+ pixels)
- Ensure both hands are clearly visible
- Watch the progress indicator: "Pull more! XX/80px"
- Try starting with hands closer together

---

### Fast Movements Not Tracked
**Problem:** Hand disappears when moving quickly

**Solutions:**
- System uses `model_complexity=0` for faster tracking
- Lower detection confidence already set to 0.5
- Try moving slightly slower for better tracking
- Ensure good lighting for better detection

---

### Scrolling Too Fast/Slow
**Problem:** Scroll speed doesn't match preference

**Solutions:**
- Modify the scroll loop in code:
  ```python
  for _ in range(15):  # Change this number
      pyautogui.scroll(37)  # Or change this value
  ```
- Increase both for faster, decrease for slower
- Current setting: ~555 units per gesture

---

## 🏗️ Technical Architecture

### Core Technologies
- **OpenCV**: Webcam capture and image processing
- **MediaPipe**: Hand landmark detection (21 points per hand)
- **PyAutoGUI**: System keyboard/mouse control
- **NumPy**: Numerical computations and array operations

### Detection Pipeline
1. **Frame Capture**: Webcam feed at real-time FPS
2. **Hand Detection**: MediaPipe identifies hands in frame
3. **Landmark Extraction**: 21 key points tracked per hand
4. **Gesture Recognition**: Algorithm analyzes finger positions and hand movement
5. **Action Execution**: PyAutoGUI simulates keyboard/mouse inputs
6. **Visual Feedback**: Annotated frame displayed to user

### Key Algorithms
- **Finger Detection**: Compares y-coordinates of fingertips vs. knuckles
- **Movement Tracking**: Uses deque to store recent hand positions
- **Gesture Differentiation**: State machine prevents interference between gestures
- **Cooldown System**: Time-based locks prevent accidental repeated triggers

---

## 📊 Performance Metrics

- **Detection Latency**: ~30-50ms per frame
- **FPS**: 20-30 FPS (depends on hardware)
- **Hand Tracking Range**: 1-6 feet from camera
- **Gesture Recognition Accuracy**: 90%+ in good lighting
- **Supported Hands**: 1-2 simultaneous hands

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Ideas for Contribution
- Add new gesture controls
- Improve detection accuracy
- Create gesture customization GUI
- Add support for more operating systems
- Implement gesture recording/playback
- Add voice command integration

---

## 🐛 Known Issues

1. **Lighting Dependency**: Performance degrades in low light
2. **Background Interference**: Cluttered backgrounds may affect detection
3. **Multi-hand Occlusion**: Overlapping hands can cause tracking loss
4. **Platform Differences**: Some keyboard shortcuts may vary by OS

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial release
- Single hand gesture controls
- Two-hand zoom functionality
- Cursor control with index finger
- Smooth scrolling (555 units)
- Real-time visual feedback
- Debug console output for zoom
  
---

## 👏 Acknowledgments

- **MediaPipe** by Google for hand tracking technology
- **OpenCV** community for computer vision tools
- **PyAutoGUI** for cross-platform GUI automation
- Inspired by touchless control systems and accessibility technology

---

## 📞 Contact

**Project Maintainer:** Raunak Dey

- GitHub: [@raunakdey41](https://github.com/raunakdey41)
- Email: raunakdey41@gmail.com
- LinkedIn: [Raunak Dey](https://www.linkedin.com/in/raunak-dey-bb2403319/)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

---

## 📸 Screenshots

### Cursor Control Mode
![Cursor Control](screenshots/cursor-control.png)
*Index finger pointing controls the mouse cursor*

### Slide Navigation
![Slide Navigation](screenshots/slide-navigation.png)
*Hand movement for presentation control*

### Two-Hand Zoom
![Zoom Gesture](screenshots/zoom-gesture.png)
*Diamond/kite shape with both hands for zoom control*

### Visual Feedback
![Visual Feedback](screenshots/visual-feedback.png)
*Real-time gesture detection and tracking indicators*

---

## 🎓 Educational Use

This project is excellent for:
- Computer Vision coursework
- Human-Computer Interaction studies
- Machine Learning demonstrations
- Accessibility technology research
- Python programming education

---

**Made with ❤️ and 🖐️ for touchless interaction**
