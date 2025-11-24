                                               #working


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

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Voice control
last_color = ""
last_speak_time = 0
speak_delay = 3  # 3 seconds

print("🚦 TRAFFIC LIGHT DETECTOR - WINDOWS VOICE")
print("🔊 Testing Windows voice...")
speak("Starting traffic light detector")
print("✅ Windows voice working!")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read camera")
        break
    
    # Flip frame
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # Convert to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Analyze center region (20x20 pixels)
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
    
    # Draw UI
    cv2.putText(frame, f"Color: {current_color}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
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
    
    # SIMPLE VOICE LOGIC
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
        
        # SPEAK
        if should_speak:
            speak(current_color)
            last_color = current_color
            last_speak_time = current_time
            print(f"✅ VOICE SUCCESS: {current_color}")
            print("-" * 50)
    
    # Show frame
    cv2.imshow('Traffic Light - WINDOWS VOICE', frame)
    
    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
speak("Program ended")
print("🎯 Program finished")