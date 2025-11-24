#in cmd
#pip install pyttsx3



import pyttsx3
print("pyttsx3 imported successfully!")
engine = pyttsx3.init()
engine.say("Test voice")
engine.runAndWait()
exit()