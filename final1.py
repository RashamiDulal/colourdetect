import cv2

cap = cv2.VideoCapture(0)

# Make window smaller
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    height, width, _ = frame.shape
    cx = width // 2
    cy = height // 2

    pixel_hsv = hsv_frame[cy, cx]
    hue = pixel_hsv[0]

    # Traffic light colors ONLY
    if hue < 10 or hue > 170:
        color = "RED"
    elif 18 <= hue < 35:
        color = "YELLOW"
    elif 35 <= hue < 85:
        color = "GREEN"
    else:
        color = "NONE"

    # Display detected color name in BLACK
    cv2.putText(frame, color, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 0), 3)    # <-- Black text

    # Mark center point
    cv2.circle(frame, (cx, cy), 6, (0, 0, 0), 2)  # Black circle

    cv2.imshow("Traffic Light Detector (Small Window)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
