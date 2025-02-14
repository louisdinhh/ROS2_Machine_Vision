import cv2
from ultralytics import YOLO

# ---- Load trained model and activate camera ----
model = YOLO("runs/detect/train/weights/best.pt")
cap = cv2.VideoCapture(0)

# ---- Error if camera is not open ----
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

while cap.isOpened():
    
    # ---- Capture frame-by-frame ----
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # ---- Run YOLO model on the frame ----
    results = model(frame)
    
    # ---- Extract the result image with predictions && draw bounding box ----

    # ---- <Bounding box customisation> ----

    # ---- <Red> ----
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = model.names[cls]
            if label == 'red':
                color = (85, 85, 255)
                thickness = 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                text = f"{label} {conf:.1f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x, text_y = x1, y1 - 10 
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), 
                              (text_x + text_size[0], text_y + 5), color, -1)
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, 
                            (255, 255, 255), font_thickness, cv2.LINE_AA)
    # ---- <Green> ----
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = model.names[cls]
            if label == 'green':
                color = (132, 202, 33)
                thickness = 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                text = f"{label} {conf:.1f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x, text_y = x1, y1 - 10 
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), 
                              (text_x + text_size[0], text_y + 5), color, -1)
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, 
                            (255, 255, 255), font_thickness, cv2.LINE_AA)
    # ---- <Blue> ----
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = box.conf[0].item()
            cls = int(box.cls[0].item())
            label = model.names[cls]
            if label == 'blue':
                color = (82, 46, 33)
                thickness = 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                text = f"{label} {conf:.1f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                font_thickness = 1
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                text_x, text_y = x1, y1 - 10 
                cv2.rectangle(frame, (text_x, text_y - text_size[1] - 5), 
                              (text_x + text_size[0], text_y + 5), color, -1)
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, 
                            (255, 255, 255), font_thickness, cv2.LINE_AA)

    # ---- <End here> ----


    # ---- Display the frame with predictions ----
    #cv2.imshow("Cube color detector", annotated_frame)
    cv2.imshow("Cube color detector", frame)
    # ---- Exit on pressing 'q' ----
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---- Release the camera and close all OpenCV windows ----
cap.release()
cv2.destroyAllWindows()
