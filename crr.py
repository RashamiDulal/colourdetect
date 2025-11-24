import cv2
import pyttsx3
import time

# Initialize speech engine
engine = pyttsx3.init()

def speak(text):
    # Non-blocking using a thread-like approach
    engine.say(text)
    engine.runAndWait()

cap = cv2.VideoCapture(0)

# Smaller display
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

last_color = ""
last_speak_time = 0
repeat_delay = 1.0  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2
    hue = hsv[cy, cx][0]

    # Detect traffic light colors ONLY
    if hue < 10 or hue > 170:
        color = "RED"
    elif 18 <= hue < 35:
        color = "YELLOW"
    elif 35 <= hue < 85:
        color = "GREEN"
    else:
        color = "NONE"

    # Display detected color in BLACK
    cv2.putText(frame, color, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
    cv2.circle(frame, (cx, cy), 6, (0, 0, 0), 2)

    current_time = time.time()

    # Speak only if color is detected
    if color != "NONE":
        # Speak immediately when color changes
        if color != last_color:
            speak(color)
            last_color = color
            last_speak_time = current_time
        # Repeat voice every 1 second while same color remains
        elif current_time - last_speak_time >= repeat_delay:
            speak(color)
            last_speak_time = current_time

    cv2.imshow("Traffic Light Detector", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
