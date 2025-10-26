import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time

# === Settings ===
MOVEMENT_DEQUE_LEN = 12
MOVEMENT_THRESHOLD = 0.15     # Hand movement threshold
ZOOM_COOLDOWN = 0.8           # Cooldown for zoom actions
SLIDE_COOLDOWN = 1.0          # Cooldown for slide changes
SCROLL_COOLDOWN = 0.4         # Cooldown for scrolling
ZOOM_DISTANCE_CHANGE = 80     # Pixel change needed for zoom (increased for easier detection)
SHOW_FEEDBACK = True

pyautogui.FAILSAFE = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,  # Lowered for better fast tracking
    min_tracking_confidence=0.5,   # Lowered for better fast tracking
    model_complexity=0             # Faster model for quick movements
)

mp_drawing = mp.solutions.drawing_utils

def landmarks_to_np(landmarks, w, h):
    return np.array([[int(lm.x * w), int(lm.y * h)] for lm in landmarks])

def hand_centroid(landmarks):
    pts = np.array(landmarks)
    return np.mean(pts, axis=0).astype(int)

def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def count_fingers_up(lm):
    """Count how many fingers are extended"""
    fingers_up = 0
    
    # Thumb (check x-axis)
    if lm[4][0] > lm[3][0]:
        fingers_up += 1
    
    # Other fingers (check y-axis)
    finger_tips = [8, 12, 16, 20]  # index, middle, ring, pinky
    finger_pips = [6, 10, 14, 18]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if lm[tip][1] < lm[pip][1]:
            fingers_up += 1
    
    return fingers_up

# State tracking
hand_position_deque = deque(maxlen=MOVEMENT_DEQUE_LEN)
last_action_times = {
    'slide': 0,
    'scroll': 0,
    'zoom': 0,
    'pause': 0
}

zoom_baseline_distance = None
is_paused = False

# Screen size
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if not ret:
    print("Cannot open webcam")
    exit(1)

frame_h, frame_w = frame.shape[:2]

print("=== Enhanced Full Hand Gesture Control ===")
print("\nSingle Hand Controls:")
print("  • Hand moves LEFT → Next slide")
print("  • Hand moves RIGHT → Previous slide")
print("  • Hand moves DOWN → Scroll down")
print("  • Hand moves UP → Scroll up")
print("  • Hand stops → Pause")
print("\nTwo Hand Controls (Zoom):")
print("  • Touch index+thumb on both hands (kite shape)")
print("  • Pull hands APART → Zoom IN")
print("  • Bring hands TOGETHER → Zoom OUT")
print("\nPress 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = hands.process(rgb)

    gesture_text = "Waiting for hand..."
    current_time = time.time()
    num_hands = len(res.multi_hand_landmarks) if res.multi_hand_landmarks else 0

    if res.multi_hand_landmarks:
        
        # TWO HAND GESTURE: Zoom
        if num_hands == 2:
            hand1_lms = res.multi_hand_landmarks[0]
            hand2_lms = res.multi_hand_landmarks[1]
            
            lm1 = landmarks_to_np(hand1_lms.landmark, frame_w, frame_h)
            lm2 = landmarks_to_np(hand2_lms.landmark, frame_w, frame_h)
            
            # Draw both hands
            if SHOW_FEEDBACK:
                mp_drawing.draw_landmarks(frame, hand1_lms, mp_hands.HAND_CONNECTIONS)
                mp_drawing.draw_landmarks(frame, hand2_lms, mp_hands.HAND_CONNECTIONS)
            
            # Get index finger tips and thumb tips from both hands
            hand1_index = lm1[8]
            hand1_thumb = lm1[4]
            hand2_index = lm2[8]
            hand2_thumb = lm2[4]
            
            # Calculate distance between the two hands (using index fingers as reference)
            hands_distance = calculate_distance(hand1_index, hand2_index)
            
            # Draw "kite" shape - lines connecting the fingers
            cv2.line(frame, tuple(hand1_index), tuple(hand1_thumb), (0, 255, 255), 3)
            cv2.line(frame, tuple(hand2_index), tuple(hand2_thumb), (0, 255, 255), 3)
            cv2.line(frame, tuple(hand1_index), tuple(hand2_index), (255, 0, 255), 2)
            cv2.line(frame, tuple(hand1_thumb), tuple(hand2_thumb), (255, 0, 255), 2)
            
            # Draw circles on key points
            cv2.circle(frame, tuple(hand1_index), 8, (0, 255, 0), -1)
            cv2.circle(frame, tuple(hand1_thumb), 8, (0, 255, 0), -1)
            cv2.circle(frame, tuple(hand2_index), 8, (0, 255, 0), -1)
            cv2.circle(frame, tuple(hand2_thumb), 8, (0, 255, 0), -1)
            
            # Calculate center point between the two hands
            center_x = (hand1_index[0] + hand2_index[0]) // 2
            center_y = (hand1_index[1] + hand2_index[1]) // 2
            cv2.circle(frame, (center_x, center_y), 12, (255, 255, 0), -1)
            
            # Display distance
            cv2.putText(frame, f"{int(hands_distance)}px", 
                       (center_x + 15, center_y - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Initialize baseline (with lower requirement)
            if zoom_baseline_distance is None:
                zoom_baseline_distance = hands_distance
                gesture_text = "🖐️🖐️ ZOOM READY - Move hands now!"
                print(f"[DEBUG] Zoom baseline set: {int(hands_distance)}px")
            else:
                distance_change = hands_distance - zoom_baseline_distance
                
                # ZOOM IN: Hands moving apart (lowered threshold)
                if distance_change > ZOOM_DISTANCE_CHANGE and (current_time - last_action_times['zoom']) > ZOOM_COOLDOWN:
                    gesture_text = "🔍++ ZOOM IN (Hands Apart)"
                    pyautogui.hotkey('ctrl', '=')
                    print(f"[ZOOM IN] Distance change: {int(distance_change)}px")
                    last_action_times['zoom'] = current_time
                    zoom_baseline_distance = hands_distance
                
                # ZOOM OUT: Hands coming together (lowered threshold)
                elif distance_change < -ZOOM_DISTANCE_CHANGE and (current_time - last_action_times['zoom']) > ZOOM_COOLDOWN:
                    gesture_text = "🔍-- ZOOM OUT (Hands Together)"
                    pyautogui.hotkey('ctrl', '-')
                    print(f"[ZOOM OUT] Distance change: {int(distance_change)}px")
                    last_action_times['zoom'] = current_time
                    zoom_baseline_distance = hands_distance
                else:
                    # Show current delta to help debug
                    if distance_change > 0:
                        gesture_text = f"🖐️🖐️ Pull more! {int(distance_change)}/{ZOOM_DISTANCE_CHANGE}px"
                    else:
                        gesture_text = f"🖐️🖐️ Push more! {int(abs(distance_change))}/{ZOOM_DISTANCE_CHANGE}px"
            
            # Clear single hand tracking when using two hands
            hand_position_deque.clear()

        # SINGLE HAND GESTURE: Movement for slides/scroll
        elif num_hands == 1:
            hand_lms = res.multi_hand_landmarks[0]
            lm = landmarks_to_np(hand_lms.landmark, frame_w, frame_h)
            
            if SHOW_FEEDBACK:
                mp_drawing.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

            # Calculate hand center
            centroid = hand_centroid(lm)
            nx = centroid[0] / frame_w
            ny = centroid[1] / frame_h
            
            hand_position_deque.append((nx, ny, current_time))
            
            # Draw centroid
            cv2.circle(frame, tuple(centroid), 15, (0, 255, 0), -1)
            cv2.circle(frame, tuple(centroid), 20, (255, 255, 255), 2)
            
            # Reset zoom when only one hand
            zoom_baseline_distance = None
            
            # MOVEMENT DETECTION
            if len(hand_position_deque) >= MOVEMENT_DEQUE_LEN:
                xs = [p[0] for p in hand_position_deque]
                ys = [p[1] for p in hand_position_deque]
                times = [p[2] for p in hand_position_deque]
                
                dx = xs[-1] - xs[0]
                dy = ys[-1] - ys[0]
                time_delta = times[-1] - times[0]
                
                movement_magnitude = np.sqrt(dx**2 + dy**2)
                
                # PAUSE DETECTION: Hand stopped
                if movement_magnitude < 0.03 and time_delta > 0.5:
                    if (current_time - last_action_times['pause']) > 2.0:
                        if not is_paused:
                            gesture_text = "⏸️ PAUSED"
                            pyautogui.press('p')
                            last_action_times['pause'] = current_time
                            is_paused = True
                        else:
                            gesture_text = "⏸️ Paused"
                else:
                    is_paused = False
                    
                    # Horizontal or Vertical movement
                    if abs(dx) > abs(dy):
                        # HORIZONTAL (Slides)
                        if dx < -MOVEMENT_THRESHOLD and (current_time - last_action_times['slide']) > SLIDE_COOLDOWN:
                            gesture_text = "◀️ NEXT SLIDE"
                            pyautogui.press('left')
                            last_action_times['slide'] = current_time
                            hand_position_deque.clear()
                        
                        elif dx > MOVEMENT_THRESHOLD and (current_time - last_action_times['slide']) > SLIDE_COOLDOWN:
                            gesture_text = "▶️ PREVIOUS SLIDE"
                            pyautogui.press('right')
                            last_action_times['slide'] = current_time
                            hand_position_deque.clear()
                        else:
                            gesture_text = "✋ Hand ready"
                    
                    else:
                        # VERTICAL (Scrolling) - Smooth continuous scrolling
                        if dy > MOVEMENT_THRESHOLD and (current_time - last_action_times['scroll']) > SCROLL_COOLDOWN:
                            gesture_text = "🔽 SCROLL DOWN"
                            # Smooth scrolling with multiple small increments
                            for _ in range(15):  # 15 scrolls of 37 = ~555 total
                                pyautogui.scroll(-50)
                                time.sleep(0.01)  # Small delay for smoothness
                            last_action_times['scroll'] = current_time
                            hand_position_deque.clear()
                        
                        elif dy < -MOVEMENT_THRESHOLD and (current_time - last_action_times['scroll']) > SCROLL_COOLDOWN:
                            gesture_text = "🔼 SCROLL UP"
                            # Smooth scrolling with multiple small increments
                            for _ in range(15):  # 15 scrolls of 37 = ~555 total
                                pyautogui.scroll(50)
                                time.sleep(0.01)  # Small delay for smoothness
                            last_action_times['scroll'] = current_time
                            hand_position_deque.clear()
                        else:
                            gesture_text = "✋ Hand ready"
            else:
                gesture_text = "✋ Tracking hand..."
            
            # Draw movement trail
            if len(hand_position_deque) > 1 and SHOW_FEEDBACK:
                for i in range(1, len(hand_position_deque)):
                    pt1 = (int(hand_position_deque[i-1][0] * frame_w), 
                           int(hand_position_deque[i-1][1] * frame_h))
                    pt2 = (int(hand_position_deque[i][0] * frame_w), 
                           int(hand_position_deque[i][1] * frame_h))
                    cv2.line(frame, pt1, pt2, (0, 165, 255), 2)

    else:
        # No hands detected
        hand_position_deque.clear()
        zoom_baseline_distance = None
        is_paused = False
        gesture_text = "❌ No hand detected"

    # Display info with background
    text_size = cv2.getTextSize(gesture_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    cv2.rectangle(frame, (5, 5), (text_size[0] + 15, 50), (0, 0, 0), -1)
    cv2.putText(frame, gesture_text, (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    
    # Hand count indicator
    hand_indicator = f"Hands: {num_hands}"
    cv2.putText(frame, hand_indicator, (10, frame_h - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.putText(frame, "Press 'q' to quit", (10, frame_h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Hand Gesture Control", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n=== Gesture Control Stopped ===")