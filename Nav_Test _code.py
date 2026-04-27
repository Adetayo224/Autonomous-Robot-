import cv2
import os

# Essential for the new "Wayland" desktop on Pi 4/5
os.environ["QT_QPA_PLATFORM"] = "xcb"

# Minimal pipeline for the OV5647 sensor
pipeline = "libcamerasrc ! video/x-raw, width=640, height=480 ! videoconvert ! appsink"


cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("? GUI is here, but Camera is busy or not found.")
else:
    print("? GUI and Camera are working! Press 'q' to close.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # This is the GUI test
        cv2.imshow("Robot Navigation View", frame)
        
        # HighGUI needs waitKey to actually render the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()