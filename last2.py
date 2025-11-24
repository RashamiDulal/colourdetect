#for usbcam final working code


import cv2
import time
import numpy as np
import win32com.client

# Initialize Windows voice
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    """Windows voice function"""
    print(f"🔊 SPEAKING: {text}")
    speaker.Speak(text)

def find_external_camera():
    """Find external webcam by trying different indexes"""
    # Try indexes 0 to 4
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Found camera at index {i}")
                cap.release()
                return i
        cap.release()
    print("❌ No camera found")
    return -1

# Find external camera
print("📷 Looking for external webcam...")
camera_index = find_external_camera()

if camera_index == -1:
    print("❌ No camera detected. Please check connection.")
    exit()

# Camera setup with external webcam
cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Test camera
ret, frame = cap.read()
if not ret:
    print("❌ Cannot read from external webcam")
    exit()

print(f"✅ External webcam ready at index {camera_index}")

# Voice control
last_color = ""
last_speak_time = 0
speak_delay = 3  # 3 seconds

#speak("External webcam connected. Traffic light detector started")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read from external webcam")
        break
    
    # Flip frame (optional - depends on your webcam)
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Analyze center region
    region_size = 10
    center_region = hsv[center_y-region_size:center_y+region_size, 
                       center_x-region_size:center_x+region_size]
    
    if center_region.size == 0:
        continue
    
    # Calculate average color
    avg_hue = np.mean(center_region[:,:,0])
    avg_sat = np.mean(center_region[:,:,1])
    avg_val = np.mean(center_region[:,:,2])
    
    # Detect color
    current_color = "NONE"
    if avg_sat > 50 and avg_val > 50:
        if avg_hue < 10 or avg_hue > 170:
            current_color = "RED"
        elif 20 <= avg_hue < 35:
            current_color = "YELLOW" 
        elif 35 <= avg_hue < 85:
            current_color = "GREEN"
    
    # Draw UI with different colors for each light
    color_map = {
        "RED": (0, 0, 255),      # Blue, Green, Red - so (0,0,255) is Red
        "GREEN": (0, 255, 0),    # Green
        "YELLOW": (0, 255, 255), # Yellow
        "NONE": (255, 255, 255)  # White
    }
    
    text_color = color_map.get(current_color, (255, 255, 255))
    cv2.putText(frame, f"Color: {current_color}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
    cv2.putText(frame, f"Webcam: {camera_index}", (20, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # Draw crosshair
    cv2.rectangle(frame, (center_x-15, center_y-15), (center_x+15, center_y+15), 
                 (255, 255, 255), 2)
    cv2.line(frame, (center_x-20, center_y), (center_x+20, center_y), 
             (255, 255, 255), 1)
    cv2.line(frame, (center_x, center_y-20), (center_x, center_y+20), 
             (255, 255, 255), 1)
    
    # Show timing info
    current_time = time.time()
    time_since_speak = current_time - last_speak_time
    time_until_next = max(0, speak_delay - time_since_speak)
    
    cv2.putText(frame, f"Next: {time_until_next:.1f}s", (20, h-60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.putText(frame, f"Last: {last_color}", (20, h-30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # SIMPLE VOICE LOGIC WITH PROPER COMMANDS
    if current_color != "NONE":
        should_speak = False
        
        # Condition 1: Color changed
        if current_color != last_color:
            should_speak = True
            print(f"🔄 COLOR CHANGED: {last_color} -> {current_color}")
        
        # Condition 2: Time to repeat (3 seconds)
        elif current_time - last_speak_time >= speak_delay:
            should_speak = True
            print(f"⏰ TIME TO REPEAT: {current_color}")
        
        # SPEAK WITH PROPER COMMANDS
        if should_speak:
            if current_color == "RED":
                speak("Stop the car! Red light")
            elif current_color == "GREEN":
                speak("Go ahead! Green light")
            elif current_color == "YELLOW":
                speak("Slow down! Yellow light")
            
            last_color = current_color
            last_speak_time = current_time
            print(f"✅ VOICE SUCCESS: {current_color}")
            print("-" * 50)
    
    # Show frame
    cv2.imshow(f'External Webcam {camera_index} - Traffic Light', frame)
    
    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
#speak("Program ended")
print("🎯 Program finished")