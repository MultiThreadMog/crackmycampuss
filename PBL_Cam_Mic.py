from ultralytics import YOLO
import cv2
import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import threading
import time

# ======== Load YOLO model ========

model = YOLO("best.pt")

# ======== Siren detection setup ========

SAMPLE_RATE = 44100
DURATION = 0.2 
SIREN_LOW = 600
SIREN_HIGH = 2000
THRESHOLD = 0.0005
siren_detected = False

detected_emergency_vehicle = False
detection_triggered = False

def state() -> bool:
    global detected_emergency_vehicle, siren_detected, detection_triggered
    
    current_detection = detected_emergency_vehicle or siren_detected

    if current_detection and not detection_triggered:
        detection_triggered = True
        return True
    elif not current_detection:
        detection_triggered = False
    
    return False


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def detect_siren():
    global siren_detected
    try:
        audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float64')
        sd.wait()
        filtered = bandpass_filter(audio[:, 0], SIREN_LOW, SIREN_HIGH, SAMPLE_RATE)
        energy = np.mean(filtered ** 2)
        siren_detected = energy > THRESHOLD
    except Exception as e:
        print("Audio error:", e)
        siren_detected = False

def siren_listener():
    while True:
        detect_siren()
        time.sleep(0.1)

threading.Thread(target=siren_listener, daemon=True).start()

# ======== Webcam stream setup ========

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print(" Press 'q' to quit webcam window.")

# ======== Main loop ========

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(source=frame, device="mps", conf=0.6, imgsz=640, verbose=False)
    annotated_frame = results[0].plot()

    class_names = results[0].names
    boxes = results[0].boxes
    detected_labels = [class_names[int(cls)] for cls in boxes.cls]

    emergency_keywords = ["ambulance", "firetruck", "police", "emergency"] 
    detected_emergency_vehicle = any(
        any(keyword in label.lower() for keyword in emergency_keywords)
        for label in detected_labels
    )
    
    if detected_emergency_vehicle and siren_detected:
        cv2.putText(annotated_frame, "Emergency Vehicle Detected!", (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
        print("Emergency Vehicle Detected!")
    elif detected_emergency_vehicle:
        cv2.putText(annotated_frame, "Vehicle Detected (No Siren)", (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
    elif siren_detected:
        cv2.putText(annotated_frame, "Siren Detected (No Vehicle)", (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
    else:
        cv2.putText(annotated_frame, "No Siren / No Vehicle", (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("YOLO + Siren Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()