import cv2
import pyttsx3
import time
import numpy as np
import threading

class TrafficLightDetector:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.8)
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("Could not open camera")
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        
        # Voice control variables
        self.last_spoken_color = ""
        self.last_speak_time = 0
        self.repeat_delay = 3  # Repeat every 3 seconds
        self.current_display_color = "NONE"
        self.speaking = False
        self.voice_queue = []
        
    def speak_color_threaded(self, color):
        """Speak in a separate thread to avoid blocking"""
        if self.speaking:
            return
            
        self.speaking = True
        try:
            self.engine.say(color)
            self.engine.runAndWait()
            self.last_spoken_color = color
            self.last_speak_time = time.time()
            print(f"🎤 SPOKE: '{color}' at {time.strftime('%H:%M:%S')}")  # Debug
        except Exception as e:
            print(f"TTS Error: {e}")
        finally:
            self.speaking = False
    
    def detect_color(self, frame):
        """Simple color detection based on hue"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, w, _ = frame.shape
        cx, cy = w // 2, h // 2

        # Use 10x10 region for stable detection
        region_size = 10
        region = hsv[cy-region_size:cy+region_size, cx-region_size:cx+region_size]
        
        if region.size == 0:
            return "NONE"

        hue = int(np.mean(region[:,:,0]))
        saturation = np.mean(region[:,:,1])
        value = np.mean(region[:,:,2])
        
        # Only detect colors if saturation and value are sufficient
        if saturation < 50 or value < 50:
            return "NONE"
            
        # Simple hue-based color detection
        if hue < 10 or hue > 170:
            return "RED"
        elif 20 <= hue < 35:
            return "YELLOW"
        elif 35 <= hue < 85:
            return "GREEN"
        else:
            return "NONE"
    
    def should_speak(self, current_color):
        """Determine if we should speak now"""
        if current_color == "NONE":
            return False
            
        current_time = time.time()
        time_since_last_speak = current_time - self.last_speak_time
        
        # Always speak when color changes
        if current_color != self.last_spoken_color:
            print(f"🔄 Color changed from '{self.last_spoken_color}' to '{current_color}'")
            return True
            
        # Speak if same color and repeat delay has passed
        if time_since_last_speak >= self.repeat_delay:
            print(f"⏰ Repeat time reached for '{current_color}' ({time_since_last_speak:.1f}s)")
            return True
            
        return False
    
    def draw_interface(self, frame, color, center_x, center_y):
        """Draw visualization"""
        text_color = (255, 255, 255)  # White text
        bg_color = (0, 0, 0)  # Black background
        
        # Create background for text
        text_size = cv2.getTextSize(color, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        cv2.rectangle(frame, (5, 5), (text_size[0] + 15, text_size[1] + 20), bg_color, -1)
        
        # Display detected color
        cv2.putText(frame, color, (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
        
        # Draw center crosshair
        crosshair_size = 15
        cv2.line(frame, (center_x - crosshair_size, center_y), 
                (center_x + crosshair_size, center_y), (255, 255, 255), 2)
        cv2.line(frame, (center_x, center_y - crosshair_size), 
                (center_x, center_y + crosshair_size), (255, 255, 255), 2)
        
        # Display timing information
        time_since_last = time.time() - self.last_speak_time
        time_until_next = max(0, self.repeat_delay - time_since_last)
        
        status_text = f"Next speak: {time_until_next:.1f}s"
        cv2.putText(frame, status_text, (10, frame.shape[0] - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        last_spoken_text = f"Last: {self.last_spoken_color}"
        cv2.putText(frame, last_spoken_text, (10, frame.shape[0] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        current_time_text = f"Time: {time.strftime('%H:%M:%S')}"
        cv2.putText(frame, current_time_text, (10, frame.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        
        # Visual countdown bar
        bar_width = 200
        bar_height = 10
        bar_x = frame.shape[1] - bar_width - 10
        bar_y = frame.shape[0] - 20
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
        
        # Progress bar
        progress = min(1.0, time_since_last / self.repeat_delay)
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
    
    def run(self):
        """Main detection loop"""
        print("🚦 Starting Traffic Light Detection...")
        print("🎯 Point camera at colored objects")
        print("🔊 Voice should repeat every 5 seconds for the same color!")
        print("Press ESC to exit")
        
        # Initial timing
        self.last_speak_time = time.time() - self.repeat_delay  # Force immediate first speak
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                cx, cy = w // 2, h // 2

                # Detect color
                self.current_display_color = self.detect_color(frame)

                # VOICE LOGIC - Check if we should speak
                if self.should_speak(self.current_display_color) and not self.speaking:
                    print(f"🗣️  Requesting speech: '{self.current_display_color}'")
                    # Start speech in a separate thread
                    speech_thread = threading.Thread(
                        target=self.speak_color_threaded, 
                        args=(self.current_display_color,)
                    )
                    speech_thread.daemon = True
                    speech_thread.start()

                # Draw interface
                self.draw_interface(frame, self.current_display_color, cx, cy)
                cv2.imshow("Traffic Light Detector - FIXED REPEAT", frame)

                if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                    break
                    
        except KeyboardInterrupt:
            print("\nExiting...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        cv2.destroyAllWindows()
        print("Cleanup completed")

def main():
    try:
        detector = TrafficLightDetector()
        detector.run()
    except Exception as e:
        print(f"Application error: {e}")

if __name__ == "__main__":
    main()