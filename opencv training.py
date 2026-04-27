import cv2
import os

# --- System Fix for Wayland Desktop ---
os.environ["QT_QPA_PLATFORM"] = "xcb"

# --- Project Paths ---
BASE_PATH = "/home/samfred/Documents/Nav Project/"
PROTO = os.path.join(BASE_PATH, "deploy.prototxt")
MODEL = os.path.join(BASE_PATH, "mobilenet_iter_73000.caffemodel")

# --- AI Model Setup ---
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

print("⏳ Loading AI Brain...")
net = cv2.dnn.readNetFromCaffe(PROTO, MODEL)
print("✅ AI Model Loaded!")

# --- THE HARD-LINKED PIPELINE ---
# Using the exact hardware path from your 'rpicam-hello' output
CAM_PATH = "/base/soc/i2c0mux/i2c@1/ov5647@36"

pipeline = (
    f"libcamerasrc camera-name={CAM_PATH} ! "
    "video/x-raw, width=640, height=480, framerate=30/1 ! "
    "videoconvert ! "
    "appsink drop=true"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("❌ Error: Still Busy. One final attempt using index 0...")
    # Last ditch effort using the simplified source
    cap = cv2.VideoCapture("libcamerasrc ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("🛑 FATAL: Camera is locked by the OS. Try 'sudo reboot' if this persists.")
    exit()

print("🚀 Vision Live! Show the camera a bottle or a chair.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        (h, w) = frame.shape[:2]
        
        # AI Detection
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                idx = int(detections[0, 0, i, 1])
                label = CLASSES[idx] if idx < len(CLASSES) else "Object"
                
                # Draw the detection
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (startX, startY, endX, endY) = box.astype("int")
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, f"{label.upper()}", (startX, startY-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                print(f"🎯 I see a {label.upper()}")

        cv2.imshow("Samfred AI Vision", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    print("🧹 Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()